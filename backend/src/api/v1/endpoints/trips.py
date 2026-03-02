"""
CRUD endpoints for Trips, TripExpenses, DieselLoads, and TripComments
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.database import get_db
from src.api.v1.endpoints.auth import get_current_user
from src.models.user import User
from src.models.trips import Trip, TripExpense, DieselLoad, TripComment
from src.api.v1.schemas.trips import (
    TripCreate, TripUpdate, TripResponse, TripExpandedResponse,
    TripExpenseCreate, TripExpenseResponse,
    DieselLoadCreate, DieselLoadResponse,
    TripCommentCreate, TripCommentResponse
)
from src.api.v1.schemas.pagination import PaginatedResponse

router = APIRouter()

# ==================== TRIPS ====================

@router.get("/trips", response_model=PaginatedResponse[TripExpandedResponse], tags=["Operaciones - Viajes"])
async def list_trips(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=2000),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Trip).options(
        selectinload(Trip.expenses),
        selectinload(Trip.diesel_loads),
        selectinload(Trip.comments)
    )
    count_query = select(func.count()).select_from(Trip)
    
    if search:
        search_filter = (Trip.numero_viaje.ilike(f"%{search}%"))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
        
    total = await db.scalar(count_query)
    query = query.order_by(Trip.fecha_programada.desc().nulls_last()).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=items,
        total=total if total else 0,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )

@router.get("/trips/{trip_id}", response_model=TripExpandedResponse, tags=["Operaciones - Viajes"])
async def get_trip(trip_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Trip).options(
        selectinload(Trip.expenses),
        selectinload(Trip.diesel_loads),
        selectinload(Trip.comments)
    ).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return trip

@router.post("/trips", response_model=TripExpandedResponse, status_code=201, tags=["Operaciones - Viajes"])
async def create_trip(data: TripCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    trip = Trip(**data.model_dump())
    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    # Reload with relations
    return await get_trip(trip.id, db, current_user)

@router.patch("/trips/{trip_id}", response_model=TripExpandedResponse, tags=["Operaciones - Viajes"])
async def update_trip(trip_id: int, data: TripUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(trip, field, value)
    
    await db.commit()
    return await get_trip(trip.id, db, current_user)

@router.get("/trips/{trip_id}/profitability", tags=["Operaciones - Rentabilidad"])
async def get_trip_profitability(trip_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Consulta la rentabilidad calculada del viaje (Tarifa - Gastos)"""
    trip = await get_trip(trip_id, db, current_user)
    
    ingresos = trip.tarifa_cliente or 0.0
    gastos_viaje = sum(float(e.monto) for e in trip.expenses)
    gastos_diesel = sum(float(d.costo_total) for d in trip.diesel_loads)
    total_gastos = gastos_viaje + gastos_diesel
    
    utilidad = float(ingresos) - total_gastos
    margen = (utilidad / float(ingresos) * 100) if ingresos > 0 else 0.0
    
    return {
        "trip_id": trip.id,
        "ingresos": ingresos,
        "gastos_viaje": gastos_viaje,
        "gastos_diesel": gastos_diesel,
        "total_gastos": total_gastos,
        "utilidad": utilidad,
        "margen_porcentaje": round(margen, 2)
    }

# ==================== TRIP COMMENTS ====================

@router.post("/trips/{trip_id}/comments", response_model=TripCommentResponse, status_code=201, tags=["Operaciones - Timeline Tracking"])
async def create_trip_comment(trip_id: int, data: TripCommentCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = TripComment(**data.model_dump(), trip_id=trip_id, usuario_id=current_user.id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    # Módulo de notificaciones asume que se interceptará aquí o por medio de un background task, 
    # pero para la demo podemos dejarlo simple.
    return comment

# ==================== TRIP EXPENSES ====================

@router.post("/trips/{trip_id}/expenses", response_model=TripExpenseResponse, status_code=201, tags=["Operaciones - Gastos"])
async def create_trip_expense(trip_id: int, data: TripExpenseCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    expense = TripExpense(**data.model_dump(), trip_id=trip_id)
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return expense

# ==================== DIESEL LOADS ====================

@router.post("/trips/{trip_id}/diesel", response_model=DieselLoadResponse, status_code=201, tags=["Operaciones - Diesel"])
async def create_diesel_load(trip_id: int, data: DieselLoadCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    load = DieselLoad(**data.model_dump(), trip_id=trip_id)
    db.add(load)
    await db.commit()
    await db.refresh(load)
    return load
