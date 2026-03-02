"""
CRUD endpoints for catalogs (Drivers, Clients, Suppliers)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.api.v1.endpoints.auth import get_current_user
from src.models.user import User
from src.models.catalogs import Driver, Client, Supplier
from src.api.v1.schemas.catalogs import (
    DriverCreate, DriverUpdate, DriverResponse,
    ClientCreate, ClientUpdate, ClientResponse,
    SupplierCreate, SupplierUpdate, SupplierResponse
)
from src.api.v1.schemas.pagination import PaginatedResponse

router = APIRouter()

# ==================== DRIVERS ====================

@router.get("/drivers", response_model=PaginatedResponse[DriverResponse], tags=["Catálogos - Choferes"])
async def list_drivers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=2000),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Driver)
    count_query = select(func.count()).select_from(Driver)
    
    if search:
        search_filter = (Driver.nombre.ilike(f"%{search}%")) | (Driver.apellido.ilike(f"%{search}%"))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
        
    total = await db.scalar(count_query)
    query = query.order_by(Driver.nombre).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=items,
        total=total if total else 0,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )

@router.get("/drivers/{driver_id}", response_model=DriverResponse, tags=["Catálogos - Choferes"])
async def get_driver(driver_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Chofer no encontrado")
    return driver

@router.post("/drivers", response_model=DriverResponse, status_code=201, tags=["Catálogos - Choferes"])
async def create_driver(data: DriverCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    driver = Driver(**data.model_dump())
    db.add(driver)
    await db.commit()
    await db.refresh(driver)
    return driver

@router.patch("/drivers/{driver_id}", response_model=DriverResponse, tags=["Catálogos - Choferes"])
async def update_driver(driver_id: int, data: DriverUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Chofer no encontrado")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(driver, field, value)
    
    await db.commit()
    await db.refresh(driver)
    return driver

@router.delete("/drivers/{driver_id}", status_code=204, tags=["Catálogos - Choferes"])
async def delete_driver(driver_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Chofer no encontrado")
    
    await db.delete(driver)
    await db.commit()

# ==================== CLIENTS ====================

@router.get("/clients", response_model=PaginatedResponse[ClientResponse], tags=["Catálogos - Clientes"])
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=2000),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Client)
    count_query = select(func.count()).select_from(Client)
    
    if search:
        search_filter = (Client.nombre.ilike(f"%{search}%")) | (Client.rfc.ilike(f"%{search}%"))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
        
    total = await db.scalar(count_query)
    query = query.order_by(Client.nombre).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=items,
        total=total if total else 0,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )

@router.get("/clients/{client_id}", response_model=ClientResponse, tags=["Catálogos - Clientes"])
async def get_client(client_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client

@router.post("/clients", response_model=ClientResponse, status_code=201, tags=["Catálogos - Clientes"])
async def create_client(data: ClientCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    client = Client(**data.model_dump())
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client

@router.patch("/clients/{client_id}", response_model=ClientResponse, tags=["Catálogos - Clientes"])
async def update_client(client_id: int, data: ClientUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    
    await db.commit()
    await db.refresh(client)
    return client

@router.delete("/clients/{client_id}", status_code=204, tags=["Catálogos - Clientes"])
async def delete_client(client_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    await db.delete(client)
    await db.commit()

# ==================== SUPPLIERS ====================

@router.get("/suppliers", response_model=PaginatedResponse[SupplierResponse], tags=["Catálogos - Proveedores"])
async def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=2000),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Supplier)
    count_query = select(func.count()).select_from(Supplier)
    
    if search:
        search_filter = (Supplier.nombre.ilike(f"%{search}%")) | (Supplier.rfc.ilike(f"%{search}%"))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
        
    total = await db.scalar(count_query)
    query = query.order_by(Supplier.nombre).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=items,
        total=total if total else 0,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )

@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse, tags=["Catálogos - Proveedores"])
async def get_supplier(supplier_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return supplier

@router.post("/suppliers", response_model=SupplierResponse, status_code=201, tags=["Catálogos - Proveedores"])
async def create_supplier(data: SupplierCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)
    return supplier

@router.patch("/suppliers/{supplier_id}", response_model=SupplierResponse, tags=["Catálogos - Proveedores"])
async def update_supplier(supplier_id: int, data: SupplierUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(supplier, field, value)
    
    await db.commit()
    await db.refresh(supplier)
    return supplier

@router.delete("/suppliers/{supplier_id}", status_code=204, tags=["Catálogos - Proveedores"])
async def delete_supplier(supplier_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    await db.delete(supplier)
    await db.commit()
