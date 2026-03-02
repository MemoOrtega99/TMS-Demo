"""
Endpoints for Dashboard KPIs
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.core.database import get_db
from src.api.v1.endpoints.auth import get_current_user
from src.models.user import User
from src.models.trips import Trip, TripStatus
from src.models.invoices import Invoice, InvoiceType, InvoiceStatus
from src.models.fleet import Vehicle, VehicleStatus

router = APIRouter()

@router.get("/summary", tags=["Dashboard"])
async def dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard summary info
    """
    
    # Active trips
    trips_query = select(func.count(Trip.id)).where(Trip.estatus.in_([TripStatus.EN_RUTA, TripStatus.ASIGNADO]))
    active_trips = await db.scalar(trips_query)
    
    # Available vehicles
    vehicles_query = select(func.count(Vehicle.id)).where(Vehicle.estatus == VehicleStatus.DISPONIBLE)
    available_vehicles = await db.scalar(vehicles_query)
    
    # Overdue Receivables (CxC)
    cxc_query = select(func.sum(Invoice.total - Invoice.monto_pagado)).where(
        Invoice.tipo == InvoiceType.POR_COBRAR,
        Invoice.estatus == InvoiceStatus.VENCIDA
    )
    overdue_cxc = await db.scalar(cxc_query) or 0
    
    # Upcoming Payables (CxP)
    cxp_query = select(func.sum(Invoice.total - Invoice.monto_pagado)).where(
        Invoice.tipo == InvoiceType.POR_PAGAR,
        Invoice.estatus.in_([InvoiceStatus.PENDIENTE, InvoiceStatus.VENCIDA, InvoiceStatus.PARCIAL])
    )
    upcoming_cxp = await db.scalar(cxp_query) or 0
    
    return {
        "active_trips": active_trips or 0,
        "available_vehicles": available_vehicles or 0,
        "overdue_cxc": float(overdue_cxc),
        "upcoming_cxp": float(upcoming_cxp)
    }
