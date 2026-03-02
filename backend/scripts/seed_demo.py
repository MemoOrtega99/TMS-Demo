"""
seed_demo.py — Seed de datos de demostración para Soluciones-TMS
Agrega datos realistas que complementan el seed base:
  - Tracking comments (timeline) en viajes activos
  - Notificaciones mixtas (leídas/no leídas)
  - Artículos de inventario
  - Gastos de viaje detallados
  - Cargas de diesel vinculadas a viajes
  - Facturas (CxC y CxP) con distintos estatus

Ejecutar: python -m scripts.seed_demo (desde el directorio backend/)
"""
import asyncio
import sys
import os
from datetime import date, datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func
from src.core.database import AsyncSessionLocal
from src.models.trips import Trip, TripComment, TripExpense, DieselLoad, CommentType, ExpenseType, DieselLoadType
from src.models.notifications import Notification, NotificationType, NotificationPriority
from src.models.inventory import InventoryItem, InventoryCategory
from src.models.invoices import Invoice, InvoiceType, InvoiceStatus
from src.models.catalogs import Client, Supplier
from src.models.fleet import Vehicle
from src.models.user import User


async def seed_tracking_comments(session):
    """Agrega comentarios de tracking realistas a los viajes en ruta/completados."""
    print("  📍 Seeding tracking comments...")

    trips_q = await session.execute(
        select(Trip).where(Trip.estatus.in_(["en_ruta", "completado", "asignado"]))
        .limit(5)
    )
    trips = trips_q.scalars().all()

    if not trips:
        print("  ⚠️  No suitable trips found. Run seed_trips.py first.")
        return 0

    user_q = await session.execute(select(User).limit(1))
    user = user_q.scalar_one_or_none()
    user_id = user.id if user else None

    now = datetime.now(timezone.utc)
    comments_added = 0

    demo_comments_by_status = {
        "en_ruta": [
            ("estatus_change", "Viaje programado y listo para asignación de unidad.", None, now - timedelta(hours=12)),
            ("estatus_change", "Unidad asignada y operador confirmado para el viaje.", "Patio principal", now - timedelta(hours=11)),
            ("actualizacion", "Unidad salió de patio con carga completa. Todo en orden, sin novedades.", "Patio principal", now - timedelta(hours=10)),
            ("actualizacion", "Pasé primera caseta sin novedad. Buen tráfico en la carretera.", None, now - timedelta(hours=8)),
            ("incidencia", "Revisión federal en caseta intermedia. Estimado 30-45 min de retraso. Todo en regla.", "Caseta federal", now - timedelta(hours=5)),
            ("actualizacion", "Retomé la ruta. ETA al destino en approx. 3 horas.", None, now - timedelta(hours=4)),
        ],
        "completado": [
            ("estatus_change", "Viaje programado exitosamente.", None, now - timedelta(days=3, hours=24)),
            ("estatus_change", "Unidad y operador asignados, listos para salir mañana.", None, now - timedelta(days=3, hours=20)),
            ("actualizacion", "Salida del patio con carga verificada y sellada.", "Patio", now - timedelta(days=3, hours=18)),
            ("actualizacion", "En ruta, sin novedades. Buen clima.", None, now - timedelta(days=3, hours=14)),
            ("actualizacion", "Entrega realizada en almacén del cliente. Firmó de conformidad.", "Destino final", now - timedelta(days=2, hours=16)),
            ("estatus_change", "Viaje marcado como completado. Documentos entregados.", None, now - timedelta(days=2, hours=15)),
        ],
        "asignado": [
            ("estatus_change", "Viaje creado y en espera de asignación.", None, now - timedelta(hours=24)),
            ("estatus_change", "Unidad asignada. Operador notificado para mañana.", "Patio", now - timedelta(hours=16)),
        ],
    }

    for trip in trips:
        estatus_key = str(trip.estatus).replace("TripStatus.", "")
        if "en_ruta" in estatus_key.lower():
            template = demo_comments_by_status["en_ruta"]
        elif "completado" in estatus_key.lower():
            template = demo_comments_by_status["completado"]
        else:
            template = demo_comments_by_status["asignado"]

        # Check if already has comments
        existing = await session.scalar(
            select(func.count(TripComment.id)).where(TripComment.trip_id == trip.id)
        )
        if existing and existing > 0:
            print(f"  ⏭️  Trip {trip.numero_viaje} already has {existing} comments")
            continue

        for tipo_str, mensaje, ubicacion, created_at in template:
            try:
                tipo = CommentType(tipo_str)
            except ValueError:
                tipo = CommentType.actualizacion

            comment = TripComment(
                trip_id=trip.id,
                usuario_id=user_id,
                tipo=tipo,
                mensaje=mensaje,
                ubicacion=ubicacion,
                genera_notificacion=True,
                created_at=created_at,
            )
            session.add(comment)
            comments_added += 1

    await session.commit()
    print(f"  ✅ Added {comments_added} tracking comments across {len(trips)} trips")
    return comments_added


