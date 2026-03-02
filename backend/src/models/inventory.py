"""
Inventory models for product and stock movement management.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
import enum

from sqlalchemy import String, Integer, Text, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.purchases import PurchaseOrder


# ==================== ENUMS ====================

class InventoryCategory(str, enum.Enum):
    """Categoría de producto en inventario"""
    REFACCIONES = "refacciones"
    COMBUSTIBLE = "combustible"
    INSUMOS = "insumos"
    HERRAMIENTAS = "herramientas"
    LLANTAS = "llantas"
    LUBRICANTES = "lubricantes"
    OTRO = "otro"


class MovementType(str, enum.Enum):
    """Tipo de movimiento de inventario"""
    ENTRADA = "entrada"    # Incrementa stock
    SALIDA = "salida"      # Decrementa stock


class MovementReason(str, enum.Enum):
    """Razón del movimiento"""
    COMPRA = "compra"              # Entrada por compra
    DEVOLUCION = "devolucion"      # Devolución a proveedor o de cliente
    AJUSTE = "ajuste"              # Ajuste de inventario
    CONSUMO = "consumo"            # Uso interno
    MANTENIMIENTO = "mantenimiento"  # Para mantenimiento de unidades
    OTRO = "otro"


# ==================== MODELS ====================

class InventoryItem(BaseModel, TimestampMixin):
    """
    Producto en inventario - catálogo de productos con control de stock.
    """
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Identificación
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Clasificación
    categoria: Mapped[InventoryCategory] = mapped_column(
        SQLEnum(InventoryCategory, values_callable=lambda obj: [e.value for e in obj]), 
        nullable=False
    )
    
    # Unidad de medida
    unidad_medida: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Stock
    stock_actual: Mapped[Decimal] = mapped_column(Numeric(14, 3), default=0)
    stock_minimo: Mapped[Decimal] = mapped_column(Numeric(14, 3), default=0)
    stock_maximo: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 3), nullable=True)
    
    # Ubicación
    ubicacion: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Costos
    costo_promedio: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    ultimo_costo: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    
    # Movimientos
    movements: Mapped[List["InventoryMovement"]] = relationship(
        "InventoryMovement", 
        back_populates="inventory_item"
    )
    
    @property
    def stock_bajo(self) -> bool:
        """Verifica si el stock está por debajo del mínimo"""
        return self.stock_actual < self.stock_minimo
    
    @property
    def valor_inventario(self) -> Decimal:
        """Calcula el valor del inventario (stock * costo promedio)"""
        return self.stock_actual * self.costo_promedio


class InventoryMovement(BaseModel, TimestampMixin):
    """
    Movimiento de inventario - entrada o salida de productos.
    """
    __tablename__ = "inventory_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Identificación
    numero: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    
    # Producto
    inventory_item_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("inventory_items.id"), 
        nullable=False
    )
    inventory_item: Mapped["InventoryItem"] = relationship(
        "InventoryItem", 
        back_populates="movements"
    )
    
    # Tipo de movimiento
    tipo: Mapped[MovementType] = mapped_column(
        SQLEnum(MovementType, values_callable=lambda obj: [e.value for e in obj]), 
        nullable=False
    )
    razon: Mapped[MovementReason] = mapped_column(
        SQLEnum(MovementReason, values_callable=lambda obj: [e.value for e in obj]), 
        nullable=False
    )
    
    # Cantidad
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    
    # Fecha y hora del movimiento
    fecha_movimiento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Costo unitario al momento del movimiento
    costo_unitario: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    
    # Stock después del movimiento (snapshot)
    stock_resultante: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    
    # Origen - Orden de compra (para entradas de compras)
    purchase_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("purchase_orders.id"), 
        nullable=True
    )
    purchase_order: Mapped[Optional["PurchaseOrder"]] = relationship(
        "PurchaseOrder", 
        back_populates="inventory_movements"
    )
    
    # Referencia externa
    referencia: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Usuario que registró
    usuario_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id"), 
        nullable=False
    )
    usuario: Mapped["User"] = relationship("User")
