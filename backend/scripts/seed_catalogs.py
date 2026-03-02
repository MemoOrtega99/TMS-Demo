# -*- coding: utf-8 -*-
"""
Script para crear datos de ejemplo en catalogos.
Crea 3 registros de cada catalogo.
"""
import asyncio
import sys
import os
from datetime import date, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from src.core.database import AsyncSessionLocal
from src.models.catalogs import (
    Driver, Client, Supplier,
    DriverStatus, ClientStatus, SupplierType, SupplierStatus
)
from src.models.fleet import (
    Vehicle, Trailer, VehicleStatus, TrailerType, UnitStatus
)
# Removed vehicle_catalogs import

async def seed_drivers():
    """Crear 3 choferes de ejemplo"""
    drivers_data = [
        {
            "nombre": "Juan Carlos",
            "apellido": "Garcia Lopez",
            "telefono": "8181234567",
            "email": "jgarcia@ejemplo.com",
            "fecha_ingreso": date(2020, 3, 15),
            "estatus": DriverStatus.ACTIVO,
            "salario_base": 15000.00,
            "licencia_numero": "MON123456",
            "licencia_tipo": "Federal",
            "licencia_vigencia": date.today() + timedelta(days=365),
        },
        {
            "nombre": "Pedro",
            "apellido": "Martinez Hernandez",
            "telefono": "8187654321",
            "email": "pmartinez@ejemplo.com",
            "fecha_ingreso": date(2019, 7, 1),
            "estatus": DriverStatus.ACTIVO,
            "salario_base": 16500.00,
            "licencia_numero": "MON789012",
            "licencia_tipo": "Federal",
            "licencia_vigencia": date.today() + timedelta(days=180),
        },
        {
            "nombre": "Roberto",
            "apellido": "Sanchez Ramirez",
            "telefono": "8189876543",
            "email": "rsanchez@ejemplo.com",
            "fecha_ingreso": date(2021, 1, 10),
            "estatus": DriverStatus.ACTIVO,
            "salario_base": 14500.00,
            "licencia_numero": "MON345678",
            "licencia_tipo": "Federal",
            "licencia_vigencia": date.today() + timedelta(days=540),
        },
    ]
    
    async with AsyncSessionLocal() as session:
        for data in drivers_data:
            result = await session.execute(
                select(Driver).where(Driver.email == data["email"])
            )
            if result.scalar_one_or_none():
                print(f"  Ya existe chofer: {data['nombre']}")
                continue
            
            driver = Driver(**data)
            session.add(driver)
            print(f"  Creado chofer: {data['nombre']} {data['apellido']}")
        
        await session.commit()


async def seed_vehicles():
    """Crear 3 vehiculos de ejemplo con sus marcas y modelos"""
    async with AsyncSessionLocal() as session:
        # Verificar si ya existen
        result = await session.execute(select(Vehicle).where(Vehicle.numero_economico == "U-001"))
        if result.scalar_one_or_none():
            print("  Vehiculos ya existen")
            return
        
        # 2. Crear Vehiculos (Dummy data)
        print("  Creando vehiculos de prueba...")
        vehicles = [
            Vehicle(numero_economico="U-001", marca="Kenworth", modelo="T680", anio=2021, placas="987-AA-1", numero_serie="SERIE001", estatus=VehicleStatus.DISPONIBLE),
            Vehicle(numero_economico="U-002", marca="Freightliner", modelo="Cascadia", anio=2023, placas="123-BB-2", numero_serie="SERIE002", estatus=VehicleStatus.DISPONIBLE),
            Vehicle(numero_economico="U-003", marca="International", modelo="LT625", anio=2020, placas="456-CC-3", numero_serie="SERIE003", estatus=VehicleStatus.DISPONIBLE),
        ]
        session.add_all(vehicles)
        await session.commit()