async def seed_notifications(session):
    """Agrega notificaciones mixtas para el usuario admin."""
    print("  🔔 Seeding notifications...")

    user_q = await session.execute(select(User).limit(1))
    user = user_q.scalar_one_or_none()
    if not user:
        print("  ⚠️  No users found. Run seed.py first.")
        return 0

    existing = await session.scalar(
        select(func.count(Notification.id)).where(Notification.usuario_id == user.id)
    )
    if existing and existing > 5:
        print(f"  ⏭️  Already {existing} notifications. Skipping.")
        return 0

    now = datetime.now(timezone.utc)
    notif_data = [
        # Facturas vencidas
        ("FAC-2026-015 vencida — $127,500 por cobrar a Grupo Bimbo", NotificationType.factura_vencida, NotificationPriority.urgente, "FAC-2026-015 MXN $127,500 con Grupo Bimbo lleva 15 días vencida.", False, now - timedelta(hours=2)),
        ("FAC-2026-011 vencida hace 3 días — FEMSA Logística $72,800", NotificationType.factura_vencida, NotificationPriority.alta, "Revisar con el área de cobranza.", False, now - timedelta(days=1)),
        ("FAC-2026-009 próxima a vencer en 5 días — Cemex $78,400", NotificationType.factura_por_vencer, NotificationPriority.alta, "Programar cobro antes del vencimiento.", False, now - timedelta(hours=6)),
        # Estatus de viajes
        ("VJ-2026-003 — Incidencia reportada: revisión federal Caseta Linares", NotificationType.tracking_update, NotificationPriority.alta, "El operador reportó +45 min de retraso por revisión federal.", False, now - timedelta(hours=5)),
        ("VJ-2026-004 — Viaje completado exitosamente", NotificationType.viaje_completado, NotificationPriority.media, "Documentos recibidos y firmados.", True, now - timedelta(days=2)),
        ("VJ-2026-002 — Unidad asignada y operador confirmado", NotificationType.viaje_en_ruta, NotificationPriority.media, "Unidad ECO-005 asignada. Operador confirmó disponibilidad.", True, now - timedelta(days=1, hours=4)),
        # Mantenimiento/Flota  
        ("ECO-007 requiere servicio preventivo esta semana", NotificationType.servicio_proximo, NotificationPriority.alta, "El vehículo ECO-007 alcanzará los 10,000 km de servicio esta semana.", False, now - timedelta(hours=14)),
        ("Licencia de A. López García vence en 25 días", NotificationType.servicio_proximo, NotificationPriority.alta, "Licencia vence el 31 Mar 2026. Coordinar renovación.", False, now - timedelta(days=5)),
        # Inventario bajo
        ("Filtro de aceite: 2 pzas (mín 5) — Solicitar reposición", NotificationType.stock_bajo, NotificationPriority.media, "Filtro de aceite motor (Freightliner) por debajo del mínimo.", False, now - timedelta(hours=8)),
        ("Banda de distribución Freightliner: 1 pza (mín 3)", NotificationType.stock_bajo, NotificationPriority.alta, "Stock crítico. Riesgo de no poder atender mantenimiento.", False, now - timedelta(days=2)),
        # Tracking updates
        ("VJ-2026-003 — Retomó ruta. ETA 16:30 hrs", NotificationType.tracking_update, NotificationPriority.media, "Operador retomó ruta tras revisión. Entrega estimada 16:30.", True, now - timedelta(hours=4)),
        ("VJ-2026-001 — Viaje programado para mañana", NotificationType.viaje_programado, NotificationPriority.baja, "Viaje confirmado. Todo listo para salida.", True, now - timedelta(days=2)),
        # CxP
        ("Llantera del Norte — $52,000 vencen en 3 días", NotificationType.factura_por_vencer, NotificationPriority.alta, "4 facturas próximas a vencer con Llantera del Norte.", False, now - timedelta(hours=3)),
        ("VJ-2026-003 — Salida de patio confirmada", NotificationType.tracking_update, NotificationPriority.baja, "Carga verificada y sellada.", True, now - timedelta(hours=10)),
        ("VJ-2026-002 — En ruta sin novedades", NotificationType.tracking_update, NotificationPriority.baja, "Seguimiento normal, sin incidentes.", True, now - timedelta(days=1, hours=6)),
    ]

    added = 0
    for titulo, tipo, prioridad, mensaje, leida, created_at in notif_data:
        notif = Notification(
            usuario_id=user.id,
            titulo=titulo,
            tipo=tipo,
            prioridad=prioridad,
            mensaje=mensaje,
            leida=leida,
            created_at=created_at,
        )
        session.add(notif)
        added += 1

    await session.commit()
    unread = sum(1 for _,_,_,_,l,_ in notif_data if not l)
    print(f"  ✅ Added {added} notifications ({unread} unread)")
    return added


