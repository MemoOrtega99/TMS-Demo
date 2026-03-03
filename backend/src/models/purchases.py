"""
Purchase models for requisitions and purchase orders.
"""
from datetime import date
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
import enum

from sqlalchemy import String, Integer, Text, Date, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from src.models.catalogs import Supplier
    from src.models.user import User
    from src.models.invoices import Invoice
    from src.models.inventory import InventoryMovement, InventoryItem


# ==================== ENUMS ====================

class RequisitionStatus(str, enum.Enum):
    """Estatus de requisición"""
    BORRADOR = "borrador"        # En edición
    PENDIENTE = "pendiente"      # Enviada para aprobación
    APROBADA = "aprobada"        # Aprobada → genera OC
    RECHAZADA = "rechazada"      # Rechazada
    COMPLETADA = "completada"    # Proceso completo


class PurchaseOrderStatus(str, enum.Enum):
    """Estatus de orden de compra"""
    PENDIENTE = "pendiente"      # Recién creada
    ENVIADA = "enviada"          # Enviada al proveedor
    PARCIAL = "parcial"          # Recepción parcial
    RECIBIDA = "recibida"        # Recepción completa
    CANCELADA = "cancelada"      # Cancelada


# ==================== MODELS ====================

class Requisition(BaseModel, TimestampMixin):
    """
    Requisición de compra - solicitud inicial antes de generar orden de compra.
    """
    __tablename__ = "requisitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Identificación
    numero: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    
    # Fechas
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_requerida: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Solicitante
    solicitante_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id"), 
        nullable=False
    )
    solicitante: Mapped["User"] = relationship("User", foreign_keys=[solicitante_id])
    
    # Proveedor sugerido (opcional en requisición)
    proveedor_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("suppliers.id"), 
        nullable=True
    )
    proveedor: Mapped[Optional["Supplier"]] = relationship(
        "Supplier", 
        foreign_keys=[proveedor_id]
    )
    
    # Estado
    estatus: Mapped[RequisitionStatus] = mapped_column(
        SQLEnum(RequisitionStatus), 
        default=RequisitionStatus.BORRADOR
    )
    
    # Montos estimados
    total_estimado: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    
    # Líneas de la requisición
    items: Mapped[List["RequisitionItem"]] = relationship(
        "RequisitionItem", 
        back_populates="requisition",
        cascade="all, delete-orphan"
    )
    
    # Orden de compra generada (cuando se aprueba)
    purchase_order: Mapped[Optional["PurchaseOrder"]] = relationship(
        "PurchaseOrder", 
        back_populates="requisition",
        uselist=False
    )


class RequisitionItem(BaseModel):
    """
    Línea de requisición - cada producto/servicio solicitado.
    """
    __tablename__ = "requisition_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Relación con requisición
    requisition_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("requisitions.id"), 
        nullable=False
    )
    requisition: Mapped["Requisition"] = relationship(
        "Requisition", 
        back_populates="items"
    )
    
    # Producto (opcional - puede ser nuevo o existente en inventario)
    inventory_item_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("inventory_items.id"), 
        nullable=True
    )
    inventory_item: Mapped[Optional["InventoryItem"]] = relationship("InventoryItem")
    
    # Descripción (siempre requerida, incluso si hay producto)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Cantidad y unidad
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    unidad: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Precio estimado (opcional)
    precio_estimado: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(14, 2), 
        nullable=True
    )


class PurchaseOrder(BaseModel, TimestampMixin):
    """
    Orden de compra - generada a partir de una requisición aprobada.
    """
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Identificación
    numero: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    
    # Requisición de origen
    requisition_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("requisitions.id"), 
        nullable=True
    )
    requisition: Mapped["Requisition"] = relationship(
        "Requisition", 
        back_populates="purchase_order"
    )
    
    # Proveedor (requerido en OC)
    proveedor_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("suppliers.id"), 
        nullable=False
    )
    proveedor: Mapped["Supplier"] = relationship(
        "Supplier", 
        back_populates="purchase_orders"
    )
    
    # Fechas
    fecha_orden: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_entrega_esperada: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_entrega_real: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Montos
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    iva: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    
    # Estado
    estatus: Mapped[PurchaseOrderStatus] = mapped_column(
        SQLEnum(PurchaseOrderStatus), 
        default=PurchaseOrderStatus.PENDIENTE
    )
    
    # Líneas de la orden
    items: Mapped[List["PurchaseOrderItem"]] = relationship(
        "PurchaseOrderItem", 
        back_populates="purchase_order",
        cascade="all, delete-orphan"
    )
    
    # Facturas asociadas
    invoices: Mapped[List["Invoice"]] = relationship(
        "Invoice", 
        backref="purchase_order"
    )
    
    # Movimientos de inventario (recepciones)
    inventory_movements: Mapped[List["InventoryMovement"]] = relationship(
        "InventoryMovement", 
        back_populates="purchase_order"
    )


class PurchaseOrderItem(BaseModel):
    """
    Línea de orden de compra - cada producto/servicio ordenado.
    """
    __tablename__ = "purchase_order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Relación con orden de compra
    purchase_order_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("purchase_orders.id"), 
        nullable=False
    )
    purchase_order: Mapped["PurchaseOrder"] = relationship(
        "PurchaseOrder", 
        back_populates="items"
    )
    
    # Producto (opcional)
    inventory_item_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("inventory_items.id"), 
        nullable=True
    )
    inventory_item: Mapped[Optional["InventoryItem"]] = relationship("InventoryItem")
    
    # Descripción
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Cantidad y unidad
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    unidad: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Precio
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    
    # Recepción
    cantidad_recibida: Mapped[Decimal] = mapped_column(Numeric(14, 3), default=0)
    
    @property
    def subtotal(self) -> Decimal:
        """Calcula el subtotal de la línea"""
        return self.cantidad * self.precio_unitario
    
    @property
    def pendiente_recibir(self) -> Decimal:
        """Cantidad pendiente de recibir"""
        return self.cantidad - self.cantidad_recibida
