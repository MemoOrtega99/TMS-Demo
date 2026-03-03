"""
Inventory Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.database import get_db
from src.api.v1.endpoints.auth import get_current_user
from src.models.user import User
from src.models.inventory import InventoryItem, InventoryMovement
from src.api.v1.schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse, InventoryItemWithMovementsResponse,
    InventoryMovementCreate, InventoryMovementResponse
)
from src.api.v1.schemas.pagination import PaginatedResponse

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[InventoryItemResponse], tags=["Inventario"])
async def list_inventory_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    search: Optional[str] = None,
    categoria: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(InventoryItem)
    count_query = select(func.count()).select_from(InventoryItem)
    
    if search:
        search_filter = (InventoryItem.codigo.ilike(f"%{search}%")) | (InventoryItem.nombre.ilike(f"%{search}%"))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
        
    if categoria:
        query = query.where(InventoryItem.categoria == categoria)
        count_query = count_query.where(InventoryItem.categoria == categoria)
        
    total = await db.scalar(count_query)
    query = query.order_by(InventoryItem.nombre).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=items,
        total=total if total else 0,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )

@router.get("/{item_id}", response_model=InventoryItemWithMovementsResponse, tags=["Inventario"])
async def get_inventory_item(item_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(InventoryItem)
        .options(selectinload(InventoryItem.movements))
        .where(InventoryItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Articulo no encontrado")
    return item
@router.post("/", response_model=InventoryItemResponse, tags=["Inventario"])
async def create_inventory_item(
    obj_in: InventoryItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if code already exists
    result = await db.execute(select(InventoryItem).where(InventoryItem.codigo == obj_in.codigo))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El código de artículo ya existe")

    item = InventoryItem(**obj_in.dict())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
