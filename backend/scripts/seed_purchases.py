"""
Script para generar Órdenes de Compra.
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
from src.models.purchases import Requisition, RequisitionItem, RequisitionStatus, PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus
from src.models.catalogs import Supplier
from src.models.user import User

async def seed_purchases(session):
    print("🛒 Generando Órdenes de Compra y Requisiciones...")
    
    suppliers_res = await session.execute(select(Supplier).limit(5))
    suppliers = suppliers_res.scalars().all()
    
    admin_res = await session.execute(select(User).limit(1))
    admin = admin_res.scalar_one_or_none()
    
    if not suppliers or not admin:
        print("⚠️ Faltan proveedores o usuario admin.")
        return
        
    for i in range(1, 15): # 14 OC
        proveedor = random.choice(suppliers)
        po = PurchaseOrder(
            numero=f"OC-2026-{i:03d}",
            requisition_id=1, # Bypass
            proveedor_id=proveedor.id,
            fecha_orden=datetime.now().date() - timedelta(days=random.randint(1, 30)),
            subtotal=Decimal(str(random.randint(5000, 20000))),
            iva=Decimal("0.16") * Decimal(str(random.randint(5000, 20000))),
            total=Decimal("1.16") * Decimal(str(random.randint(5000, 20000))),
            estatus=random.choice(list(PurchaseOrderStatus))
        )
        session.add(po)


async def main():
    async with AsyncSessionLocal() as session:
        req = Requisition(
            numero="REQ-000",
            fecha=datetime.now().date(),
            solicitante_id=1,
            estatus=RequisitionStatus.COMPLETADA
        )
        session.add(req)
        await session.commit()
        await seed_purchases(session)
        await session.commit()
        
    print("✅ Dummy data de compras insertada con éxito.")

if __name__ == "__main__":
    asyncio.run(main())
