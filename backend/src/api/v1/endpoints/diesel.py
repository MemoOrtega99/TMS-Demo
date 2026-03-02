"""
Diesel module endpoints.
Covers: Cargas de diesel, Rendimientos, Tanque del patio.
"""
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from src.core.database import get_db
from src.api.v1.endpoints.auth import get_current_user
from src.models.user import User
from src.models.trips import DieselLoad, DieselLoadType
from src.models.catalogs import Vehicle, Driver
from src.models.inventory import InventoryItem, InventoryMovement, InventoryCategory, MovementType, MovementReason
from src.api.v1.schemas.diesel import (
    DieselLoadCreate, DieselLoadUpdate, DieselLoadResponse,
    TankEntryCreate, TankStatusResponse,
    RendimientoVehiculo, DieselSummary,
)

router = APIRouter(prefix="/diesel")


# ==================== HELPERS ====================

def _calc_fields(load: DieselLoad) -> dict:
    """Calculate derived fields for a diesel load."""
    distancia_km = None
    rendimiento_fisico = None
    rendimiento_insite = None
    diferencia_diesel = None

    if load.km_odometro and load.km_anterior and load.km_odometro > load.km_anterior:
        distancia_km = load.km_odometro - load.km_anterior
        if load.litros_cargados and load.litros_cargados > 0:
            rendimiento_fisico = round(Decimal(distancia_km) / load.litros_cargados, 2)

    if load.distancia_insite and load.diesel_computadora and load.diesel_computadora > 0:
        rendimiento_insite = round(load.distancia_insite / load.diesel_computadora, 2)

    if load.litros_cargados and load.diesel_computadora:
        diferencia_diesel = round(load.litros_cargados - load.diesel_computadora, 2)

    return {
        "distancia_km": distancia_km,
        "rendimiento_fisico": rendimiento_fisico,
        "rendimiento_insite": rendimiento_insite,
        "diferencia_diesel": diferencia_diesel,
    }


async def _enrich_load(load: DieselLoad, db: AsyncSession) -> DieselLoadResponse:
    """Build DieselLoadResponse with resolved names and calculated fields."""
    data = DieselLoadResponse.model_validate(load)

    # Resolve vehicle eco
    vehicle = await db.get(Vehicle, load.vehiculo_id)
    data.vehiculo_eco = vehicle.numero_economico if vehicle else None

    # Resolve driver name
    if load.chofer_id:
        driver = await db.get(Driver, load.chofer_id)
        data.chofer_nombre = f"{driver.nombre} {driver.apellidos}" if driver else None

    # Resolve trip number
    if load.trip_id:
        from src.models.trips import Trip
        trip = await db.get(Trip, load.trip_id)
        data.numero_viaje = trip.numero_viaje if trip else None

    # Calculated fields
    calc = _calc_fields(load)
    for k, v in calc.items():
        setattr(data, k, v)

    return data


async def _get_diesel_tank(db: AsyncSession) -> Optional[InventoryItem]:
    """Get the diesel tank inventory item (category=combustible)."""
    result = await db.execute(
        select(InventoryItem).where(
            and_(
                InventoryItem.codigo == "DIESEL-TANQUE",
                InventoryItem.is_deleted == False,
            )
        ).limit(1)
    )
    return result.scalar_one_or_none()


# ==================== SUMMARY ====================

