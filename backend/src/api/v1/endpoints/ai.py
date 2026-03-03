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
    Construye un contexto robusto para responder preguntas del dashboard:
    - Rentabilidad de viajes
    - Rendimiento de diesel
    - Resumen mensual (Febrero 2026)
    - CxC vencidas
    """
    sections = []
    from datetime import date, datetime
    from sqlalchemy import String, func, text, desc

    # --- 1. VIAJES Y RENTABILIDAD ---
    try:
        # Viaje más rentable del mes (Tarifa - Gastos)
        prof_q = await db.execute(text("""
            SELECT t.numero_viaje, t.origen, t.destino, t.tarifa_cliente, 
                   COALESCE(SUM(e.monto), 0) as total_gastos,
                   (t.tarifa_cliente - COALESCE(SUM(e.monto), 0)) as utilidad
            FROM trips t
            LEFT JOIN trip_expenses e ON t.id = e.trip_id
            WHERE (t.estatus::text LIKE '%completado%')
              AND t.fecha_entrega_real >= '2026-02-01'
            GROUP BY t.id, t.numero_viaje, t.origen, t.destino, t.tarifa_cliente
            ORDER BY utilidad DESC
            LIMIT 1
        """))
        best_trip = prof_q.fetchone()
        if best_trip and best_trip.utilidad is not None:
            sections.append(f"VIAJE MÁS RENTABLE (Feb 2026): {best_trip.numero_viaje} ({best_trip.origen}-{best_trip.destino}) | Utilidad: ${float(best_trip.utilidad):,.2f} (Tarifa: ${float(best_trip.tarifa_cliente or 0):,.0f} - Gastos: ${float(best_trip.total_gastos or 0):,.0f})")
        
        # Resumen de estatus
        trips_by_status = await db.execute(select(Trip.estatus, func.count(Trip.id)).group_by(Trip.estatus))
        sections.append(f"RESUMEN OPERATIVO TOTAL (Viajes): {dict(trips_by_status.all())}")
    except Exception as e:
        sections.append(f"(Error en análisis de viajes: {e})")
        await db.rollback()

    # --- 2. RENDIMIENTO DE DIESEL ---
    try:
        # Rendimiento promedio de la flota
        diesel_perf = await db.execute(text("""
            SELECT v.id, v.placas, 
                   SUM(l.litros) as total_litros,
                   (MAX(l.km_odometro) - MIN(l.km_odometro)) as km_recorridos
            FROM diesel_loads l
            JOIN vehicles v ON l.vehicle_id = v.id
            GROUP BY v.id, v.placas
            HAVING (MAX(l.km_odometro) - MIN(l.km_odometro)) > 0
        """))
        perf_rows = diesel_perf.all()
        if perf_rows:
            perf_lines = []
            total_km = 0
            total_l = 0
            for r in perf_rows:
                rend = r.km_recorridos / r.total_litros if r.total_litros > 0 else 0
                perf_lines.append(f"  - Unidad {r.placas}: {rend:.2f} km/L")
                total_km += r.km_recorridos
                total_l += r.total_litros
            
            avg_rend = total_km / total_l if total_l > 0 else 0
            sections.append(f"RENDIMIENTO DE DIESEL DE LA FLOTA: {avg_rend:.2f} km/L promedio\n" + "\n".join(perf_lines))
    except Exception as e:
        sections.append(f"(Error en análisis de diesel: {e})")
        await db.rollback()

    # --- 3. FINANZAS Y CXC VENCIDAS ---
    try:
        today = date.today()
        # Saldo total vencido
        vencido_q = await db.execute(
            select(func.sum(Invoice.total - Invoice.monto_pagado))
            .where(Invoice.tipo == InvoiceType.POR_COBRAR, Invoice.fecha_vencimiento < today, Invoice.estatus.cast(String).not_ilike('%PAGADA%'))
        )
        total_vencido = vencido_q.scalar() or 0
        
        # Facturas vencidas importantes
        top_vencidas = await db.execute(
            select(Invoice.numero_factura, Client.nombre, (Invoice.total - Invoice.monto_pagado).label('saldo'), Invoice.fecha_vencimiento)
            .join(Client, Invoice.cliente_id == Client.id)
            .where(Invoice.tipo == InvoiceType.POR_COBRAR, Invoice.fecha_vencimiento < today, Invoice.estatus.cast(String).not_ilike('%PAGADA%'))
            .order_by(desc('saldo'))
            .limit(3)
        )
        v_lines = [f"  - {r.numero_factura} ({r.nombre}): ${float(r.saldo):,.2f} | Venció: {r.fecha_vencimiento}" for r in top_vencidas]
        
        sections.append(f"CUENTAS POR COBRAR VENCIDAS: ${float(total_vencido):,.2f} MXN\n" + "\n".join(v_lines))
    except Exception as e:
        sections.append(f"(Error en análisis financiero: {e})")
        await db.rollback()

    # --- 4. RESUMEN EJECUTIVO FEBRERO 2026 ---
    try:
        feb_q = await db.execute(text("""
            SELECT COUNT(id) as total, 
                   SUM(tarifa_cliente) as ingresos
            FROM trips 
            WHERE (estatus::text LIKE '%completado%')
              AND fecha_entrega_real >= '2026-02-01' AND fecha_entrega_real <= '2026-02-28 23:59:59'
        """))
        feb_stats = feb_q.fetchone()
        
        feb_exp_q = await db.execute(text("""
            SELECT SUM(monto) FROM trip_expenses 
            WHERE fecha_gasto >= '2026-02-01' AND fecha_gasto <= '2026-02-28'
        """))
        feb_exp = feb_exp_q.scalar() or 0
        
        if feb_stats and feb_stats.total > 0:
            ingresos = float(feb_stats.ingresos or 0)
            gastos = float(feb_exp or 0)
            utilidad = ingresos - gastos
            sections.append(f"RESUMEN EJECUTIVO FEBRERO 2026:\n  - Viajes completados: {feb_stats.total}\n  - Ingresos totales: ${ingresos:,.2f}\n  - Gastos operativos: ${gastos:,.2f}\n  - Margen operativo: ${utilidad:,.2f}")
    except Exception as e:
        sections.append(f"(Error en resumen mensual: {e})")
        await db.rollback()

    # --- 5. RENDIMIENTO POR OPERADOR (Detallado) ---
    try:
        # Viajes + ingresos + gastos por operador
        op_perf = await db.execute(text("""
            SELECT 
                d.nombre || ' ' || d.apellido AS operador,
                COUNT(t.id)                   AS viajes_completados,
                COALESCE(SUM(t.tarifa_cliente), 0)                            AS ingresos,
                COALESCE(SUM(e.total_gastos), 0)                              AS gastos,
                COALESCE(SUM(t.tarifa_cliente), 0) - COALESCE(SUM(e.total_gastos), 0) AS utilidad
            FROM drivers d
            JOIN trips t ON t.chofer_id = d.id
            LEFT JOIN (
                SELECT trip_id, SUM(monto) AS total_gastos FROM trip_expenses GROUP BY trip_id
            ) e ON e.trip_id = t.id
            WHERE (t.estatus::text LIKE '%completado%')
            GROUP BY d.id, d.nombre, d.apellido
            ORDER BY viajes_completados DESC
        """))
        op_rows = op_perf.all()
        if op_rows:
            op_lines = []
            for r in op_rows:
                margen = (float(r.utilidad) / float(r.ingresos) * 100) if r.ingresos else 0
                op_lines.append(
                    f"  - {r.operador}: {r.viajes_completados} viajes | "
                    f"Ingresos ${float(r.ingresos):,.0f} | "
                    f"Gastos ${float(r.gastos):,.0f} | "
                    f"Utilidad ${float(r.utilidad):,.0f} | "
                    f"Margen {margen:.1f}%"
                )
            sections.append("RENDIMIENTO POR OPERADOR:\n" + "\n".join(op_lines))
    except Exception as e:
        sections.append(f"(Error en rendimiento de operadores: {e})")
        await db.rollback()

    # --- 6. RENDIMIENTO POR UNIDAD (Flota) ---
    try:
        # Viajes + ingresos + diesel (km/L) por vehículo
        unit_perf = await db.execute(text("""
            SELECT 
                v.placas,
                v.modelo,
                COUNT(t.id)                              AS viajes,
                COALESCE(SUM(t.tarifa_cliente), 0)       AS ingresos,
                COALESCE(SUM(dl.litros_total), 0)        AS litros_consumidos,
                COALESCE(SUM(dl.costo_diesel), 0)        AS costo_diesel,
                COALESCE(SUM(dl.km_delta), 0)            AS km_recorridos
            FROM vehicles v
            LEFT JOIN trips t ON t.vehiculo_id = v.id
              AND (t.estatus::text LIKE '%completado%')
            LEFT JOIN (
                SELECT 
                    vehicle_id,
                    SUM(litros)       AS litros_total,
                    SUM(costo_total)  AS costo_diesel,
                    MAX(km_odometro) - MIN(km_odometro) AS km_delta
                FROM diesel_loads
                GROUP BY vehicle_id
            ) dl ON dl.vehicle_id = v.id
            GROUP BY v.id, v.placas, v.modelo
            ORDER BY viajes DESC
        """))
        unit_rows = unit_perf.all()
        if unit_rows:
            unit_lines = []
            for r in unit_rows:
                rend_kml = (float(r.km_recorridos) / float(r.litros_consumidos)) if r.litros_consumidos else 0
                unit_lines.append(
                    f"  - {r.placas} ({r.modelo or 'N/A'}): "
                    f"{r.viajes} viajes | "
                    f"Ingresos ${float(r.ingresos):,.0f} | "
                    f"Diesel ${float(r.costo_diesel):,.0f} | "
                    f"Rendimiento {rend_kml:.2f} km/L"
                )
            sections.append("RENDIMIENTO POR UNIDAD (FLOTA):\n" + "\n".join(unit_lines))
    except Exception as e:
        sections.append(f"(Error en rendimiento de flota: {e})")
        await db.rollback()

    context = "\n\n".join(sections)
    now_str = datetime.now().strftime('%d/%m/%Y %H:%M')
    return f"""
--- CONTEXTO OPERATIVO ESTRATÉGICO (Soluciones-TMS) ---
Fecha del reporte: {now_str}
Usa estos datos para responder las preguntas del dashboard de forma ejecutiva.

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