async def seed_trailers():
    """Crear 3 remolques de ejemplo"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Trailer).where(Trailer.numero_economico == "R-001"))
        if result.scalar_one_or_none():
            print("  Remolques ya existen")
            return
        
        print("  Creando remolques de prueba...")
        trailers = [
            Trailer(numero_economico="R-001", tipo=TrailerType.CAJA_SECA, marca="Utility", modelo="5000", anio=2022, placas="111-TR-1", capacidad_carga_ton=30.0, estatus=UnitStatus.DISPONIBLE),
            Trailer(numero_economico="R-002", tipo=TrailerType.PLATAFORMA, marca="Fontaine", modelo="Revolution", anio=2020, placas="222-TR-2", capacidad_carga_ton=35.0, estatus=UnitStatus.DISPONIBLE),
            Trailer(numero_economico="R-003", tipo=TrailerType.REFRIGERADO, marca="Great Dane", modelo="Everest", anio=2024, placas="333-TR-3", capacidad_carga_ton=28.0, estatus=UnitStatus.DISPONIBLE),
        ]
        session.add_all(trailers)
        await session.commit()


async def seed_clients():
    """Crear 3 clientes de ejemplo"""
    clients_data = [
        {
            "nombre": "Distribuidora Nacional S.A. de C.V.",
            "rfc": "DNA201201AB1",
            "direccion": "Av. Constitucion 1500, Centro, Monterrey, N.L.",
            "telefono": "8183001500",
            "email": "contacto@disnac.com.mx",
            "contacto_nombre": "Maria Gonzalez",
            "dias_credito": 30,
            "limite_credito": Decimal("500000.00"),
            "estatus": ClientStatus.ACTIVO,
        },
        {
            "nombre": "Importaciones del Norte S.A. de C.V.",
            "rfc": "INO150615CD2",
            "direccion": "Blvd. Diaz Ordaz 100, Santa Maria, Monterrey, N.L.",
            "telefono": "8184002000",
            "email": "ventas@imponorte.com",
            "contacto_nombre": "Carlos Mendoza",
            "dias_credito": 15,
            "limite_credito": Decimal("300000.00"),
            "estatus": ClientStatus.ACTIVO,
        },
        {
            "nombre": "Logistica Integral Azteca S.A. de C.V.",
            "rfc": "LIA180901EF3",
            "direccion": "Carr. Colombia Km 15, Apodaca, N.L.",
            "telefono": "8186003000",
            "email": "operaciones@lialogistics.mx",
            "contacto_nombre": "Ana Lucia Torres",
            "dias_credito": 45,
            "limite_credito": Decimal("750000.00"),
            "estatus": ClientStatus.ACTIVO,
        },
    ]
    
    async with AsyncSessionLocal() as session:
        for data in clients_data:
            result = await session.execute(
                select(Client).where(Client.rfc == data["rfc"])
            )
            if result.scalar_one_or_none():
                print(f"  Ya existe cliente: {data['nombre']}")
                continue
            
            client = Client(**data)
            session.add(client)
            print(f"  Creado cliente: {data['nombre']}")
        
        await session.commit()


async def seed_suppliers():
    """Crear 3 proveedores de ejemplo"""
    suppliers_data = [
        {
            "nombre": "Combustibles del Valle S.A. de C.V.",
            "rfc": "CVA100301GH1",
            "tipo": SupplierType.COMBUSTIBLE,
            "direccion": "Carr. Miguel Aleman Km 20, Guadalupe, N.L.",
            "telefono": "8185001000",
            "email": "ventas@combuvalle.com",
            "contacto_nombre": "Fernando Reyes",
            "estatus": SupplierStatus.ACTIVO,
        },
        {
            "nombre": "Refacciones y Servicios Profesionales S.A. de C.V.",
            "rfc": "RSP120815IJ2",
            "tipo": SupplierType.REFACCIONES,
            "direccion": "Av. Ruiz Cortines 2500, San Nicolas, N.L.",
            "telefono": "8186002000",
            "email": "ventas@refacpro.mx",
            "contacto_nombre": "Luis Garza",
            "estatus": SupplierStatus.ACTIVO,
        },
        {
            "nombre": "Taller Mecanico Especializado S.A. de C.V.",
            "rfc": "TME140220KL3",
            "tipo": SupplierType.SERVICIOS,
            "direccion": "Calle Industrial 500, Apodaca, N.L.",
            "telefono": "8187003000",
            "email": "servicio@tallerme.com",
            "contacto_nombre": "Miguel Angel Perez",
            "estatus": SupplierStatus.ACTIVO,
        },
    ]
    
    async with AsyncSessionLocal() as session:
        for data in suppliers_data:
            result = await session.execute(
                select(Supplier).where(Supplier.rfc == data["rfc"])
            )
            if result.scalar_one_or_none():
                print(f"  Ya existe proveedor: {data['nombre']}")
                continue
            
            supplier = Supplier(**data)
            session.add(supplier)
            print(f"  Creado proveedor: {data['nombre']}")
        
        await session.commit()


async def main():
    print("\nIniciando seed de catalogos...")
    
    print("\nChoferes:")
    await seed_drivers()
    
    print("\nVehiculos:")
    await seed_vehicles()
    
    print("\nRemolques:")
    await seed_trailers()
    
    print("\nClientes:")
    await seed_clients()
    
    print("\nProveedores:")
    await seed_suppliers()
    
    print("\nSeed completado!\n")


if __name__ == "__main__":
    asyncio.run(main())
