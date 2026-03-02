# -*- coding: utf-8 -*-
import asyncio
from sqlalchemy import text
import sys, os
sys.path.insert(0, '/app')
from src.core.database import AsyncSessionLocal

async def fix():
    async with AsyncSessionLocal() as session:
        # Corregir suppliers
        await session.execute(text("UPDATE suppliers SET tipo = 'COMBUSTIBLE' WHERE tipo = 'combustible'"))
        await session.execute(text("UPDATE suppliers SET tipo = 'REFACCIONES' WHERE tipo = 'refacciones'"))
        await session.execute(text("UPDATE suppliers SET tipo = 'SERVICIOS' WHERE tipo = 'servicios'"))
        await session.execute(text("UPDATE suppliers SET estatus = 'ACTIVO' WHERE estatus = 'activo'"))
        
        # Corregir clients
        await session.execute(text("UPDATE clients SET estatus = 'ACTIVO' WHERE estatus = 'activo'"))
        
        # Corregir vehicles
        await session.execute(text("UPDATE vehicles SET estatus = 'DISPONIBLE' WHERE estatus = 'disponible'"))
        await session.execute(text("UPDATE vehicles SET estatus = 'EN_RUTA' WHERE estatus = 'en_ruta'"))
        
        # Corregir trailers
        await session.execute(text("UPDATE trailers SET tipo = 'CAJA_SECA' WHERE tipo = 'caja_seca'"))
        await session.execute(text("UPDATE trailers SET tipo = 'PLATAFORMA' WHERE tipo = 'plataforma'"))
        await session.execute(text("UPDATE trailers SET tipo = 'REFRIGERADO' WHERE tipo = 'refrigerado'"))
        await session.execute(text("UPDATE trailers SET estatus = 'DISPONIBLE' WHERE estatus = 'disponible'"))
        await session.execute(text("UPDATE trailers SET estatus = 'EN_USO' WHERE estatus = 'en_uso'"))
        
        await session.commit()
        print('Datos corregidos!')

if __name__ == "__main__":
    asyncio.run(fix())
