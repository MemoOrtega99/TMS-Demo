"""
CRUD endpoints for fleet (Vehicles, Trailers, Dollies, Services)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.database import get_db
from src.api.v1.endpoints.auth import get_current_user
from src.models.user import User
from src.models.fleet import Vehicle, Trailer, Dolly, VehicleService
from src.api.v1.schemas.fleet import (
    VehicleCreate, VehicleUpdate, VehicleResponse,
    TrailerCreate, TrailerUpdate, TrailerResponse,
    DollyCreate, DollyUpdate, DollyResponse,
    VehicleServiceCreate, VehicleServiceUpdate, VehicleServiceResponse
)
from src.api.v1.schemas.pagination import PaginatedResponse

router = APIRouter()

# ==================== VEHICLES ====================

@router.get("/vehicles", response_model=PaginatedResponse[VehicleResponse], tags=["Flota - Unidades"])
async def list_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=2000),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Vehicle)
    count_query = select(func.count()).select_from(Vehicle)
    
    if search:
        search_filter = (Vehicle.numero_economico.ilike(f"%{search}%")) | (Vehicle.placas.ilike(f"%{search}%"))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
        
    total = await db.scalar(count_query)
    query = query.order_by(Vehicle.numero_economico).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=items,
        total=total if total else 0,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )

@router.get("/vehicles/{vehicle_id}", response_model=VehicleResponse, tags=["Flota - Unidades"])
async def get_vehicle(vehicle_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    return vehicle

@router.post("/vehicles", response_model=VehicleResponse, status_code=201, tags=["Flota - Unidades"])
async def create_vehicle(data: VehicleCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    vehicle = Vehicle(**data.model_dump())
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle

@router.patch("/vehicles/{vehicle_id}", response_model=VehicleResponse, tags=["Flota - Unidades"])
async def update_vehicle(vehicle_id: int, data: VehicleUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    
    await db.commit()
    await db.refresh(vehicle)
    return vehicle

@router.delete("/vehicles/{vehicle_id}", status_code=204, tags=["Flota - Unidades"])
async def delete_vehicle(vehicle_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    
    await db.delete(vehicle)
    await db.commit()

# ==================== TRAILERS ====================

@router.get("/trailers", response_model=PaginatedResponse[TrailerResponse], tags=["Flota - Remolques"])
async def list_trailers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=2000),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Trailer)
    count_query = select(func.count()).select_from(Trailer)
    
    if search:
        search_filter = (Trailer.numero_economico.ilike(f"%{search}%")) | (Trailer.placas.ilike(f"%{search}%"))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
        
    total = await db.scalar(count_query)
    query = query.order_by(Trailer.numero_economico).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=items,
        total=total if total else 0,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )

@router.post("/trailers", response_model=TrailerResponse, status_code=201, tags=["Flota - Remolques"])
async def create_trailer(data: TrailerCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    trailer = Trailer(**data.model_dump())
    db.add(trailer)
    await db.commit()
    await db.refresh(trailer)
    return trailer

@router.patch("/trailers/{trailer_id}", response_model=TrailerResponse, tags=["Flota - Remolques"])
async def update_trailer(trailer_id: int, data: TrailerUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Trailer).where(Trailer.id == trailer_id))
    trailer = result.scalar_one_or_none()
    if not trailer:
        raise HTTPException(status_code=404, detail="Remolque no encontrado")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(trailer, field, value)
    
    await db.commit()
    await db.refresh(trailer)
    return trailer

# ==================== DOLLIES ====================

@router.get("/dollies", response_model=PaginatedResponse[DollyResponse], tags=["Flota - Dollies"])
async def list_dollies(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=2000),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Dolly)
    count_query = select(func.count()).select_from(Dolly)
    
    if search:
        search_filter = (Dolly.numero_economico.ilike(f"%{search}%")) | (Dolly.placas.ilike(f"%{search}%"))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
        
    total = await db.scalar(count_query)
    query = query.order_by(Dolly.numero_economico).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=items,
        total=total if total else 0,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )

@router.post("/dollies", response_model=DollyResponse, status_code=201, tags=["Flota - Dollies"])
async def create_dolly(data: DollyCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    dolly = Dolly(**data.model_dump())
    db.add(dolly)
    await db.commit()
    await db.refresh(dolly)
    return dolly

@router.patch("/dollies/{dolly_id}", response_model=DollyResponse, tags=["Flota - Dollies"])
async def update_dolly(dolly_id: int, data: DollyUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Dolly).where(Dolly.id == dolly_id))
    dolly = result.scalar_one_or_none()
    if not dolly:
        raise HTTPException(status_code=404, detail="Dolly no encontrado")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(dolly, field, value)
    
    await db.commit()
    await db.refresh(dolly)
    return dolly

# ==================== VEHICLE SERVICES ====================

@router.get("/vehicles/{vehicle_id}/services", response_model=List[VehicleServiceResponse], tags=["Flota - Servicios"])
async def list_vehicle_services(vehicle_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = select(VehicleService).where(VehicleService.vehicle_id == vehicle_id).order_by(VehicleService.fecha_servicio.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/vehicles/{vehicle_id}/services", response_model=VehicleServiceResponse, status_code=201, tags=["Flota - Servicios"])
async def create_vehicle_service(vehicle_id: int, data: VehicleServiceCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = VehicleService(**data.model_dump(), vehicle_id=vehicle_id)
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service
