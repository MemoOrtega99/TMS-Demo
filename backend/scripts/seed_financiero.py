"""
seed_financiero.py — Seed de datos financieros completo para Soluciones-TMS.

Genera:
  - 5 meses de historial de viajes completados (Nov 2025 – Mar 2026)
  - Facturas POR_COBRAR (clientes) y POR_PAGAR (proveedores) por mes
  - Pagos parciales y totales para cada factura
  - Facturas vencidas sin pagar (para análisis de cartera)
  - Gastos de nómina, diesel y mantenimiento (facturas de proveedores)
  - Resumen listo para preguntas: CxC, CxP, margen, vencimiento, cobros del mes
"""

import asyncio
import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from src.core.database import AsyncSessionLocal
from src.models.trips import Trip, TripStatus, TripExpense, ExpenseType
from src.models.invoices import Invoice, Payment, InvoiceType, InvoiceStatus, PaymentMethod
from src.models.catalogs import Driver, Client, ClientStatus, Supplier, SupplierType, SupplierStatus, DriverStatus
from src.models.user import User

# ──────────────────────────────────────────────
# Configuración de escenario
# ──────────────────────────────────────────────
MONTHS = [
    (2025, 11, "NOV25"),
    (2025, 12, "DIC25"),
    (2026,  1, "ENE26"),
    (2026,  2, "FEB26"),
    (2026,  3, "MAR26"),
]

ROUTES = [
    ("CDMX",      "Monterrey",    Decimal("22000")),
    ("Guadalajara","Nuevo Laredo", Decimal("18500")),
    ("CDMX",      "Tijuana",      Decimal("35000")),
    ("Puebla",    "Monterrey",    Decimal("16000")),
    ("Queretaro", "Chihuahua",    Decimal("28000")),
    ("CDMX",      "Mérida",       Decimal("30000")),
    ("Saltillo",  "Guadalajara",  Decimal("20000")),
]

CLIENTS_DATA = [
    ("Distribuidora Nacional S.A. de C.V.",  "RFC-DN001", "contacto@distnac.com"),
    ("Importaciones del Norte S.A. de C.V.", "RFC-IN002", "finanzas@impnorte.com"),
    ("Logística Express México S.A.",        "RFC-LX003", "ops@logexpressm.com"),
    ("Grupo Industrial Regiomontano",        "RFC-GI004", "cuentas@girm.com.mx"),
    ("Cementos Bajío S.A. de C.V.",          "RFC-CB005", "pagos@cementbajio.mx"),
]

SUPPLIERS_DATA = [
    ("Diesel Pátzcuaro S.A.",    "RFC-DP001", SupplierType.COMBUSTIBLE),
    ("Talleres Mecánicos Ruta",  "RFC-TM002", SupplierType.REFACCIONES),
    ("Seguros Transporte Max",   "RFC-ST003", SupplierType.SERVICIOS),
    ("Casetas y Peajes MX S.A.", "RFC-CP004", SupplierType.CASETAS),
    ("Proveedor General CDMX",   "RFC-PG005", SupplierType.OTRO),
]


