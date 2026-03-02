"""
Script para generar Servicios de Mantenimiento de las unidades (Fleet Services).
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
from src.models.fleet import Vehicle, VehicleService, ServiceType

async def seed_services(session):
    print("🔧 Generando Historial de Servicios de Unidades...")
    
    vehicles_res = await session.execute(select(Vehicle))
    vehicles = vehicles_res.scalars().all()
    
    if not vehicles:
        print("⚠️ No hay vehículos registrados.")
        return
        
    proveedores_taller = ["Taller Hermanos García", "Taller Diesel del Norte", "Taller Interno", "Agencia Kenworth"]

    for v in vehicles:
        # 1 a 3 servicios por unidad
        num_servicios = random.randint(1, 3)
        km_actual = v.km_actual or 120000
        
        for _ in range(num_servicios):
            km_servicio = km_actual - random.randint(5000, 30000)
            tipo = random.choice(list(ServiceType))
            fecha = datetime.now().date() - timedelta(days=random.randint(10, 180))
            
            # Próximo servicio (para uno de ellos que esté pronto)
            prox_km = km_servicio + 15000 if tipo == ServiceType.PREVENTIVO else None
            
            svc = VehicleService(
                vehicle_id=v.id,
                tipo_servicio=tipo,
                descripcion=f"Servicio {tipo.value} general - Cambio de filtros y aceites",
                km_servicio=km_servicio,
                fecha_servicio=fecha,
                costo=Decimal(str(random.randint(1500, 12000))),
                proveedor=random.choice(proveedores_taller),
                proximo_servicio_km=prox_km
            )
            session.add(svc)


async def main():
    async with AsyncSessionLocal() as session:
        await seed_services(session)
        await session.commit()
    print("✅ Dummy data de mantenimientos insertada con éxito.")

if __name__ == "__main__":
    asyncio.run(main())
