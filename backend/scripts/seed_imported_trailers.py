import asyncio
import sys
import os
import pandas as pd
from sqlalchemy import select

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import AsyncSessionLocal
from src.models.fleet import Trailer, UnitStatus, TrailerType

async def import_trailers():
    print("🚛 Importing Trailers from remolques.ods...")
    
    # Read file
    try:
        df = pd.read_excel('/app/remolques.ods', engine='odf')
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    # Normalize column names
    df.columns = [c.strip().upper() for c in df.columns]
    
    # Expected columns: ['UNIDAD', 'MARCA', 'TIPO', 'ECO', 'AÑO', 'PLACAS', 'NIV']
    
    async with AsyncSessionLocal() as session:
        count = 0
        generated_eco_seq = 1
        
        for _, row in df.iterrows():
            # Handle ECO
            eco_val = row['ECO']
            raw_eco = "S/N"
            
            if pd.notna(eco_val):
                try:
                    # Try to parse as int/float and format to 3 digits
                    eco_int = int(float(eco_val))
                    raw_eco = f"{eco_int:03d}"
                except ValueError:
                    # Keep as string but strip
                    s_val = str(eco_val).strip().upper()
                    if s_val not in ["NAN", "NONE", ""]:
                         raw_eco = s_val
                    else:
                         raw_eco = "S/N"
            
            if raw_eco == "S/N":
                # Generate ECO: R-001, R-002...
                # Check if exists to avoid collision
                while True:
                    eco = f"R-{generated_eco_seq:03d}"
                    existing = await session.execute(select(Trailer).where(Trailer.numero_economico == eco))
                    if not existing.scalar_one_or_none():
                        break
                    generated_eco_seq += 1
                generated_eco_seq += 1
            else:
                eco = raw_eco
                # Check duplication
                existing = await session.execute(select(Trailer).where(Trailer.numero_economico == eco))
                if existing.scalar_one_or_none():
                    print(f"  ⏭️  Trailer {eco} already exists")
                    continue

            brand_name = str(row['MARCA']).strip().title() if pd.notna(row['MARCA']) else "Generica"
            
            # 2. Map Type (UNIDAD column seems to be the type description)
            # We need to map string to Enum keys
            raw_type = str(row['UNIDAD']).strip().upper() if pd.notna(row['UNIDAD']) else "PLATAFORMA"
            
            # Simple heuristic mapping
            if "CAJA" in raw_type or "SECA" in raw_type:
                trailer_type = TrailerType.CAJA_SECA
            elif "REFRI" in raw_type:
                trailer_type = TrailerType.REFRIGERADO
            elif "TANQUE" in raw_type or "PIPA" in raw_type:
                trailer_type = TrailerType.TANQUE
            elif "DOLLY" in raw_type:
                trailer_type = TrailerType.DOLLY
            else:
                trailer_type = TrailerType.PLATAFORMA # Fallback
            
            # 3. Handle Length (TIPO column seems to be length in feet, e.g. 40, 53)
            largo_meters = None
            if pd.notna(row['TIPO']):
                try:
                    feet = float(row['TIPO'])
                    largo_meters = round(feet * 0.3048, 2)
                except ValueError:
                    pass

            # 4. Create Trailer
            vin = str(row['NIV']).strip() if pd.notna(row['NIV']) else f"SIN-VIN-{eco}"
            placas = str(row['PLACAS']).strip() if pd.notna(row['PLACAS']) else f"TEMP-{eco}"
            anio = int(row['AÑO']) if pd.notna(row['AÑO']) else 2020

            trailer = Trailer(
                numero_economico=eco,
                marca=brand_name,
                tipo=trailer_type,
                anio=anio,
                placas=placas,
                numero_serie=vin,
                largo_metros=largo_meters,
                estatus=UnitStatus.DISPONIBLE
            )
            session.add(trailer)
            count += 1
            print(f"  ✅ Imported {eco} ({brand_name} {trailer_type.value})")

        await session.commit()
        print(f"✨ Successfully imported {count} trailers.")

if __name__ == "__main__":
    asyncio.run(import_trailers())
