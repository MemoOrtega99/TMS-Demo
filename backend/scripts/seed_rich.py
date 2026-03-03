
import asyncio
import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func
from src.core.database import AsyncSessionLocal
from src.models.trips import Trip, TripStatus
from src.models.catalogs import Driver, Client, DriverStatus
from src.models.fleet import Vehicle

async def seed_rich_data():
    print("\n🚀 STARTING RICH DATA SEED 🚀")
    print("==================================\n")

    async with AsyncSessionLocal() as session:
        # 1. Ensure we have drivers
        drivers_q = await session.execute(select(Driver))
        drivers = drivers_q.scalars().all()
        
        if len(drivers) < 3:
            print("  👨‍✈️ Creating more drivers...")
            new_drivers = [
                Driver(nombre="Juan", apellido="Pérez", telefono="555-101", estatus=DriverStatus.ACTIVO),
                Driver(nombre="Pedro", apellido="Rodríguez", telefono="555-102", estatus=DriverStatus.ACTIVO),
                Driver(nombre="Mariana", apellido="Sosa", telefono="555-103", estatus=DriverStatus.ACTIVO),
            ]
            for d in new_drivers:
                session.add(d)
            await session.commit()
            drivers = (await session.execute(select(Driver))).scalars().all()

        # 2. Ensure we have clients
        clients_q = await session.execute(select(Client))
        clients = clients_q.scalars().all()
        if not clients:
            print("  ⚠️ No clients found. Please run seed_full.py first.")
            return

        # 3. Create many completed trips to show performance
        print("  🚚 Creating trip history for performance analysis...")
        
        # Distribution: Juan (5), Pedro (3), Mariana (1)
        trip_counts = {drivers[0].id: 8, drivers[1].id: 3, drivers[2].id: 1}
        
        base_date = date.today() - timedelta(days=60)
        trip_idx = 500
        
        added_trips = 0
        for driver_id, count in trip_counts.items():
            for i in range(count):
                trip_no = f"VJ-HIST-{trip_idx}"
                trip_idx += 1
                
                # Check if exists
                exists = await session.scalar(select(Trip).where(Trip.numero_viaje == trip_no))
                if exists: continue
                
                t = Trip(
                    numero_viaje=trip_no,
                    chofer_id=driver_id,
                    cliente_id=clients[0].id,
                    origen="CDMX",
                    destino="Monterrey",
                    tarifa_cliente=Decimal("15000.00"),
                    estatus=TripStatus.completado,
                    fecha_programada=base_date + timedelta(days=i*2),
                    fecha_entrega_real=datetime.now() - timedelta(days=2)
                )
                session.add(t)
                added_trips += 1
        
        # 4. Diesel Performance Data
        print("  ⛽ Seeding diesel loads for performance analysis...")
        vehicles_q = await session.execute(select(Vehicle))
        vehicles = vehicles_q.scalars().all()
        
        if vehicles:
            for v in vehicles:
                # Add a few loads
                load1 = DieselLoad(
                    vehicle_id=v.id,
                    litros=400,
                    costo_total=Decimal("9600.00"),
                    km_odometro=50000,
                    fecha_carga=datetime.now() - timedelta(days=10),
                    tipo=DieselLoadType.patio
                )
                load2 = DieselLoad(
                    vehicle_id=v.id,
                    litros=350,
                    costo_total=Decimal("8400.00"),
                    km_odometro=51500, # 1500km / 350L = ~4.2 km/L
                    fecha_carga=datetime.now() - timedelta(days=5),
                    tipo=DieselLoadType.gasolinera
                )
                session.add_all([load1, load2])

        # 5. February Data Summary
        print("  📅 Seeding February trips for monthly summary...")
        feb_start = date(2026, 2, 1)
        for i in range(10):
            trip_no = f"VJ-FEB-{i+1:03d}"
            exists = await session.scalar(select(Trip).where(Trip.numero_viaje == trip_no))
            if exists: continue
            
            # Mix of profitability
            tarifa = Decimal("20000.00") if i % 2 == 0 else Decimal("12000.00")
            
            t = Trip(
                numero_viaje=trip_no,
                chofer_id=drivers[i % len(drivers)].id,
                cliente_id=clients[0].id,
                origen="Queretaro",
                destino="Nuevo Laredo",
                tarifa_cliente=tarifa,
                estatus=TripStatus.completado,
                fecha_programada=feb_start + timedelta(days=i*2),
                fecha_entrega_real=datetime(2026, 2, 2) + timedelta(days=i*2)
            )
            session.add(t)
            
            # Add some expenses to check profitability
            exp = TripExpense(
                trip_id=t.id,
                tipo_gasto=ExpenseType.combustible,
                monto=Decimal("8000.00"),
                fecha_gasto=feb_start + timedelta(days=i*2)
            )
            session.add(exp)

        await session.commit()
        print(f"  ✅ Added diesel loads and February history.")

    print("\n✅ RICH SEED COMPLETED SUCCESSFULLY! ✅\n")

if __name__ == "__main__":
    from src.models.trips import DieselLoad, DieselLoadType, TripExpense, ExpenseType
    asyncio.run(seed_rich_data())
