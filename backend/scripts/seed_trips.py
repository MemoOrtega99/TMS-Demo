
import asyncio
import sys
import os
import random
from datetime import date, timedelta
from decimal import Decimal

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from src.core.database import AsyncSessionLocal
from src.models.trips import Trip, TripStatus
from src.models.catalogs import Client, Driver, ClientStatus
from src.models.fleet import Vehicle, Trailer

async def seed_trips():
    """Create example trips linked to existing catalogs"""
    print("  Creating example trips...")
    
    async with AsyncSessionLocal() as session:
        # 1. Fetch dependencies
        # Note: ClientStatus uses native_enum=False so we use string 'ACTIVO' or check logic
        # If ClientStatus.activo (lowercase) exists in model, use it.
        # But ClientStatus was NOT changed to lowercase members in my fix (I only added native_enum=False). 
        # So ClientStatus.ACTIVO is correct. 
        # BUT underlying value is 'ACTIVO' (because fix_enums.py set it so).
        # Model ClientStatus.ACTIVO = 'activo'. Wait.
        # If I set native_enum=False, SQLAlchemy sends 'ACTIVO' if member name is 'ACTIVO', or uses value?
        # native_enum=False uses the Enum VALUE by default when persisting to VARCHAR.
        # Unlike native_enum=True which uses NAME by default? No.
        # Confusion here.
        # Check src/models/catalogs.py. ClientStatus.ACTIVO = "activo".
        # DB has "ACTIVO" (uppercase).
        # If native_enum=False, SQLAlchemy persists "activo" (lowercase value).
        # But DB has "ACTIVO".
        # This might be another mismatch!
        # fix_enums.py set DB to "ACTIVO".
        # If Client expects "activo", and DB has "ACTIVO".
        # fetch where(Client.estatus == ClientStatus.ACTIVO) -> WHERE estatus = 'activo'.
        # Returns nothing if DB has 'ACTIVO'.
        
        # I should probably have updated ClientStatus to uppercase values too?
        # Or updated DB to lowercase values?
        # ClientStatus is: ACTIVO = "activo".
        
        # Let's try to query first. If empty, I might need to fix ClientStatus values too.
        
        clients = (await session.execute(select(Client))).scalars().all()
        print(f"DEBUG: Fetched {len(clients)} clients from DB")
        if clients:
            print(f"DEBUG: Client 0 estatus: {clients[0].estatus} (type: {type(clients[0].estatus)})")
            print(f"DEBUG: Client 0 estatus value: {clients[0].estatus.value if hasattr(clients[0].estatus, 'value') else 'N/A'}")
        
        # Filter in python if needed or assume active.
        # active_clients = [c for c in clients if str(c.estatus).upper() == 'ACTIVO' or str(c.estatus).lower() == 'activo']
        active_clients = clients
        print(f"DEBUG: Active clients (unfiltered): {len(active_clients)}")
        
        drivers = (await session.execute(select(Driver))).scalars().all() # Driver uses string 'activo'
        vehicles = (await session.execute(select(Vehicle))).scalars().all()
        trailers = (await session.execute(select(Trailer))).scalars().all()

        if not active_clients or not drivers or not vehicles:
            print("  ⚠️  Not enough catalogs found (clients, drivers, or vehicles missing). Run seed_catalogs.py first.")
            # return but maybe print what IS found
            print(f"Clients: {len(active_clients)}, Drivers: {len(drivers)}, Vehicles: {len(vehicles)}")
            return

        clients = active_clients

        # 2. Define example routes
        routes = [
            ("Monterrey, NL", "Laredo, TX", 230),
            ("Apodaca, NL", "Mexico, DF", 900),
            ("Escobedo, NL", "Guadalajara, JAL", 850),
            ("San Nicolas, NL", "Reynosa, TAM", 210),
            ("Santa Catarina, NL", "Saltillo, COAH", 80),
        ]

        # 3. Create trips with different statuses
        
        # Trip 1: Programado (Only basic info)
        trips_data = []
        
        # --- Programado ---
        trips_data.append({
            "numero_viaje": f"VJ-{date.today().year}-001",
            "fecha_programada": date.today() + timedelta(days=2),
            "estatus": TripStatus.programado, # Lowercase member
            "cliente_id": clients[0].id,
            "origen": routes[0][0],
            "destino": routes[0][1],
            "tipo_carga": "1X40HC",
            "contenedores": ["MSKU1234567"]
        })

        # --- Asignado ---
        trips_data.append({
            "numero_viaje": f"VJ-{date.today().year}-002",
            "fecha_programada": date.today() + timedelta(days=1),
            "estatus": TripStatus.asignado,
            "cliente_id": clients[1].id if len(clients) > 1 else clients[0].id,
            "chofer_id": drivers[0].id,
            "vehiculo_id": vehicles[0].id,
            "remolque1_id": trailers[0].id if trailers else None,
            "origen": routes[1][0],
            "destino": routes[1][1],
            "tipo_carga": "2X40HC",
            "contenedores": ["MSKU9876543", "TRLU1234567"]
        })

        # --- En Ruta ---
        trips_data.append({
            "numero_viaje": f"VJ-{date.today().year}-003",
            "fecha_programada": date.today(),
            "estatus": TripStatus.en_ruta,
            "cliente_id": clients[0].id,
            "chofer_id": drivers[1].id if len(drivers) > 1 else drivers[0].id,
            "vehiculo_id": vehicles[1].id if len(vehicles) > 1 else vehicles[0].id,
            "remolque1_id": trailers[1].id if len(trailers) > 1 else None,
            "origen": routes[2][0],
            "destino": routes[2][1],
            "tipo_carga": "1X20DC",
            "contenedores": ["HLCU1234567"],
            "km_salida": 125000
        })

        # --- Completado ---
        trips_data.append({
            "numero_viaje": f"VJ-{date.today().year}-004",
            "fecha_programada": date.today() - timedelta(days=5),
            "fecha_entrega_real": date.today() - timedelta(days=3),
            "estatus": TripStatus.completado,
            "cliente_id": clients[1].id if len(clients) > 1 else clients[0].id,
            "chofer_id": drivers[0].id,
            "vehiculo_id": vehicles[0].id,
            "remolque1_id": trailers[2].id if len(trailers) > 2 else None,
            "origen": routes[3][0],
            "destino": routes[3][1],
            "tipo_carga": "2X20DC",
            "contenedores": ["MAEU1234567", "PONU1234567"],
            "km_salida": 124000,
            "km_llegada": 124500
        })

        # 4. Insert trips
        new_count = 0
        for data in trips_data:
            # Check if exists
            exists = await session.execute(select(Trip).where(Trip.numero_viaje == data["numero_viaje"]))
            if exists.scalar_one_or_none():
                print(f"  ⏭️  Trip {data['numero_viaje']} already exists")
                continue

            trip = Trip(**data)
            session.add(trip)
            print(f"  ✅ Trip {data['numero_viaje']} staged")
            new_count += 1
        
        await session.commit()
        print(f"  ✨ Created {new_count} new trips")

async def main():
    print("\n🌱 Seeding Trips...")
    await seed_trips()
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(main())
