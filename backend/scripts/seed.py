"""
Script para crear datos iniciales (seed).
Ejecutar después de las migraciones.

Uso:
    python -m scripts.seed
"""
import asyncio
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from src.core.database import AsyncSessionLocal
from src.core.security import get_password_hash
from src.models import User, Role, DEFAULT_ROLES
from src.models.inventory import InventoryItem, InventoryCategory


async def seed_roles():
    """Crear roles predefinidos"""
    async with AsyncSessionLocal() as session:
        for role_data in DEFAULT_ROLES:
            # Verificar si ya existe
            result = await session.execute(
                select(Role).where(Role.name == role_data["name"])
            )
            if result.scalar_one_or_none():
                print(f"  ⏭️  Rol '{role_data['name']}' ya existe")
                continue
            
            role = Role(
                name=role_data["name"],
                description=role_data["description"],
                permissions=role_data["permissions"],
            )
            session.add(role)
            print(f"  ✅ Rol '{role_data['name']}' creado")
        
        await session.commit()


async def seed_admin_user():
    """Crear usuario administrador por defecto"""
    async with AsyncSessionLocal() as session:
        # Verificar si ya existe
        result = await session.execute(
            select(User).where(User.email == "admin@admin.com")
        )
        if result.scalar_one_or_none():
            print("  ⏭️  Usuario admin ya existe")
            return
        
        # Obtener rol admin
        result = await session.execute(
            select(Role).where(Role.name == "admin")
        )
        admin_role = result.scalar_one_or_none()
        
        if not admin_role:
            print("  ❌ Error: Rol 'admin' no encontrado. Ejecuta seed_roles primero.")
            return
        
        admin = User(
            email="admin@admin.com",
            password_hash=get_password_hash("admin123"),  # ⚠️ Cambiar en producción
            name="Administrador",
            role_id=admin_role.id,
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        
        print("  ✅ Usuario admin creado:")
        print("     Email: admin@admin.com")
        print("     Password: admin123")
        print("     ⚠️  CAMBIAR PASSWORD EN PRODUCCIÓN")


async def main():
    print("\n🌱 Iniciando seed de datos...")
    print("\n📋 Creando roles:")
    await seed_roles()
    
    print("\n👤 Creando usuario admin:")
    await seed_admin_user()

    print("\n🛢️  Inicializando tanque de diesel:")
    from scripts.seed_diesel import seed_diesel_tank
    await seed_diesel_tank()
    
    print("\n✨ Seed completado!\n")


if __name__ == "__main__":
    asyncio.run(main())