async def seed_inventory(session):
    """Agrega artículos de inventario realistas de refacciones para flota."""
    print("  📦 Seeding inventory items...")

    existing = await session.scalar(select(func.count(InventoryItem.id)))
    if existing and existing > 5:
        print(f"  ⏭️  Already {existing} inventory items. Skipping.")
        return 0

    items = [
        ("REF-001", "Filtro de aceite motor (Freightliner Cascadia)", InventoryCategory.REFACCIONES, 2, 5, "pza", 850.00, "Estante A1"),
        ("REF-002", "Filtro de combustible Kenworth T680", InventoryCategory.REFACCIONES, 4, 5, "pza", 420.00, "Estante A2"),
        ("REF-003", "Pastillas de freno traseras (jgo.)", InventoryCategory.REFACCIONES, 6, 4, "jgo", 1800.00, "Estante A3"),
        ("REF-004", "Banda de distribución Freightliner", InventoryCategory.REFACCIONES, 1, 3, "pza", 2800.00, "Estante A4"),
        ("REF-005", "Filtro de aire primario", InventoryCategory.REFACCIONES, 8, 4, "pza", 650.00, "Estante A5"),
        ("LLA-001", "Llanta 11R22.5 Bridgestone R150 (nueva)", InventoryCategory.LLANTAS, 8, 4, "pza", 6800.00, "Bodega principal"),
        ("LLA-002", "Llanta 315/80R22.5 Continental (nueva)", InventoryCategory.LLANTAS, 3, 2, "pza", 7200.00, "Bodega principal"),
        ("LLA-003", "Llanta recauchutada 11R22.5", InventoryCategory.LLANTAS, 6, 4, "pza", 3200.00, "Bodega secundaria"),
        ("LUB-001", "Aceite motor Mobil Delvac 15W-40 (Caneca 19L)", InventoryCategory.LUBRICANTES, 12, 6, "pza", 1250.00, "Estante B2"),
        ("LUB-002", "Líquido de frenos DOT4 (1L)", InventoryCategory.LUBRICANTES, 15, 8, "pza", 165.00, "Estante B1"),
        ("LUB-003", "Grasa de chasis Shell Gadus S2 (400g)", InventoryCategory.LUBRICANTES, 20, 10, "pza", 98.00, "Estante B3"),
        ("LUB-004", "Aceite de transmision Meritor (Cubeta 19L)", InventoryCategory.LUBRICANTES, 4, 3, "pza", 1800.00, "Estante B4"),
        ("HER-001", "Gato hidraulico de piso 20T", InventoryCategory.HERRAMIENTAS, 2, 1, "pza", 4500.00, "Herramientas"),
        ("HER-002", "Llave de impacto neumatica 3/4", InventoryCategory.HERRAMIENTAS, 3, 2, "pza", 3200.00, "Herramientas"),
        ("OTHER-001", "Triangulos de emergencia (reflectivos)", InventoryCategory.OTRO, 10, 5, "set", 280.00, "Seguridad"),
    ]

    added = 0
    for codigo, nombre, categoria, stock, minimo, unidad, precio, ubicacion in items:
        exists = await session.scalar(
            select(func.count(InventoryItem.id)).where(InventoryItem.codigo == codigo)
        )
        if exists:
            continue
        item = InventoryItem(
            codigo=codigo, nombre=nombre, categoria=categoria,
            stock_actual=stock, stock_minimo=minimo, unidad_medida=unidad,
            precio_promedio=precio, ubicacion=ubicacion,
        )
        session.add(item)
        added += 1

    await session.commit()
    print(f"  ✅ Added {added} inventory items ({sum(1 for _,_,_,s,m,_,_,_ in items if s < m)} below minimum)")
    return added


