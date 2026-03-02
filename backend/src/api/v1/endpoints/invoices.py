"""
Endpoints for Invoices and Payments
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.database import get_db
from src.api.v1.endpoints.auth import get_current_user
from src.models.user import User
from src.models.invoices import Invoice, Payment, InvoiceStatus
from src.api.v1.schemas.invoices import (
    InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceExpandedResponse,
    PaymentCreate, PaymentResponse
)
from src.api.v1.schemas.pagination import PaginatedResponse

router = APIRouter()

# ==================== INVOICES ====================

@router.get("/invoices", response_model=PaginatedResponse[InvoiceExpandedResponse], tags=["Finanzas - Facturas"])
async def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    tipo: Optional[str] = None, # POR_PAGAR | POR_COBRAR
    estatus: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Invoice).options(selectinload(Invoice.payments))
    count_query = select(func.count()).select_from(Invoice)
    
    filters = []
    if tipo:
        filters.append(Invoice.tipo == tipo)
    if estatus:
        filters.append(Invoice.estatus == estatus)
    if search:
        filters.append(Invoice.numero_factura.ilike(f"%{search}%"))
        
    if filters:
        for f in filters:
            query = query.where(f)
            count_query = count_query.where(f)
            
    total = await db.scalar(count_query)
    query = query.order_by(Invoice.fecha_vencimiento.asc().nulls_last()).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=items,
        total=total if total else 0,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )

@router.get("/invoices/{invoice_id}", response_model=InvoiceExpandedResponse, tags=["Finanzas - Facturas"])
async def get_invoice(invoice_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Invoice).options(selectinload(Invoice.payments)).where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return invoice

@router.post("/invoices", response_model=InvoiceExpandedResponse, status_code=201, tags=["Finanzas - Facturas"])
async def create_invoice(data: InvoiceCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoice = Invoice(**data.model_dump())
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    return await get_invoice(invoice.id, db, current_user)

@router.patch("/invoices/{invoice_id}", response_model=InvoiceExpandedResponse, tags=["Finanzas - Facturas"])
async def update_invoice(invoice_id: int, data: InvoiceUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoice = await get_invoice(invoice_id, db, current_user)
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(invoice, field, value)
    
    await db.commit()
    return await get_invoice(invoice.id, db, current_user)

@router.delete("/invoices/{invoice_id}", status_code=204, tags=["Finanzas - Facturas"])
async def delete_invoice(invoice_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoice = await get_invoice(invoice_id, db, current_user)
    await db.delete(invoice)
    await db.commit()

# ==================== PAYMENTS ====================

@router.post("/invoices/{invoice_id}/payments", response_model=PaymentResponse, status_code=201, tags=["Finanzas - Pagos"])
async def create_payment(invoice_id: int, data: PaymentCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoice = await get_invoice(invoice_id, db, current_user)
    
    # Crear el pago
    payment = Payment(**data.model_dump(exclude={"invoice_id"}), invoice_id=invoice_id, usuario_id=current_user.id)
    db.add(payment)
    
    # Actualizar monto_pagado y estatus en la factura
    invoice.monto_pagado += payment.monto
    if invoice.monto_pagado >= invoice.total:
        invoice.monto_pagado = invoice.total # Asegurar que no exceda (o manejar según lógica de negocio)
        invoice.estatus = InvoiceStatus.PAGADA
    else:
        invoice.estatus = InvoiceStatus.PARCIAL

    await db.commit()
    await db.refresh(payment)
    return payment

# ==================== AGING REPORT (Cuentas por cobrar/pagar vencidas) ====================

@router.get("/reports/aging", tags=["Finanzas - Reportes"])
async def get_aging_report(
    tipo: str = Query("POR_COBRAR", description="POR_PAGAR o POR_COBRAR"), 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Genera reporte de antigüedad de saldos"""
    query = select(Invoice).where(
        Invoice.tipo == tipo,
        Invoice.estatus.in_([InvoiceStatus.PENDIENTE, InvoiceStatus.PARCIAL])
    )
    result = await db.execute(query)
    invoices = result.scalars().all()
    
    from datetime import date
    today = date.today()
    
    report = {
        "corriente": 0.0,
        "1_30_dias": 0.0,
        "31_60_dias": 0.0,
        "61_90_dias": 0.0,
        "mas_90_dias": 0.0,
        "total": 0.0
    }
    
    for inv in invoices:
        saldo = float(inv.total - inv.monto_pagado)
        report["total"] += saldo
        
        if not inv.fecha_vencimiento or inv.fecha_vencimiento >= today:
            report["corriente"] += saldo
        else:
            dias_vencido = (today - inv.fecha_vencimiento).days
            if dias_vencido <= 30:
                report["1_30_dias"] += saldo
            elif dias_vencido <= 60:
                report["31_60_dias"] += saldo
            elif dias_vencido <= 90:
                report["61_90_dias"] += saldo
            else:
                report["mas_90_dias"] += saldo
                
    return report
