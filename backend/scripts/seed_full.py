
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.seed import main as seed_core
from scripts.seed_catalogs import main as seed_catalogs
from scripts.seed_trips import main as seed_trips
from scripts.seed_diesel import seed_diesel_tank

async def main():
    print("\n🚀 STARTING FULL DATABASE SEED 🚀")
    print("==================================\n")

    print("\n1️⃣  CORE DATA (Roles & Admin)")
    await seed_core()

    print("\n2️⃣  CATALOGS (Clients, Drivers, Vehicles, etc.)")
    await seed_catalogs()

    print("\n3️⃣  TRIPS (Linked to catalogs)")
    await seed_trips()

    print("\n4️⃣  DIESEL TANK (Inventory)")
    await seed_diesel_tank()

    print("\n5️⃣  IMPORTED UNITS (Legacy)")
    from scripts.seed_imported_units import import_units
    await import_units()

    print("\n6️⃣  IMPORTED TRAILERS (Legacy)")
    from scripts.seed_imported_trailers import import_trailers
    await import_trailers()

    print("\n✅ FULL SEED COMPLETED SUCCESSFULLY! ✅\n")

if __name__ == "__main__":
    asyncio.run(main())