async def seed_trip_expenses(session):
    """Agrega gastos detallados a los viajes existentes."""
    print("  💳 Seeding trip expenses...")

    trips_q = await session.execute(
        select(Trip).where(Trip.estatus.in_(["en_ruta", "completado"]))
        .limit(4)
    )
    trips = trips_q.scalars().all()

    if not trips:
        print("  ⚠️  No trips found. Skipping.")
        return 0

    added = 0
    expenses_template = [
        (ExpenseType.caseta, "Caseta autopista ida", 485.00),
        (ExpenseType.caseta, "Caseta intermedia", 1250.00),
        (ExpenseType.viaticos, "Viáticos operador — día 1", 500.00),
        (ExpenseType.viaticos, "Viáticos operador — día 2", 500.00),
    ]

    for trip in trips:
        existing = await session.scalar(
            select(func.count(TripExpense.id)).where(TripExpense.trip_id == trip.id)
        )
        if existing and existing > 0:
            print(f"  ⏭️  Trip {trip.numero_viaje} already has {existing} expenses")
            continue

        for tipo, descripcion, monto in expenses_template:
            expense = TripExpense(
                trip_id=trip.id,
                tipo_gasto=tipo,
                descripcion=descripcion,
                monto=monto,
                fecha_gasto=date.today() - timedelta(days=1),
            )
            session.add(expense)
            added += 1

    await session.commit()
    print(f"  ✅ Added {added} trip expenses")
    return added