async def seed_financiero():
    print("\n💰 INICIANDO SEED FINANCIERO COMPLETO 💰")
    print("=" * 50)

    async with AsyncSessionLocal() as db:
        # ── 0. Obtener entidades base ──────────────────────
        user = await db.scalar(select(User).limit(1))
        if not user:
            print("  ❌ No hay usuarios. Ejecuta seed_full.py primero.")
            return

        drivers_q = await db.execute(select(Driver))
        drivers = drivers_q.scalars().all()

        if not drivers:
            print("  ❌ No hay choferes. Ejecuta seed_full.py primero.")
            return

        # ── 1. Crear / encontrar clientes ──────────────────
        print("\n  👤 Configurando clientes...")
        clients = []
        for nombre, rfc, email in CLIENTS_DATA:
            existing = await db.scalar(select(Client).where(Client.rfc == rfc))
            if not existing:
                c = Client(
                    nombre=nombre,
                    rfc=rfc,
                    email=email,
                    telefono="800-111-0000",
                    direccion="Av. Industrial 100, México",
                    estatus=ClientStatus.ACTIVO,
                    dias_credito=30,
                )
                db.add(c)
                await db.flush()
                clients.append(c)
            else:
                clients.append(existing)
        await db.commit()

        # ── 2. Crear / encontrar proveedores ───────────────
        print("  🏭 Configurando proveedores...")
        suppliers = []
        for nombre, rfc, tipo in SUPPLIERS_DATA:
            existing = await db.scalar(select(Supplier).where(Supplier.rfc == rfc))
            if not existing:
                s = Supplier(
                    nombre=nombre,
                    rfc=rfc,
                    tipo=tipo,
                    email=f"factura@{nombre.lower().replace(' ', '')}.mx",
                    estatus=SupplierStatus.ACTIVO,
                )
                db.add(s)
                await db.flush()
                suppliers.append(s)
            else:
                suppliers.append(existing)
        await db.commit()

        # ── 3. Generar viajes, facturas de ingresos y egresos por mes ──
        print("\n  📅 Generando historial de 5 meses...\n")
        trip_counter = 1000
        inv_counter = 1000

        for year, month, mes_tag in MONTHS:
            print(f"  ── {mes_tag} ({year}-{month:02d}) ──")
            
            n_trips = random.randint(14, 22)       # entre 14 y 22 viajes/mes
            viajes_completados = []

            for j in range(n_trips):
                trip_counter += 1
                trip_no = f"VJ-{mes_tag}-{trip_counter}"
                exists = await db.scalar(select(Trip).where(Trip.numero_viaje == trip_no))
                if exists:
                    continue

                route = random.choice(ROUTES)
                driver = random.choice(drivers)
                client = random.choice(clients)
                trip_date = date(year, month, random.randint(1, 27))

                tarifa = route[2] * Decimal(str(round(random.uniform(0.9, 1.15), 2)))

                t = Trip(
                    numero_viaje=trip_no,
                    chofer_id=driver.id,
                    cliente_id=client.id,
                    origen=route[0],
                    destino=route[1],
                    tarifa_cliente=tarifa.quantize(Decimal("0.01")),
                    estatus=TripStatus.completado,
                    fecha_programada=trip_date,
                    fecha_entrega_real=datetime(year, month, min(trip_date.day + 2, 28))
                )
                db.add(t)
                await db.flush()  # get id

                # Gastos del viaje
                gastos_caseta = tarifa * Decimal("0.06")
                gastos_diesel = tarifa * Decimal("0.35")
                gastos_viaticos = tarifa * Decimal("0.05")

                db.add(TripExpense(trip_id=t.id, tipo_gasto=ExpenseType.caseta,
                                   monto=gastos_caseta.quantize(Decimal("0.01")),
                                   fecha_gasto=trip_date))
                db.add(TripExpense(trip_id=t.id, tipo_gasto=ExpenseType.combustible,
                                   monto=gastos_diesel.quantize(Decimal("0.01")),
                                   fecha_gasto=trip_date))
                db.add(TripExpense(trip_id=t.id, tipo_gasto=ExpenseType.viaticos,
                                   monto=gastos_viaticos.quantize(Decimal("0.01")),
                                   fecha_gasto=trip_date))

                viajes_completados.append((t, client, tarifa, trip_date))

            await db.commit()

            # ── 3b. Facturas POR_COBRAR (ingresos de clientes) ──────
            # Agrupar viajes por cliente en el mes y emitir factura
            by_client: dict[int, list] = {}
            for trip_obj, client, tarifa, trip_date in viajes_completados:
                by_client.setdefault(client.id, []).append((trip_obj, tarifa, trip_date, client))

            for client_id, viajes in by_client.items():
                inv_counter += 1
                fac_no = f"FAC-{mes_tag}-{inv_counter:04d}"
                total_cobrar = sum(v[1] for v in viajes)
                subtotal = (total_cobrar / Decimal("1.16")).quantize(Decimal("0.01"))
                iva = (total_cobrar - subtotal).quantize(Decimal("0.01"))
                fecha_fac = viajes[-1][2]  # fecha del último viaje
                fecha_vcto = fecha_fac + timedelta(days=30)

                # Decidir estatus según el mes
                if mes_tag in ("NOV25", "DIC25", "ENE26"):
                    # Meses pasados → PAGADA o PARCIAL
                    paid_ratio = random.choice([1.0, 1.0, 0.5, 1.0])
                    monto_pagado = (total_cobrar * Decimal(str(paid_ratio))).quantize(Decimal("0.01"))
                    estatus = InvoiceStatus.PAGADA if paid_ratio == 1.0 else InvoiceStatus.PARCIAL
                elif mes_tag == "FEB26":
                    # Febrero → algunas pagadas, algunas VENCIDAS (fecha_vcto < hoy)
                    paid_ratio = random.choice([0, 0, 0.5, 1.0])
                    monto_pagado = (total_cobrar * Decimal(str(paid_ratio))).quantize(Decimal("0.01"))
                    estatus = (InvoiceStatus.PAGADA if paid_ratio == 1.0
                               else InvoiceStatus.PARCIAL if paid_ratio > 0
                               else InvoiceStatus.PENDIENTE)
                    fecha_vcto = date(2026, 2, 28)  # force overdue
                else:
                    # MAR26 → recientes, pendientes
                    monto_pagado = Decimal("0.00")
                    estatus = InvoiceStatus.PENDIENTE
                    fecha_vcto = date(2026, 3, 31)

                inv = Invoice(
                    numero_factura=fac_no,
                    tipo=InvoiceType.POR_COBRAR,
                    estatus=estatus,
                    fecha_factura=fecha_fac,
                    fecha_vencimiento=fecha_vcto,
                    subtotal=subtotal,
                    iva=iva,
                    total=total_cobrar,
                    monto_pagado=monto_pagado,
                    cliente_id=client_id,
                    concepto=f"Servicios de transporte {mes_tag} — {len(viajes)} viaje(s)",
                )
                db.add(inv)
                await db.flush()

                # Pago asociado si aplica
                if monto_pagado > 0:
                    p = Payment(
                        invoice_id=inv.id,
                        fecha_pago=fecha_fac + timedelta(days=random.randint(5, 25)),
                        monto=monto_pagado,
                        metodo_pago=random.choice([PaymentMethod.TRANSFERENCIA, PaymentMethod.CHEQUE]),
                        referencia=f"REF-{mes_tag}-{inv_counter}",
                        usuario_id=user.id
                    )
                    db.add(p)

            await db.commit()
            print(f"    ✅ {len(viajes_completados)} viajes + {len(by_client)} facturas CxC")

            # ── 3c. Facturas POR_PAGAR (egresos a proveedores) ──────
            inv_gasto_counter = 0
            gasto_scenarios = [
                (suppliers[0], "Diesel y combustibles del mes",   Decimal("85000"), InvoiceStatus.PAGADA),
                (suppliers[1], "Mantenimiento preventivo flota",  Decimal("42000"), InvoiceStatus.PAGADA if mes_tag != "MAR26" else InvoiceStatus.PENDIENTE),
                (suppliers[2], "Prima de seguro de carga",        Decimal("28000"), InvoiceStatus.PAGADA if mes_tag in ("NOV25", "DIC25") else InvoiceStatus.PENDIENTE),
                (suppliers[3], "Casetas autopistas",              Decimal("31000"), InvoiceStatus.PAGADA),
                (suppliers[4], "Gastos generales operativos",     Decimal("15000"), InvoiceStatus.PARCIAL if mes_tag == "FEB26" else InvoiceStatus.PAGADA),
            ]

            for sup, concepto, importe_base, est in gasto_scenarios:
                inv_counter += 1
                inv_gasto_counter += 1
                factor = Decimal(str(round(random.uniform(0.92, 1.08), 3)))
                total_pp = (importe_base * factor).quantize(Decimal("0.01"))
                sub_pp  = (total_pp / Decimal("1.16")).quantize(Decimal("0.01"))
                iva_pp  = (total_pp - sub_pp).quantize(Decimal("0.01"))
                fecha_pp = date(year, month, random.randint(1, 25))

                mp = Decimal("0.00")
                if est == InvoiceStatus.PAGADA:
                    mp = total_pp
                elif est == InvoiceStatus.PARCIAL:
                    mp = (total_pp * Decimal("0.5")).quantize(Decimal("0.01"))

                inv_pp = Invoice(
                    numero_factura=f"CXP-{mes_tag}-{inv_counter:04d}",
                    tipo=InvoiceType.POR_PAGAR,
                    estatus=est,
                    fecha_factura=fecha_pp,
                    fecha_vencimiento=fecha_pp + timedelta(days=30),
                    subtotal=sub_pp,
                    iva=iva_pp,
                    total=total_pp,
                    monto_pagado=mp,
                    proveedor_id=sup.id,
                    concepto=f"{concepto} ({mes_tag})",
                )
                db.add(inv_pp)
                await db.flush()

                if mp > 0:
                    p_pp = Payment(
                        invoice_id=inv_pp.id,
                        fecha_pago=fecha_pp + timedelta(days=random.randint(3, 20)),
                        monto=mp,
                        metodo_pago=PaymentMethod.TRANSFERENCIA,
                        referencia=f"PAG-{mes_tag}-PROV-{inv_gasto_counter}",
                        usuario_id=user.id
                    )
                    db.add(p_pp)

            await db.commit()
            print(f"    ✅ {inv_gasto_counter} facturas CxP ({mes_tag})")

        # ── 4. Facturas extra vencidas para que haya deuda real ──────
        print("\n  ⚠️  Agregando cartera vencida dramática para la demo...")
        vencidas_extra = [
            ("Distribuidora Nacional S.A. de C.V.", clients[0].id, Decimal("187500"), date(2026, 1, 15), "Servicio fletes enero 2026"),
            ("Logística Express México S.A.",        clients[2].id, Decimal("95200"),  date(2026, 2, 1),  "Servicio Querétaro-Nogales"),
            ("Grupo Industrial Regiomontano",        clients[3].id, Decimal("68000"),  date(2025, 12, 1), "Fletes diciembre crédito ext."),
        ]

        for nombre_cl, cl_id, total_v, fecha_v, concepto_v in vencidas_extra:
            inv_counter += 1
            fac_v = f"FAC-VCTO-{inv_counter:04d}"
            exists = await db.scalar(select(Invoice).where(Invoice.numero_factura == fac_v))
            if exists:
                continue
            sub_v = (total_v / Decimal("1.16")).quantize(Decimal("0.01"))
            iva_v = (total_v - sub_v).quantize(Decimal("0.01"))
            inv_v = Invoice(
                numero_factura=fac_v,
                tipo=InvoiceType.POR_COBRAR,
                estatus=InvoiceStatus.PENDIENTE,
                fecha_factura=fecha_v,
                fecha_vencimiento=fecha_v + timedelta(days=30),
                subtotal=sub_v,
                iva=iva_v,
                total=total_v,
                monto_pagado=Decimal("0.00"),
                cliente_id=cl_id,
                concepto=concepto_v,
            )
            db.add(inv_v)

        await db.commit()
        print("    ✅ Cartera vencida agregada")

        # ── 5. Resumen final ───────────────────────────────────────────
        from sqlalchemy import func
        cxc_total = await db.scalar(
            select(func.sum(Invoice.total - Invoice.monto_pagado))
            .where(Invoice.tipo == InvoiceType.POR_COBRAR, Invoice.estatus != InvoiceStatus.PAGADA)
        )
        cxp_total = await db.scalar(
            select(func.sum(Invoice.total - Invoice.monto_pagado))
            .where(Invoice.tipo == InvoiceType.POR_PAGAR, Invoice.estatus != InvoiceStatus.PAGADA)
        )
        total_trips = await db.scalar(
            select(func.count(Trip.id)).where(Trip.estatus == TripStatus.completado)
        )

        print(f"\n{'='*50}")
        print(f"  ✅ SEED FINANCIERO COMPLETADO CON ÉXITO")
        print(f"{'='*50}")
        print(f"  📦 Viajes completados totales:  {total_trips}")
        print(f"  💚 Saldo CxC pendiente:         ${float(cxc_total or 0):,.2f} MXN")
        print(f"  💔 Saldo CxP pendiente:         ${float(cxp_total or 0):,.2f} MXN")
        print(f"{'='*50}\n")


if __name__ == "__main__":
    asyncio.run(seed_financiero())
