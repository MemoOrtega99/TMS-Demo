# -*- coding: utf-8 -*-
import asyncio
from sqlalchemy import text
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.database import AsyncSessionLocal

async def seed():
    async with AsyncSessionLocal() as session:
        # Clientes
        clients_sql = [
            """INSERT INTO clients (nombre, rfc, direccion, telefono, email, contacto_nombre, dias_credito, limite_credito, estatus, created_at, updated_at) 
               VALUES ('Distribuidora Nacional S.A. de C.V.', 'DNA201201AB1', 'Av. Constitucion 1500, Centro, Monterrey, N.L.', '8183001500', 'contacto@disnac.com.mx', 'Maria Gonzalez', 30, 500000.00, 'ACTIVO', NOW(), NOW())""",
            """INSERT INTO clients (nombre, rfc, direccion, telefono, email, contacto_nombre, dias_credito, limite_credito, estatus, created_at, updated_at) 
               VALUES ('Importaciones del Norte S.A. de C.V.', 'INO150615CD2', 'Blvd. Diaz Ordaz 100, Santa Maria, Monterrey, N.L.', '8184002000', 'ventas@imponorte.com', 'Carlos Mendoza', 15, 300000.00, 'ACTIVO', NOW(), NOW())""",
            """INSERT INTO clients (nombre, rfc, direccion, telefono, email, contacto_nombre, dias_credito, limite_credito, estatus, created_at, updated_at) 
               VALUES ('Logistica Integral Azteca S.A. de C.V.', 'LIA180901EF3', 'Carr. Colombia Km 15, Apodaca, N.L.', '8186003000', 'operaciones@lialogistics.mx', 'Ana Lucia Torres', 45, 750000.00, 'ACTIVO', NOW(), NOW())""",
        ]
        
        for sql in clients_sql:
            await session.execute(text(sql))
            print('Cliente creado')
        
        # Proveedores
        suppliers_sql = [
            """INSERT INTO suppliers (nombre, rfc, tipo, direccion, telefono, email, contacto_nombre, estatus, created_at, updated_at) 
               VALUES ('Combustibles del Valle S.A. de C.V.', 'CVA100301GH1', 'COMBUSTIBLE', 'Carr. Miguel Aleman Km 20, Guadalupe, N.L.', '8185001000', 'ventas@combuvalle.com', 'Fernando Reyes', 'ACTIVO', NOW(), NOW())""",
            """INSERT INTO suppliers (nombre, rfc, tipo, direccion, telefono, email, contacto_nombre, estatus, created_at, updated_at) 
               VALUES ('Refacciones y Servicios Profesionales S.A. de C.V.', 'RSP120815IJ2', 'REFACCIONES', 'Av. Ruiz Cortines 2500, San Nicolas, N.L.', '8186002000', 'ventas@refacpro.mx', 'Luis Garza', 'ACTIVO', NOW(), NOW())""",
            """INSERT INTO suppliers (nombre, rfc, tipo, direccion, telefono, email, contacto_nombre, estatus, created_at, updated_at) 
               VALUES ('Taller Mecanico Especializado S.A. de C.V.', 'TME140220KL3', 'SERVICIOS', 'Calle Industrial 500, Apodaca, N.L.', '8187003000', 'servicio@tallerme.com', 'Miguel Angel Perez', 'ACTIVO', NOW(), NOW())""",
        ]
        
        for sql in suppliers_sql:
            await session.execute(text(sql))
            print('Proveedor creado')
        
        await session.commit()
        print('Completado!')

if __name__ == "__main__":
    asyncio.run(seed())
