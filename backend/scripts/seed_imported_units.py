import asyncio
import sys
import os
import pandas as pd
from sqlalchemy import select

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import AsyncSessionLocal
from src.models.fleet import Vehicle, VehicleStatus

async def import_units():
    print("🚗 Importing Units from unidades.ods...")
    
    # Read file
    try:
        df = pd.read_excel('/app/unidades.ods', engine='odf')
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    # Normalize column names just in case
    df.columns = [c.strip().upper() for c in df.columns]
    
    # Expected columns: ['UNIDAD', 'MARCA', 'MODELO', 'ECO', 'AÑO', 'PLACAS', 'NIV']
    
    async with AsyncSessionLocal() as session:
        count = 0
        for _, row in df.iterrows():
            eco_val = row['ECO']
            if pd.isna(eco_val):
                continue
                
            # Normalize to 3 digits: 1.0 -> 001, 93 -> 093
            try:
                # Convert to float first to handle "1.0", then int, then string
                eco_int = int(float(eco_val))
                eco = f"{eco_int:03d}"
            except ValueError:
                # If it's a non-numeric string, keep it but strip
                eco = str(eco_val).strip()
            
            # Skip if ECO is invalid
            if not eco or eco == 'nan':
                continue
                
            # Check if exists
            existing = await session.execute(select(Vehicle).where(Vehicle.numero_economico == eco))
            if existing.scalar_one_or_none():
                print(f"  ⏭️  Unit {eco} already exists")
                continue

            vin = str(row['NIV']).strip() if pd.notna(row['NIV']) else f"SIN-VIN-{eco}"
            placas = str(row['PLACAS']).strip() if pd.notna(row['PLACAS']) else None
            anio_val = int(row['AÑO']) if pd.notna(row['AÑO']) else 2020
            
            brand_name = str(row['MARCA']).strip().title() if pd.notna(row['MARCA']) else "Desconocida"
            model_name = str(row['MODELO']).strip() if pd.notna(row['MODELO']) else "Generico"

            vehicle = Vehicle(
                numero_economico=eco,
                marca=brand_name,
                modelo=model_name,
                anio=anio_val,
                placas=placas,
                numero_serie=vin,
                estatus=VehicleStatus.DISPONIBLE
            )
            session.add(vehicle)
            count += 1
            print(f"  ✅ Imported {eco} ({brand_name} {model_name})")

        await session.commit()
        print(f"✨ Successfully imported {count} units.")

if __name__ == "__main__":
    asyncio.run(import_units())
