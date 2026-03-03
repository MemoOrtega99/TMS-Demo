"""
seed_rendimientos.py — Asigna vehículos a viajes y genera cargas de diesel
con odómetros realistas para que el AI pueda calcular km/L por unidad.
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func, text
from src.core.database import AsyncSessionLocal
from src.models.fleet import Vehicle
from src.models.trips import Trip, TripStatus, DieselLoad, DieselLoadType


# KMs aproximados por ruta
ROUTE_KM = {
    ("CDMX", "Monterrey"):     940,
    ("Guadalajara", "Nuevo Laredo"): 810,
    ("CDMX", "Tijuana"):       2900,
    ("Puebla", "Monterrey"):   840,
    ("Queretaro", "Chihuahua"): 1400,
    ("CDMX", "Mérida"):        1550,
    ("Saltillo", "Guadalajara"): 780,
}
DEFAULT_KM = 900


async def seed_rendimientos():
    print("\n🚛 SEED DE RENDIMIENTOS POR UNIDAD 🚛")
    print("=" * 50)

    async with AsyncSessionLocal() as db:
        # 1. Obtener vehículos
        vehs_q = await db.execute(select(Vehicle))
        vehicles = vehs_q.scalars().all()
        if not vehicles:
            print("  ❌ No hay vehículos. Ejecuta seed_full.py primero.")
            return
        print(f"  🚚 {len(vehicles)} vehículos encontrados: {[v.placas for v in vehicles]}")

        # 2. Asignar vehículo a viajes que no tienen uno
        trips_sin_veh = (await db.execute(
            select(Trip)
            .where(Trip.estatus == TripStatus.completado, Trip.vehiculo_id == None)
            .order_by(Trip.id)
        )).scalars().all()

        print(f"  🔗 Asignando vehículo a {len(trips_sin_veh)} viajes sin unidad...")
        for i, trip in enumerate(trips_sin_veh):
            trip.vehiculo_id = vehicles[i % len(vehicles)].id

        await db.commit()
        print(f"  ✅ Vehículos asignados")

        # 3. Borrar cargas de diesel anteriores (si existen y son de prueba)
        old_loads = (await db.execute(select(DieselLoad))).scalars().all()
        for load in old_loads:
            await db.delete(load)
        await db.commit()
        print(f"  🧹 Cargas diesel anteriores eliminadas ({len(old_loads)} registros)")

        # 4. Generar historial de cargas diesel realistas por vehículo
        #    Basado en los viajes asignados — simula paradas en gasolinera
        print(f"  ⛽  Generando historial de cargas diesel por unidad...")

        for v in vehicles:
            viajes_v = (await db.execute(
                select(Trip)
                .where(Trip.vehiculo_id == v.id, Trip.estatus == TripStatus.completado)
                .order_by(Trip.fecha_programada)
            )).scalars().all()

            if not viajes_v:
                continue

            # km/L de la unidad (variación realista entre 3.8 y 4.8)
            kml_base = round(random.uniform(3.8, 4.8), 2)
            km_odometro = random.randint(80000, 120000)  # odómetro inicial

            for trip in viajes_v:
                km_ruta = ROUTE_KM.get((trip.origen, trip.destino), DEFAULT_KM)

                # Consumo esperado para este viaje
                litros = round(km_ruta / kml_base, 1)
                costo_litro = round(random.uniform(22.5, 24.5), 2)
                costo_total = Decimal(str(round(litros * costo_litro, 2)))

                # Carga al inicio del viaje
                load = DieselLoad(
                    vehicle_id=v.id,
                    litros=litros,
                    costo_total=costo_total,
                    km_odometro=km_odometro,
                    fecha_carga=trip.fecha_programada,
                    tipo=random.choice([DieselLoadType.patio, DieselLoadType.gasolinera]),
                )
                db.add(load)

                # Avanzar odómetro
                km_odometro += km_ruta

            await db.commit()

        # 5. Resumen
        total_loads = await db.scalar(select(func.count(DieselLoad.id)))
        total_litros = await db.scalar(select(func.sum(DieselLoad.litros)))
        total_costo = await db.scalar(select(func.sum(DieselLoad.costo_total)))

        print(f"\n{'='*50}")
        print(f"  ✅ SEED DE RENDIMIENTOS COMPLETADO")
        print(f"{'='*50}")
        print(f"  ⛽  Cargas de diesel:    {total_loads}")
        print(f"  📏  Litros totales:      {float(total_litros or 0):,.0f} L")
        print(f"  💵  Costo total diesel:  ${float(total_costo or 0):,.2f} MXN")
        print(f"{'='*50}\n")

        # 6. Vista previa del rendimiento por unidad
        perf = await db.execute(text("""
            SELECT 
                v.placas, v.modelo,
                COUNT(t.id) as viajes,
                SUM(dl.litros) as litros,
                (MAX(dl.km_odometro) - MIN(dl.km_odometro)) as km_total
            FROM vehicles v
            LEFT JOIN trips t ON t.vehiculo_id = v.id AND t.estatus = 'completado'
            LEFT JOIN diesel_loads dl ON dl.vehicle_id = v.id
            GROUP BY v.id, v.placas, v.modelo
            HAVING SUM(dl.litros) IS NOT NULL
        """))
        print("  VISTA PREVIA RENDIMIENTO:")
        for r in perf.all():
            rend = r.km_total / r.litros if r.litros else 0
            print(f"    🚛 {r.placas} ({r.modelo}): {r.viajes} viajes | {float(r.litros):,.0f} L | {rend:.2f} km/L")


if __name__ == "__main__":
    asyncio.run(seed_rendimientos())
