
import asyncio
from sqlalchemy import select
from src.core.database import AsyncSessionLocal
from src.models.vehicle_catalogs import VehicleBrand, VehicleModel, VehicleType
from src.api.v1.schemas.catalogs import VehicleBrandCreate, VehicleModelCreate, VehicleTypeCreate

async def test_catalogs():
    async with AsyncSessionLocal() as db:
        print("Testing VehicleBrand creation with Title Case...")
        # Test Title Case
        brand_data = VehicleBrandCreate(nombre="kenworth")
        print(f"Input: 'kenworth', Validated: '{brand_data.nombre}'")
        
        # Check if exists
        existing = await db.execute(select(VehicleBrand).where(VehicleBrand.nombre == brand_data.nombre))
        if not existing.scalar_one_or_none():
            brand = VehicleBrand(nombre=brand_data.nombre)
            db.add(brand)
            await db.commit()
            await db.refresh(brand)
            print(f"Created Brand: {brand.id} - {brand.nombre}")
        else:
            brand = existing.scalar_one()
            print(f"Brand already exists: {brand.id} - {brand.nombre}")

        print("\nTesting VehicleModel creation...")
        model_data = VehicleModelCreate(nombre="t680", brand_id=brand.id)
        print(f"Input: 't680', Validated: '{model_data.nombre}'")
        
        existing_model = await db.execute(select(VehicleModel).where(VehicleModel.nombre == model_data.nombre))
        if not existing_model.scalar_one_or_none():
            model = VehicleModel(nombre=model_data.nombre, brand_id=brand.id)
            db.add(model)
            await db.commit()
            await db.refresh(model)
            print(f"Created Model: {model.id} - {model.nombre}")
        
        print("\nTesting VehicleType creation...")
        type_data = VehicleTypeCreate(nombre="tractocamión")
        print(f"Input: 'tractocamión', Validated: '{type_data.nombre}'")
        
        existing_type = await db.execute(select(VehicleType).where(VehicleType.nombre == type_data.nombre))
        if not existing_type.scalar_one_or_none():
            vtype = VehicleType(nombre=type_data.nombre)
            db.add(vtype)
            await db.commit()
            await db.refresh(vtype)
            print(f"Created Type: {vtype.id} - {vtype.nombre}")

if __name__ == "__main__":
    asyncio.run(test_catalogs())
