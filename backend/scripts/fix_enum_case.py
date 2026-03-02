#!/usr/bin/env python3
"""
Script para corregir los valores de enums en la base de datos.
Convierte todos los valores de MAYUSCULAS a minusculas para que coincidan
con los schemas de Pydantic y el frontend.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from src.core.database import AsyncSessionLocal


# Mapeo de valores: tabla.columna -> {VALOR_VIEJO: valor_nuevo}
ENUM_MAPPINGS = {
    "drivers.estatus": {
        "ACTIVO": "activo",
        "INACTIVO": "inactivo",
        "VACACIONES": "vacaciones",
    },
    "vehicles.estatus": {
        "DISPONIBLE": "disponible",
        "EN_RUTA": "en_ruta",
        "TALLER": "taller",
        "BAJA": "baja",
    },
    "trailers.tipo": {
        "CAJA_SECA": "caja_seca",
        "PLATAFORMA": "plataforma",
        "REFRIGERADO": "refrigerado",
        "TANQUE": "tanque",
    },
    "trailers.estatus": {
        "DISPONIBLE": "disponible",
        "EN_USO": "en_uso",
        "TALLER": "taller",
        "BAJA": "baja",
    },
    "clients.estatus": {
        "ACTIVO": "activo",
        "INACTIVO": "inactivo",
        "SUSPENDIDO": "suspendido",
    },
    "suppliers.tipo": {
        "COMBUSTIBLE": "combustible",
        "REFACCIONES": "refacciones",
        "SERVICIOS": "servicios",
        "OTRO": "otro",
    },
    "suppliers.estatus": {
        "ACTIVO": "activo",
        "INACTIVO": "inactivo",
    },
}


async def fix_enum_values():
    """Actualiza todos los valores de enums a minúsculas"""
    async with AsyncSessionLocal() as session:
        print("\n🔧 Iniciando corrección de valores de enums...\n")
        
        total_updates = 0
        
        for table_column, mappings in ENUM_MAPPINGS.items():
            table_name, column_name = table_column.split(".")
            
            print(f"📋 Procesando {table_name}.{column_name}:")
            
            for old_value, new_value in mappings.items():
                # Verificar cuántos registros necesitan actualización
                count_query = text(f"""
                    SELECT COUNT(*) 
                    FROM {table_name} 
                    WHERE {column_name} = :old_value
                """)
                result = await session.execute(count_query, {"old_value": old_value})
                count = result.scalar()
                
                if count > 0:
                    # Actualizar los valores
                    update_query = text(f"""
                        UPDATE {table_name} 
                        SET {column_name} = :new_value 
                        WHERE {column_name} = :old_value
                    """)
                    await session.execute(
                        update_query, 
                        {"old_value": old_value, "new_value": new_value}
                    )
                    print(f"  ✅ Actualizados {count} registros: '{old_value}' → '{new_value}'")
                    total_updates += count
                else:
                    print(f"  ⏭️  Sin cambios para '{old_value}'")
            
            print()
        
        # Commit de todos los cambios
        await session.commit()
        
        print(f"✅ ¡Corrección completada! Total de registros actualizados: {total_updates}\n")


async def verify_fixes():
    """Verifica que los valores se hayan actualizado correctamente"""
    async with AsyncSessionLocal() as session:
        print("\n🔍 Verificando correcciones...\n")
        
        # Verificar algunos valores de muestra
        checks = [
            ("drivers", "estatus"),
            ("vehicles", "estatus"),
            ("trailers", "tipo"),
            ("trailers", "estatus"),
            ("clients", "estatus"),
            ("suppliers", "tipo"),
            ("suppliers", "estatus"),
        ]
        
        for table_name, column_name in checks:
            query = text(f"""
                SELECT DISTINCT {column_name} 
                FROM {table_name} 
                ORDER BY {column_name}
            """)
            result = await session.execute(query)
            values = [row[0] for row in result]
            
            print(f"  {table_name}.{column_name}: {values}")
        
        print("\n✅ Verificación completada!\n")


async def main():
    print("\n" + "="*60)
    print("  CORRECCIÓN DE VALORES DE ENUMS EN BASE DE DATOS")
    print("="*60)
    
    await fix_enum_values()
    await verify_fixes()
    
    print("✨ ¡Proceso finalizado con éxito!\n")


if __name__ == "__main__":
    asyncio.run(main())
