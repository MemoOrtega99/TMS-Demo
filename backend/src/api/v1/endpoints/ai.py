"""
Endpoints for AI Chat via OpenRouter.
El AI lee datos reales de la base de datos para dar respuestas contextualizadas.
No se requiere pgvector — simplemente construimos un contexto estructurado
con queries SQL y se lo pasamos al modelo como system prompt.
"""
import httpx
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, text
from decimal import Decimal

from src.core.config import settings
from src.core.database import get_db
from src.api.v1.endpoints.auth import get_current_user
from src.models.user import User
from src.models.trips import Trip, TripStatus, TripExpense, DieselLoad
from src.models.invoices import Invoice, InvoiceStatus, InvoiceType
from src.models.fleet import Vehicle, VehicleStatus
from src.models.catalogs import Driver, Client
from src.models.inventory import InventoryItem

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    sources: list[str] = []

SYSTEM_PROMPT = """
Eres un asistente de inteligencia artificial para Soluciones-TMS, 
un sistema integral de gestión de transporte (TMS) para una empresa de transporte de carga en México.
Tienes acceso en tiempo real a los datos operativos de la empresa a través del contexto inyectado.

INSTRUCCIONES:
- Responde en español, de forma clara, ejecutiva y profesional.
- Usa los datos del contexto para responder con precisión; no inventes cifras.
- Usa formato markdown para mejorar la lectura (negritas, tablas, viñetas).
- Cuando das cifras monetarias, usa el formato $X,XXX MXN.
- Si el usuario pregunta algo que no puedes responder con los datos disponibles, dilo claramente.
- Actúa como un analista de operaciones de transporte senior.
"""

async def build_rich_context(db: AsyncSession) -> str:
    """
    Construye un contexto rico con datos reales del sistema TMS.
    Esto se inyecta al AI como parte del system prompt para que pueda
    responder preguntas sobre la operación sin necesidad de pgvector.
    """
    sections = []

    # --- VIAJES ---
    try:
        trips_by_status = await db.execute(
            select(Trip.estatus, func.count(Trip.id))
            .group_by(Trip.estatus)
        )
        trips_stats = {str(s): c for s, c in trips_by_status.all()}
        sections.append(f"VIAJES POR ESTATUS: {trips_stats}")

        # Viajes recientes con tarifa
        recent_trips = await db.execute(
            select(Trip.numero_viaje, Trip.origen, Trip.destino, Trip.tarifa_cliente, Trip.estatus, Trip.fecha_programada)
            .order_by(desc(Trip.fecha_programada))
            .limit(10)
        )
        trips_list = recent_trips.all()
        if trips_list:
            trip_lines = [
                f"  - {t.numero_viaje}: {t.origen} → {t.destino} | Tarifa: ${float(t.tarifa_cliente or 0):,.0f} | Estatus: {t.estatus}"
                for t in trips_list
            ]
            sections.append("ÚLTIMOS 10 VIAJES:\n" + "\n".join(trip_lines))

        # Facturación total de viajes completados
        billing_q = await db.execute(
            select(func.sum(Trip.tarifa_cliente))
            .where(Trip.estatus == TripStatus.completado)
        )
        total_billing = billing_q.scalar() or 0
        sections.append(f"FACTURACIÓN TOTAL (viajes completados): ${float(total_billing):,.2f} MXN")
    except Exception as e:
        sections.append(f"(Error cargando datos de viajes: {e})")

    # --- FINANZAS: CxC y CxP ---
    try:
        fin_q = await db.execute(
            select(Invoice.tipo, Invoice.estatus, func.sum(Invoice.total - Invoice.monto_pagado), func.count(Invoice.id))
            .where(Invoice.estatus.in_([InvoiceStatus.PENDIENTE, InvoiceStatus.VENCIDA, InvoiceStatus.PARCIAL]))
            .group_by(Invoice.tipo, Invoice.estatus)
        )
        fin_rows = fin_q.all()
        fin_lines = [f"  - {t.value}/{s.value}: {c} facturas, saldo ${float(m or 0):,.2f}" for t, s, m, c in fin_rows if m]
        if fin_lines:
            sections.append("ESTADO DE CUENTAS (pendientes):\n" + "\n".join(fin_lines))
    except Exception as e:
        sections.append(f"(Error cargando datos financieros: {e})")

    # --- FLOTA ---
    try:
        fleet_q = await db.execute(
            select(Vehicle.estatus, func.count(Vehicle.id)).group_by(Vehicle.estatus)
        )
        fleet_stats = {str(s): c for s, c in fleet_q.all()}
        sections.append(f"ESTATUS DE FLOTA: {fleet_stats}")

        total_vehicles = sum(fleet_stats.values())
        sections.append(f"TOTAL UNIDADES REGISTRADAS: {total_vehicles}")
    except Exception as e:
        sections.append(f"(Error cargando datos de flota: {e})")

    # --- DIESEL ---
    try:
        diesel_q = await db.execute(
            select(func.sum(DieselLoad.litros), func.sum(DieselLoad.costo_total), func.count(DieselLoad.id))
        )
        dl = diesel_q.one()
        if dl and dl[0]:
            sections.append(
                f"DIESEL — Total litros: {float(dl[0]):,.0f} L | Costo total: ${float(dl[1] or 0):,.2f} MXN | Cargas registradas: {dl[2]}"
            )
    except Exception as e:
        sections.append(f"(Error cargando datos de diesel: {e})")

    # --- INVENTARIO ---
    try:
        inv_low_q = await db.execute(
            select(InventoryItem.codigo, InventoryItem.nombre, InventoryItem.stock_actual, InventoryItem.stock_minimo)
            .where(InventoryItem.stock_actual < InventoryItem.stock_minimo)
        )
        low_items = inv_low_q.all()
        if low_items:
            lines = [f"  - {i.codigo} {i.nombre}: {i.stock_actual} pzas (mín: {i.stock_minimo})" for i in low_items]
            sections.append("⚠️ INVENTARIO BAJO MÍNIMO:\n" + "\n".join(lines))
        else:
            sections.append("INVENTARIO: Todos los artículos sobre el mínimo ✓")
    except Exception as e:
        sections.append(f"(Error cargando inventario: {e})")

    # --- CATÁLOGOS ---
    try:
        n_clients = await db.scalar(select(func.count(Client.id)))
        n_drivers = await db.scalar(select(func.count(Driver.id)))
        sections.append(f"CATÁLOGOS: {n_clients} clientes registrados, {n_drivers} operadores")
    except Exception as e:
        sections.append(f"(Error cargando catálogos: {e})")

    context = "\n\n".join(sections)
    from datetime import datetime as dt
    now_str = dt.now().strftime('%d/%m/%Y %H:%M')
    return f"""
--- CONTEXTO OPERATIVO EN TIEMPO REAL (Soluciones-TMS) ---
Fecha: {now_str} hrs

{context}

--- FIN DEL CONTEXTO ---
"""


