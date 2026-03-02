"""
API v1 Router
"""
from fastapi import APIRouter

from src.api.v1.endpoints import auth, catalogs, fleet, trips, invoices, purchases, inventory, notifications, ai, dashboard, tracking_ws

router = APIRouter()

# Auth
router.include_router(auth.router, prefix="/auth")

# Catalogs (Choferes, Clientes, Proveedores)
router.include_router(catalogs.router)

# Fleet (Unidades, Remolques, Dollies, Servicios)
router.include_router(fleet.router)

# Trips (Viajes, Gastos, Diesel, Tracking)
router.include_router(trips.router)

# Invoices (CxP, CxC, Payments, Aging Report)
router.include_router(invoices.router)

# Purchases (Purchase Orders)
router.include_router(purchases.router)

# Inventory (Items, Movements)
router.include_router(inventory.router)

# Notifications
router.include_router(notifications.router)

# AI Chat (OpenRouter)
router.include_router(ai.router, prefix="/ai")

# Dashboard
router.include_router(dashboard.router, prefix="/dashboard")

# Tracking WebSocket (tiempo real)
router.include_router(tracking_ws.router)
