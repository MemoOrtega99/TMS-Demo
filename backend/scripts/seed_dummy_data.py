"""
Script para generar datos de prueba masivos (dummy data) para Soluciones-TMS.
Pobla: Remolques, Dollies, Inventario, y simula algunas Cargas de Diesel extra para dar contexto rico a la IA.
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from src.core.database import AsyncSessionLocal
from src.models.fleet import Trailer, Dolly, TrailerType, UnitStatus
from src.models.inventory import InventoryItem, InventoryCategory, InventoryMovement, MovementType, MovementReason
from src.models.trips import DieselLoad
from src.models.catalogs import Supplier, Driver
from src.models.fleet import Vehicle

async def seed_fleet_extended(session):
    print("🚛 Generando Remolques y Dollies...")
    
    # Remolques (12 equipos)
    trailers_data = [
        ("REM-101", TrailerType.CAJA_SECA, "Great Dane", "2022", 30.5),
        ("REM-102", TrailerType.CAJA_SECA, "Utility", "2023", 30.0),
        ("REM-103", TrailerType.CAJA_SECA, "Wabash", "2021", 28.5),
        ("REM-104", TrailerType.PLATAFORMA, "Lozano", "2020", 35.0),
        ("REM-105", TrailerType.PLATAFORMA, "Lozano", "2020", 35.0),
        ("REM-106", TrailerType.REFRIGERADO, "Utility", "2024", 28.0),
        ("REM-107", TrailerType.REFRIGERADO, "Great Dane", "2023", 28.0),
        ("REM-108", TrailerType.TANQUE, "Retesa", "2022", 40.0),
        ("REM-109", TrailerType.TANQUE, "Retesa", "2022", 40.0),
        ("REM-110", TrailerType.CAJA_SECA, "Hyundai", "2021", 29.0),
        ("REM-111", TrailerType.PLATAFORMA, "Fontaine", "2019", 35.0),
        ("REM-112", TrailerType.REFRIGERADO, "Utility", "2024", 28.0),
    ]

    for eco, tipo, marca, anio, cap in trailers_data:
        res = await session.execute(select(Trailer).where(Trailer.numero_economico == eco))
        if not res.scalar_one_or_none():
            t = Trailer(
                numero_economico=eco,
                tipo=tipo,
                marca=marca,
                anio=int(anio),
                capacidad_carga_ton=Decimal(str(cap)),
                estatus=random.choice(list(UnitStatus))
            )
            session.add(t)

    # Dollies (4 equipos)
    dollies_data = [
        ("DLY-001", "Lozano", "2022"),
        ("DLY-002", "Lozano", "2022"),
        ("DLY-003", "Hendrickson", "2021"),
        ("DLY-004", "Hendrickson", "2023"),
    ]

    for eco, marca, anio in dollies_data:
        res = await session.execute(select(Dolly).where(Dolly.numero_economico == eco))
        if not res.scalar_one_or_none():
            d = Dolly(
                numero_economico=eco,
                marca=marca,
                anio=int(anio),
                estatus=random.choice(list(UnitStatus))
            )
            session.add(d)

async def seed_inventory(session):
    print("📦 Generando Inventario (Refacciones, Llantas, etc)...")
    
    items_data = [
        # codigo, nombre, categoria, stock_actual, stock_min, unidad, costo
        ("REF-001", "Filtro de Aceite Motor Cummins", InventoryCategory.REFACCIONES, 12, 15, "pza", 450.50), # BAJO MINIMO
        ("REF-002", "Filtro de Aire Primario", InventoryCategory.REFACCIONES, 24, 10, "pza", 890.00),
        ("REF-003", "Balata Tambor Trasera", InventoryCategory.REFACCIONES, 4, 8, "juego", 1250.00), # BAJO MINIMO
        ("REF-004", "Bolsa de Aire Suspensión", InventoryCategory.REFACCIONES, 18, 5, "pza", 1850.00),
        ("LLA-001", "Llanta Toda Posición 11R22.5", InventoryCategory.LLANTAS, 45, 20, "pza", 6500.00),
        ("LLA-002", "Llanta Tracción 11R22.5", InventoryCategory.LLANTAS, 15, 24, "pza", 6800.00), # BAJO MINIMO
        ("LUB-001", "Aceite Motor 15W40", InventoryCategory.LUBRICANTES, 450, 200, "litros", 95.00),
        ("LUB-002", "Anticongelante Heavy Duty", InventoryCategory.LUBRICANTES, 180, 100, "litros", 85.00),
        ("LUB-003", "Grasa para Chasis (Cubeta)", InventoryCategory.LUBRICANTES, 3, 5, "cubeta", 1450.00), # BAJO MINIMO
        ("INS-001", "Matraca Tensor de Banda", InventoryCategory.INSUMOS, 12, 5, "pza", 350.00),
        ("HER-001", "Gato Hidráulico 20T", InventoryCategory.HERRAMIENTAS, 4, 2, "pza", 2500.00),
    ]

    for codigo, nombre, cat, actual, min_stock, unidad, costo in items_data:
        res = await session.execute(select(InventoryItem).where(InventoryItem.codigo == codigo))
        if not res.scalar_one_or_none():
            item = InventoryItem(
                codigo=codigo,
                nombre=nombre,
                categoria=cat,
                stock_actual=Decimal(str(actual)),
                stock_minimo=Decimal(str(min_stock)),
                unidad_medida=unidad,
                costo_promedio=Decimal(str(costo)),
                ultimo_costo=Decimal(str(costo))
            )
            session.add(item)


async def seed_diesel(session):
    print("⛽ Generando Cargas de Diesel históricas...")
    
    # Obtener algunos vehículos y choferes
    vehicles_res = await session.execute(select(Vehicle).limit(5))
    vehicles = vehicles_res.scalars().all()
    
    drivers_res = await session.execute(select(Driver).limit(5))
    drivers = drivers_res.scalars().all()

    if not vehicles or not drivers:
        print("⚠️ No hay vehículos o choferes para asignar diesel.")
        return

    for i in range(1, 21): # 20 cargas
        v = random.choice(vehicles)
        d = random.choice(drivers)
        litros = Decimal(str(random.randint(150, 600)))
        costo_l = Decimal(str(random.uniform(22.5, 24.8)))
        
        load = DieselLoad(
            vehicle_id=v.id,
            chofer_id=d.id,
            tipo=random.choice(["patio", "gasolinera"]),
            litros=litros,
            costo_por_litro=costo_l,
            costo_total=litros * costo_l,
            km_odometro=v.km_actual + random.randint(100, 5000),
            fecha_carga=datetime.now() - timedelta(days=random.randint(1, 45))
        )
        session.add(load)


async def main():
    async with AsyncSessionLocal() as session:
        await seed_fleet_extended(session)
        await seed_inventory(session)
        await session.commit()
        
        # El diesel necesita que existan primero vehículos (de otro script)
        # pero corramos de todas formas
        await seed_diesel(session)
        await session.commit()
        
    print("✅ Dummy data masiva insertada con éxito.")

if __name__ == "__main__":
    asyncio.run(main())