@router.get("/summary", response_model=DieselSummary)
async def get_diesel_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dashboard summary: tank level + month stats."""
    today = date.today()
    first_of_month = today.replace(day=1)

    # Tank status
    tank = await _get_diesel_tank(db)
    stock_tanque = tank.stock_actual if tank else Decimal(0)
    stock_maximo = (tank.stock_maximo if tank and tank.stock_maximo else None) or Decimal(40000)
    porcentaje_tanque = round((stock_tanque / stock_maximo) * 100, 1) if stock_maximo > 0 else Decimal(0)


    # Month stats
    result = await db.execute(
        select(
            func.coalesce(func.sum(DieselLoad.litros_cargados), 0),
            func.coalesce(func.sum(DieselLoad.costo_total), 0),
            func.count(DieselLoad.id),
        ).where(
            and_(
                DieselLoad.is_deleted == False,
                DieselLoad.fecha_carga >= datetime.combine(first_of_month, datetime.min.time()),
            )
        )
    )
    litros_mes, costo_mes, cargas_mes = result.one()

    # Fleet average rendimiento (last 30 days, only loads with km data)
    result = await db.execute(
        select(DieselLoad).where(
            and_(
                DieselLoad.is_deleted == False,
                DieselLoad.km_odometro != None,
                DieselLoad.km_anterior != None,
                DieselLoad.litros_cargados > 0,
            )
        ).limit(200)
    )
    loads = result.scalars().all()
    rendimiento_flota = None
    valid = [(l.km_odometro - l.km_anterior, l.litros_cargados)
             for l in loads
             if l.km_odometro > l.km_anterior and l.litros_cargados > 0]
    if valid:
        total_km = sum(d for d, _ in valid)
        total_l = sum(l for _, l in valid)
        if total_l > 0:
            rendimiento_flota = round(Decimal(total_km) / total_l, 2)

    return DieselSummary(
        stock_tanque=float(stock_tanque),
        porcentaje_tanque=float(porcentaje_tanque),
        litros_mes=float(litros_mes),
        costo_mes=float(costo_mes),
        cargas_mes=cargas_mes,
        rendimiento_flota=float(rendimiento_flota) if rendimiento_flota is not None else None,
    )


# ==================== CARGAS ====================

@router.get("/cargas", response_model=List[DieselLoadResponse])
async def list_diesel_loads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=2000),
    vehiculo_id: Optional[int] = None,
    tipo: Optional[str] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List diesel loads with filters."""
    query = select(DieselLoad).where(DieselLoad.is_deleted == False)

    if vehiculo_id:
        query = query.where(DieselLoad.vehiculo_id == vehiculo_id)
    if tipo:
        query = query.where(DieselLoad.tipo == tipo)
    if fecha_desde:
        query = query.where(DieselLoad.fecha_carga >= datetime.combine(fecha_desde, datetime.min.time()))
    if fecha_hasta:
        query = query.where(DieselLoad.fecha_carga <= datetime.combine(fecha_hasta, datetime.max.time()))

    query = query.order_by(DieselLoad.fecha_carga.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    loads = result.scalars().all()

    return [await _enrich_load(load, db) for load in loads]


@router.post("/cargas", response_model=DieselLoadResponse, status_code=201)
async def create_diesel_load(
    data: DieselLoadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Register a diesel load. If tipo=patio, decrements tank inventory."""
    # Validate vehicle exists
    vehicle = await db.get(Vehicle, data.vehiculo_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")

    load = DieselLoad(
        vehiculo_id=data.vehiculo_id,
        chofer_id=data.chofer_id,
        trip_id=data.trip_id,
        tipo=data.tipo,
        litros_cargados=data.litros_cargados,
        costo_por_litro=data.costo_por_litro,
        costo_total=data.costo_total,
        km_anterior=data.km_anterior,
        km_odometro=data.km_odometro,
        diesel_computadora=data.diesel_computadora,
        diesel_consumido=data.diesel_computadora,  # alias
        distancia_insite=data.distancia_insite,
        fecha_carga=data.fecha_carga,
        registrado_por=current_user.id,
        notes=data.notes,
    )
    db.add(load)

    # Update vehicle odometer
    if data.km_odometro:
        vehicle.kilometraje_actual = data.km_odometro

    # Decrement tank if patio load
    if data.tipo == DieselLoadType.patio:
        tank = await _get_diesel_tank(db)
        if tank:
            prev_stock = tank.stock_actual
            tank.stock_actual = max(Decimal(0), tank.stock_actual - data.litros_cargados)
            movement = InventoryMovement(
                numero=f"DIESEL-OUT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                inventory_item_id=tank.id,
                tipo=MovementType.SALIDA,
                razon=MovementReason.CONSUMO,
                cantidad=data.litros_cargados,
                fecha_movimiento=data.fecha_carga,
                costo_unitario=tank.costo_promedio,
                stock_resultante=tank.stock_actual,
                referencia=f"Carga a unidad {vehicle.numero_economico}",
                usuario_id=current_user.id,
            )
            db.add(movement)

    await db.commit()
    await db.refresh(load)
    return await _enrich_load(load, db)


@router.put("/cargas/{load_id}", response_model=DieselLoadResponse)
async def update_diesel_load(
    load_id: int,
    data: DieselLoadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a diesel load."""
    load = await db.get(DieselLoad, load_id)
    if not load or load.is_deleted:
        raise HTTPException(status_code=404, detail="Carga no encontrada")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(load, key, value)

    await db.commit()
    await db.refresh(load)
    return await _enrich_load(load, db)


@router.delete("/cargas/{load_id}")
async def delete_diesel_load(
    load_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete a diesel load."""
    load = await db.get(DieselLoad, load_id)
    if not load or load.is_deleted:
        raise HTTPException(status_code=404, detail="Carga no encontrada")

    load.is_deleted = True
    load.deleted_by = current_user.id
    await db.commit()
    return {"message": "Carga eliminada"}


# ==================== RENDIMIENTOS ====================

@router.get("/rendimientos", response_model=List[RendimientoVehiculo])
async def get_rendimientos(
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    vehiculo_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get fuel efficiency by vehicle for a period."""
    query = select(DieselLoad).where(DieselLoad.is_deleted == False)

    if vehiculo_id:
        query = query.where(DieselLoad.vehiculo_id == vehiculo_id)
    if fecha_desde:
        query = query.where(DieselLoad.fecha_carga >= datetime.combine(fecha_desde, datetime.min.time()))
    if fecha_hasta:
        query = query.where(DieselLoad.fecha_carga <= datetime.combine(fecha_hasta, datetime.max.time()))

    result = await db.execute(query)
    loads = result.scalars().all()

    # Group by vehicle
    by_vehicle: dict = {}
    for load in loads:
        vid = load.vehiculo_id
        if vid not in by_vehicle:
            by_vehicle[vid] = []
        by_vehicle[vid].append(load)

    rendimientos = []
    for vid, vloads in by_vehicle.items():
        vehicle = await db.get(Vehicle, vid)
        if not vehicle:
            continue

        total_litros = sum(l.litros_cargados for l in vloads)
        total_km = None
        rend_fisico = None
        rend_insite = None
        dif_promedio = None

        # Physical rendimiento
        km_pairs = [(l.km_odometro - l.km_anterior, l.litros_cargados)
                    for l in vloads
                    if l.km_odometro and l.km_anterior and l.km_odometro > l.km_anterior and l.litros_cargados > 0]
        if km_pairs:
            total_km = sum(d for d, _ in km_pairs)
            total_l_km = sum(l for _, l in km_pairs)
            if total_l_km > 0:
                rend_fisico = round(Decimal(total_km) / total_l_km, 2)

        # Insite rendimiento
        insite_pairs = [(l.distancia_insite, l.diesel_computadora)
                        for l in vloads
                        if l.distancia_insite and l.diesel_computadora and l.diesel_computadora > 0]
        if insite_pairs:
            total_dist_i = sum(d for d, _ in insite_pairs)
            total_l_i = sum(l for _, l in insite_pairs)
            if total_l_i > 0:
                rend_insite = round(total_dist_i / total_l_i, 2)

        # Diferencia promedio
        dif_pairs = [l.litros_cargados - l.diesel_computadora
                     for l in vloads
                     if l.diesel_computadora is not None]
        if dif_pairs:
            dif_promedio = round(sum(dif_pairs) / len(dif_pairs), 2)

        rendimientos.append(RendimientoVehiculo(
            vehiculo_id=vid,
            vehiculo_eco=vehicle.numero_economico,
            total_cargas=len(vloads),
            total_litros=total_litros,
            total_km=total_km,
            rendimiento_fisico_promedio=rend_fisico,
            rendimiento_insite_promedio=rend_insite,
            diferencia_promedio=dif_promedio,
        ))

    return sorted(rendimientos, key=lambda r: r.vehiculo_eco)


# ==================== RANKING POR CHOFER ====================

@router.get("/rendimientos/choferes")
async def get_rendimientos_choferes(
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get fuel efficiency ranking grouped by driver."""
    query = select(DieselLoad).where(
        and_(
            DieselLoad.is_deleted == False,
            DieselLoad.chofer_id != None,
        )
    )
    if fecha_desde:
        query = query.where(DieselLoad.fecha_carga >= datetime.combine(fecha_desde, datetime.min.time()))
    if fecha_hasta:
        query = query.where(DieselLoad.fecha_carga <= datetime.combine(fecha_hasta, datetime.max.time()))

    result = await db.execute(query)
    loads = result.scalars().all()

    # Group by driver
    by_driver: dict = {}
    for load in loads:
        did = load.chofer_id
        if did not in by_driver:
            by_driver[did] = []
        by_driver[did].append(load)

    rankings = []
    for did, dloads in by_driver.items():
        driver = await db.get(Driver, did)
        if not driver:
            continue

        total_litros = sum(l.litros_cargados for l in dloads)
        rend_fisico = None

        km_pairs = [
            (l.km_odometro - l.km_anterior, l.litros_cargados)
            for l in dloads
            if l.km_odometro and l.km_anterior and l.km_odometro > l.km_anterior and l.litros_cargados > 0
        ]
        if km_pairs:
            total_km = sum(d for d, _ in km_pairs)
            total_l_km = sum(l for _, l in km_pairs)
            if total_l_km > 0:
                rend_fisico = round(Decimal(total_km) / total_l_km, 2)

        rankings.append({
            "chofer_id": did,
            "chofer_nombre": f"{driver.nombre} {driver.apellidos or ''}".strip(),
            "total_cargas": len(dloads),
            "total_litros": float(total_litros),
            "rendimiento_fisico_promedio": float(rend_fisico) if rend_fisico is not None else None,
        })

    # Sort best-to-worst (None last)
    return sorted(
        rankings,
        key=lambda r: r["rendimiento_fisico_promedio"] if r["rendimiento_fisico_promedio"] is not None else -1,
        reverse=True,
    )


# ==================== TANQUE ====================

@router.get("/tanque", response_model=TankStatusResponse)
async def get_tank_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current diesel tank status."""
    tank = await _get_diesel_tank(db)
    if not tank:
        raise HTTPException(status_code=404, detail="Tanque de diesel no configurado en inventario")

    stock_maximo = tank.stock_maximo or Decimal(40000)
    porcentaje = round((tank.stock_actual / stock_maximo) * 100, 1) if stock_maximo > 0 else Decimal(0)

    return TankStatusResponse(
        stock_actual=tank.stock_actual,
        stock_maximo=stock_maximo,
        porcentaje=porcentaje,
        costo_promedio=tank.costo_promedio,
        valor_total=tank.stock_actual * tank.costo_promedio,
        inventory_item_id=tank.id,
    )


@router.post("/tanque/entrada", response_model=TankStatusResponse, status_code=201)
async def register_tank_entry(
    data: TankEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Register a diesel tank refill (entrada al tanque del patio)."""
    tank = await _get_diesel_tank(db)
    if not tank:
        raise HTTPException(status_code=404, detail="Tanque de diesel no configurado en inventario")

    # Update weighted average cost
    prev_stock = tank.stock_actual
    prev_cost = tank.costo_promedio
    new_stock = prev_stock + data.litros
    if new_stock > 0:
        tank.costo_promedio = round(
            (prev_stock * prev_cost + data.litros * data.costo_por_litro) / new_stock, 2
        )
    tank.stock_actual = new_stock
    tank.ultimo_costo = data.costo_por_litro

    # Create inventory movement
    movement = InventoryMovement(
        numero=f"DIESEL-IN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        inventory_item_id=tank.id,
        tipo=MovementType.ENTRADA,
        razon=MovementReason.COMPRA,
        cantidad=data.litros,
        fecha_movimiento=data.fecha,
        costo_unitario=data.costo_por_litro,
        stock_resultante=new_stock,
        referencia=data.referencia,
        usuario_id=current_user.id,
    )
    db.add(movement)
    await db.commit()
    await db.refresh(tank)

    stock_maximo = tank.stock_maximo or Decimal(40000)
    porcentaje = round((tank.stock_actual / stock_maximo) * 100, 1) if stock_maximo > 0 else Decimal(0)

    return TankStatusResponse(
        stock_actual=tank.stock_actual,
        stock_maximo=stock_maximo,
        porcentaje=porcentaje,
        costo_promedio=tank.costo_promedio,
        valor_total=tank.stock_actual * tank.costo_promedio,
        inventory_item_id=tank.id,
    )