async def seed_invoices(session):
    """Agrega facturas de CxC y CxP con distintos estatus para la demo."""
    print("  🧾 Seeding invoices (CxC & CxP)...")

    existing = await session.scalar(select(func.count(Invoice.id)))
    if existing and existing > 5:
        print(f"  ⏭️  Already {existing} invoices. Skipping.")
        return 0

    clients_q = await session.execute(select(Client).limit(5))
    clients = clients_q.scalars().all()
    if not clients:
        print("  ⚠️  No clients found.")
        return 0

    now = date.today()
    # Note: Invoice.cliente_id is nullable; for CxP we'd normally use supplier_id.
    # Using first client as placeholder since the model allows it.
    invoices_data = [
        # CxC — Por cobrar (overdue = fecha_vencimiento < today)
        ("FAC-2026-015", InvoiceType.POR_COBRAR, clients[0].id, 127500.00, 0, now - timedelta(days=15), "Grupo Bimbo — Servicios de transporte Marzo 2026", InvoiceStatus.PENDIENTE),
        ("FAC-2026-014", InvoiceType.POR_COBRAR, clients[1].id if len(clients) > 1 else clients[0].id, 72800.00, 0, now - timedelta(days=3), "FEMSA Logistica — Servicios Mar", InvoiceStatus.PENDIENTE),
        ("FAC-2026-013", InvoiceType.POR_COBRAR, clients[2].id if len(clients) > 2 else clients[0].id, 78400.00, 0, now + timedelta(days=5), "Cemex — Transporte materiales", InvoiceStatus.PENDIENTE),
        ("FAC-2026-012", InvoiceType.POR_COBRAR, clients[0].id, 95000.00, 47500.00, now + timedelta(days=12), "Grupo Bimbo — Pago parcial Feb 2026", InvoiceStatus.PARCIAL),
        ("FAC-2026-011", InvoiceType.POR_COBRAR, clients[3].id if len(clients) > 3 else clients[0].id, 110000.00, 110000.00, now - timedelta(days=20), "Liverpool — Muebles completado", InvoiceStatus.PAGADA),
        ("FAC-2026-010", InvoiceType.POR_COBRAR, clients[4].id if len(clients) > 4 else clients[0].id, 89500.00, 89500.00, now - timedelta(days=30), "Ternium — Acero completado", InvoiceStatus.PAGADA),
        # CxP — Por pagar
        ("PRP-2026-008", InvoiceType.POR_PAGAR, clients[0].id, 52000.00, 0, now + timedelta(days=3), "Llantera del Norte — Llantas vehiculos", InvoiceStatus.PENDIENTE),
        ("PRP-2026-007", InvoiceType.POR_PAGAR, clients[0].id, 38400.00, 0, now - timedelta(days=7), "Pemex Transformacion — Diesel marzo", InvoiceStatus.PENDIENTE),
        ("PRP-2026-006", InvoiceType.POR_PAGAR, clients[0].id, 28500.00, 14250.00, now + timedelta(days=10), "Taller Garcia — Mantenimientos", InvoiceStatus.PARCIAL),
        ("PRP-2026-005", InvoiceType.POR_PAGAR, clients[0].id, 18500.00, 18500.00, now - timedelta(days=15), "AutoZone Industrial — Refacciones", InvoiceStatus.PAGADA),
    ]

    added = 0
    for folio, tipo, cliente_id, total, pagado, vencimiento, concepto, estatus in invoices_data:
        exists = await session.scalar(
            select(func.count(Invoice.id)).where(Invoice.folio == folio)
        )
        if exists:
            continue
        invoice = Invoice(
            folio=folio, tipo=tipo, cliente_id=cliente_id,
            total=total, monto_pagado=pagado,
            fecha_vencimiento=vencimiento, concepto=concepto,
            estatus=estatus,
        )
        session.add(invoice)
        added += 1

    await session.commit()
    print(f"  ✅ Added {added} invoices")
    return added


async def main():
    print("\n🎯 SEED DE DEMOSTRACIÓN — Soluciones-TMS")
    print("=========================================\n")

    async with AsyncSessionLocal() as session:
        print("1️⃣  Comentarios de tracking (timeline)...")
        await seed_tracking_comments(session)

        print("\n2️⃣  Notificaciones...")
        await seed_notifications(session)

        print("\n3️⃣  Inventario de refacciones...")
        await seed_inventory(session)

        print("\n4️⃣  Gastos de viaje...")
        await seed_trip_expenses(session)

        print("\n5️⃣  Facturas CxC y CxP...")
        await seed_invoices(session)

    print("\n✅ SEED DE DEMO COMPLETADO ✅")
    print("   El sistema tiene ahora datos completos para la presentación.")


if __name__ == "__main__":
    asyncio.run(main())
