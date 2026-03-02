"""
Model exports
"""
from src.models.base import Base, BaseModel, TimestampMixin
from src.models.user import User, Role, DEFAULT_ROLES
from src.models.catalogs import Client, Supplier, Driver
from src.models.fleet import Vehicle, VehicleService, Trailer, Dolly
from src.models.trips import Trip, TripExpense, DieselLoad, TripComment
from src.models.invoices import Invoice, Payment
from src.models.purchases import PurchaseOrder, PurchaseOrderItem
from src.models.inventory import InventoryItem, InventoryMovement
from src.models.notifications import Notification

# Enums
from src.models.catalogs import DriverStatus, ClientStatus, SupplierType, SupplierStatus
from src.models.fleet import VehicleType, VehicleStatus, TrailerType, UnitStatus, ServiceType
from src.models.trips import TripStatus, ExpenseType, DieselLoadType, CommentType
from src.models.invoices import InvoiceType, InvoiceStatus, PaymentMethod
from src.models.purchases import PurchaseOrderStatus
from src.models.inventory import InventoryCategory, MovementType
from src.models.notifications import NotificationType, NotificationPriority

__all__ = [
    # Base
    "Base",
    "BaseModel",
    "TimestampMixin",
    
    # Entities
    "User",
    "Role",
    "DEFAULT_ROLES",
    "Client",
    "Supplier",
    "Driver",
    "Vehicle",
    "VehicleService",
    "Trailer",
    "Dolly",
    "Trip",
    "TripExpense",
    "DieselLoad",
    "TripComment",
    "Invoice",
    "Payment",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "InventoryItem",
    "InventoryMovement",
    "Notification",
    
    # Enums
    "DriverStatus",
    "ClientStatus",
    "SupplierType",
    "SupplierStatus",
    "VehicleType",
    "VehicleStatus",
    "TrailerType",
    "UnitStatus",
    "ServiceType",
    "TripStatus",
    "ExpenseType",
    "DieselLoadType",
    "CommentType",
    "InvoiceType",
    "InvoiceStatus",
    "PaymentMethod",
    "PurchaseOrderStatus",
    "InventoryCategory",
    "MovementType",
    "NotificationType",
    "NotificationPriority",
]