@router.post("/chat", response_model=ChatResponse, tags=["IA"])
async def ai_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Chat endpoint for OpenRouter AI integration.
    El AI recibe un contexto rico con datos reales del DB.
    No se usa pgvector — el contexto se construye con SQL queries estructuradas.
    """
    if not settings.OPENROUTER_API_KEY:
        return ChatResponse(
            response=(
                "⚠️ La clave de API de OpenRouter no está configurada.\n\n"
                "Para activar el asistente con IA real:\n"
                "1. Crea una cuenta en [openrouter.ai](https://openrouter.ai)\n"
                "2. Genera una API key\n"
                "3. Agrégala en el archivo `.env` del backend: `OPENROUTER_API_KEY=sk-or-...`\n"
                "4. Reinicia el backend con Docker\n\n"
                "Mientras tanto, puedo responder preguntas basadas en los datos del sistema."
            ),
            sources=["Sistema"]
        )

    # Construir contexto enriquecido con datos reales del DB
    try:
        context = await build_rich_context(db)
    except Exception as e:
        context = f"(No se pudo cargar el contexto del sistema: {e})"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context},
        {"role": "user", "content": request.message}
    ]

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "http://localhost:3002",
                    "X-Title": "Soluciones-TMS",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "google/gemini-2.0-flash-001",  # Rápido y económico para demo
                    "messages": messages,
                    "max_tokens": 1500,
                },
            )

            if response.status_code != 200:
                print(f"OpenRouter Error {response.status_code}:", response.text)
                raise HTTPException(
                    status_code=502,
                    detail=f"Error comunicando con OpenRouter: {response.status_code}"
                )

            data = response.json()
            ai_message = data["choices"][0]["message"]["content"]

            return ChatResponse(
                response=ai_message,
                sources=["Base de Datos TMS en tiempo real"]
            )

    except HTTPException:
        raise
    except Exception as e:
        print("Exception en AI chat:", str(e))
        raise HTTPException(status_code=500, detail="Error interno procesando la solicitud de IA.")
