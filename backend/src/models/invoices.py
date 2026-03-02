"""
Invoice and Payment models for unified financial management.
Supports both payable (por_pagar) and receivable (por_cobrar) invoices.
"""
from datetime import date
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
import enum

from sqlalchemy import String, Integer, Text, Date, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from src.models.catalogs import Supplier, Client
    from src.models.user import User
    from src.models.trips import Trip


# ==================== ENUMS ====================

class InvoiceType(str, enum.Enum):
    """Tipo de factura"""
    POR_PAGAR = "POR_PAGAR"      # Facturas de proveedores (egresos)
    POR_COBRAR = "POR_COBRAR"    # Facturas a clientes (ingresos)


class InvoiceStatus(str, enum.Enum):
    """Estatus de factura"""
    PENDIENTE = "PENDIENTE"      # Sin pago/cobro
    PARCIAL = "PARCIAL"          # Pago/cobro parcial
    PAGADA = "PAGADA"            # Totalmente pagada/cobrada
    CANCELADA = "CANCELADA"      # Anulada


class PaymentMethod(str, enum.Enum):
    """Método de pago"""
    TRANSFERENCIA = "TRANSFERENCIA"
    CHEQUE = "CHEQUE"
    EFECTIVO = "EFECTIVO"
    TARJETA = "TARJETA"
    OTRO = "OTRO"


# ==================== MODELS ====================

class Invoice(BaseModel, TimestampMixin):
    """
    Factura unificada - puede ser por pagar (a proveedores) o por cobrar (a clientes).
    
    Relaciones:
    - Por Pagar: Liga a Supplier a través de proveedor_id
    - Por Cobrar: Liga a Client a través de cliente_id
    - Puede originarse de una PurchaseOrder (para compras)
    - En el futuro, puede originarse de un Trip/Viaje (para servicios)
    """
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Identificación
    numero_factura: Mapped[str] = mapped_column(String(100), nullable=False)
    folio_fiscal: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)  # UUID del SAT
    
    # Tipo y estado
    tipo: Mapped[InvoiceType] = mapped_column(SQLEnum(InvoiceType), nullable=False)
    estatus: Mapped[InvoiceStatus] = mapped_column(
        SQLEnum(InvoiceStatus), 
        default=InvoiceStatus.PENDIENTE
    )
    
    # Fechas
    fecha_factura: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Montos
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    iva: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    monto_pagado: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    
    # Archivos
    archivo_pdf: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    archivo_xml: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Relaciones - Proveedor (para facturas por pagar)
    proveedor_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("suppliers.id"), 
        nullable=True
    )
    proveedor: Mapped[Optional["Supplier"]] = relationship(
        "Supplier", 
        back_populates="invoices"
    )
    
    # Relaciones - Cliente (para facturas por cobrar)
    cliente_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("clients.id"), 
        nullable=True
    )
    cliente: Mapped[Optional["Client"]] = relationship(
        "Client", 
        back_populates="invoices"
    )
    
    # Origen - Orden de Compra (opcional)
    purchase_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("purchase_orders.id"), 
        nullable=True
    )
    # purchase_order relationship defined in purchases.py
    
    # Origen - Viaje/Trip
    trip_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("trips.id"), 
        nullable=True
    )
    trip: Mapped[Optional["Trip"]] = relationship(
        "Trip",
        back_populates="invoices"
    )
    
    # Metadatos
    concepto: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Pagos relacionados
    payments: Mapped[List["Payment"]] = relationship(
        "Payment", 
        back_populates="invoice",
        cascade="all, delete-orphan"
    )
    
    @property
    def saldo_pendiente(self) -> Decimal:
        """Calcula el saldo pendiente de pago/cobro"""
        return self.total - self.monto_pagado
    
    @property
    def esta_vencida(self) -> bool:
        """Verifica si la factura está vencida"""
        if self.fecha_vencimiento and self.estatus == InvoiceStatus.PENDIENTE:
            return date.today() > self.fecha_vencimiento
        return False


class Payment(BaseModel, TimestampMixin):
    """
    Pago o cobro asociado a una factura.
    Permite pagos parciales (múltiples pagos por factura).
    """
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Relación con factura
    invoice_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("invoices.id"), 
        nullable=False
    )
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payments")
    
    # Información del pago
    fecha_pago: Mapped[date] = mapped_column(Date, nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    metodo_pago: Mapped[PaymentMethod] = mapped_column(
        SQLEnum(PaymentMethod), 
        nullable=False
    )
    referencia: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Comprobante
    archivo_comprobante: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Auditoría - quién registró el pago
    usuario_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id"), 
        nullable=False
    )
    usuario: Mapped["User"] = relationship("User")
