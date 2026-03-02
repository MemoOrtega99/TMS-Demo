import asyncio
import sys
import os
from sqlalchemy import text, select

# Agregar src al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import AsyncSessionLocal
from src.models import User, Role

async def cleanup_database():
    """
    Limpia todas las tablas excepto roles y el usuario administrador inicial.
    """
    async with AsyncSessionLocal() as session:
        print("\n🧹 Iniciando limpieza completa de base de datos...")
        
        try:
            # 1. Verificar que el rol admin existe
            result = await session.execute(select(Role).where(Role.name == "admin"))
            admin_role = result.scalar_one_or_none()
            
            if not admin_role:
                print("⚠️ Advertencia: Rol 'admin' no encontrado. Asegúrate de correr el seed después.")

            # 2. Lista completa de tablas a limpiar (ordenadas por dependencias aproximadas o usando CASCADE)
            # Usamos TRUNCATE ... CASCADE por seguridad.
            tables_to_truncate = [
                "audit_logs", 
                "system_events", 
                "diesel_loads",
                "trip_expenses",
                "trips",
                "vehicles", 
                "trailers",
                "drivers", 
                "payments",
                "invoices",
                "purchase_order_items",
                "purchase_orders",
                "requisition_items",
                "requisitions",
                "inventory_movements",
                "inventory_items",
                "clients", 
                "suppliers",
                "vehicle_models",
                "vehicle_brands",
                "vehicle_types",
                "trailer_brands"
            ]
            
            print(f"📦 Eliminando datos de {len(tables_to_truncate)} tablas...")
            for table in tables_to_truncate:
                try:
                    await session.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
                    print(f"  ✅ {table} limpia.")
                except Exception as e:
                    print(f"  ⚠️ Error limpiando {table} (podría no existir): {e}")
            
            # 3. Limpiar usuarios excepto admin
            print("👤 Limpiando usuarios (excepto admin@gestion-rb.com)...")
            # Primero quitamos roles de otros usuarios si fuera necesario, 
            # pero TRUNCATE/DELETE suele ser suficiente si no hay FKs estrictas en sentido opuesto.
            await session.execute(
                text("DELETE FROM users WHERE email != 'admin@gestion-rb.com'")
            )
            
            # 4. Asegurar que el admin tiene el rol correcto si existe
            if admin_role:
                admin_result = await session.execute(select(User).where(User.email == "admin@gestion-rb.com"))
                admin_user = admin_result.scalar_one_or_none()
                if admin_user:
                    admin_user.role_id = admin_role.id
                    print("👑 Rol de admin verificado.")

            await session.commit()
            print("\n✅ Base de datos limpia exitosamente.")
            print("✨ Solo se conservó el usuario admin@gestion-rb.com y los roles.")
            print("💡 Si el admin no existía, ejecuta: docker compose exec backend python scripts/seed.py")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error durante la limpieza: {e}")

if __name__ == "__main__":
    asyncio.run(cleanup_database())
