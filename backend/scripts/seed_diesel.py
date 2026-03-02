"""
Script para inicializar el tanque de diesel en inventario.
Crea el InventoryItem de categoría combustible si no existe.

Uso:
    python -m scripts.seed_diesel
    
O como parte del seed completo:
    python -m scripts.seed
"""
import asyncio
import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from src.core.database import AsyncSessionLocal


async def seed_diesel_tank(stock_inicial: Decimal = Decimal("0"), costo_por_litro: Decimal = Decimal("0")):
    """
    Crea el item de inventario del tanque de diesel del patio.
    Usa SQL raw para evitar el bug de SQLAlchemy con enum names (COMBUSTIBLE vs combustible).
    """
    async with AsyncSessionLocal() as session:
        # Verificar si ya existe
        result = await session.execute(
            text("SELECT id, stock_actual FROM inventory_items WHERE codigo = 'DIESEL-TANQUE' AND is_deleted = false LIMIT 1")
        )
        existing = result.fetchone()

        if existing:
            print(f"  ⏭️  Tanque de diesel ya existe (id={existing[0]}, stock actual: {existing[1]} L)")
            return

        # Usar SQL raw para evitar que SQLAlchemy convierta el enum al nombre en mayúsculas
        await session.execute(text("""
            INSERT INTO inventory_items (
                codigo, nombre, descripcion, categoria, unidad_medida,
                stock_actual, stock_minimo, stock_maximo,
                ubicacion, costo_promedio, ultimo_costo,
                created_at, updated_at, is_deleted, tags
            ) VALUES (
                'DIESEL-TANQUE',
                'Tanque Diesel Patio',
                'Tanque principal de diesel del patio. Capacidad: 40,000 litros.',
                'combustible',
                'litros',
                :stock_actual, :stock_minimo, :stock_maximo,
                'Patio principal',
                :costo_promedio, :ultimo_costo,
                now(), now(), false, '[]'
            )
        """), {
            "stock_actual": float(stock_inicial),
            "stock_minimo": 5000.0,
            "stock_maximo": 40000.0,
            "costo_promedio": float(costo_por_litro),
            "ultimo_costo": float(costo_por_litro),
        })
        await session.commit()

        print(f"  ✅ Tanque de diesel creado:")
        print(f"     Código: DIESEL-TANQUE")
        print(f"     Capacidad: 40,000 litros")
        print(f"     Stock mínimo (alerta): 5,000 litros")
        print(f"     Stock inicial: {stock_inicial} litros")
        print(f"     ⚠️  Actualiza el stock actual con una entrada al tanque si ya tienes diesel")


async def main():
    print("\n🛢️  Inicializando tanque de diesel...")
    await seed_diesel_tank()
    print("\n✨ Listo!\n")


if __name__ == "__main__":
    asyncio.run(main())
