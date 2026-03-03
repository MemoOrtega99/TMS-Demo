"""
Purchases and Requisitions Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.database import get_db
from src.api.v1.endpoints.auth import get_current_user
from src.models.user import User
from src.models.purchases import PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus
from src.api.v1.schemas.purchases import (
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse, 
    PurchaseOrderWithDetailsResponse, PurchaseOrderSimpleCreate
)
from src.api.v1.schemas.pagination import PaginatedResponse

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[PurchaseOrderResponse], tags=["Compras - Órdenes"])
async def list_purchase_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    search: Optional[str] = None,
    estatus: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(PurchaseOrder)
    count_query = select(func.count()).select_from(PurchaseOrder)
    
    if search:
        search_filter = (PurchaseOrder.numero.ilike(f"%{search}%"))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
        
    if estatus:
        query = query.where(PurchaseOrder.estatus == estatus)
        count_query = count_query.where(PurchaseOrder.estatus == estatus)
        
    total = await db.scalar(count_query)
    query = query.order_by(PurchaseOrder.fecha_orden.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=items,
        total=total if total else 0,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )

@router.get("/{order_id}", response_model=PurchaseOrderWithDetailsResponse, tags=["Compras - Órdenes"])
async def get_purchase_order(order_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(PurchaseOrder)
        .options(selectinload(PurchaseOrder.items))
        .where(PurchaseOrder.id == order_id)
    )
    po = result.scalar_one_or_none()
    if not po:
        raise HTTPException(status_code=404, detail="Orden de compra no encontrada")
    return po
@router.post("/", response_model=PurchaseOrderResponse, tags=["Compras - Órdenes"])
async def create_purchase_order(
    obj_in: PurchaseOrderSimpleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Simplified PO creation for the new form
    po = PurchaseOrder(
        numero=obj_in.numero_orden,
        proveedor_id=obj_in.proveedor_id,
        fecha_orden=obj_in.fecha_orden,
        fecha_entrega_esperada=obj_in.fecha_entrega,
        total=obj_in.total,
        subtotal=obj_in.total / Decimal("1.16"), # Dummy calc for now
        iva=obj_in.total - (obj_in.total / Decimal("1.16")),
        estatus=obj_in.estatus,
        # Requisition is optional now
    )
    db.add(po)
    await db.commit()
    await db.refresh(po)
    return po
