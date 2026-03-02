"""
Pydantic schemas for inventory endpoints
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


# ==================== ENUMS ====================

class InventoryCategoryEnum(str, Enum):
    REFACCIONES = "refacciones"
    COMBUSTIBLE = "combustible"
    INSUMOS = "insumos"
    HERRAMIENTAS = "herramientas"
    LLANTAS = "llantas"
    LUBRICANTES = "lubricantes"
    OTRO = "otro"


class MovementTypeEnum(str, Enum):
    ENTRADA = "entrada"
    SALIDA = "salida"


class MovementReasonEnum(str, Enum):
    COMPRA = "compra"
    DEVOLUCION = "devolucion"
    AJUSTE = "ajuste"
    CONSUMO = "consumo"
    MANTENIMIENTO = "mantenimiento"
    OTRO = "otro"


# ==================== INVENTORY ITEM SCHEMAS ====================

class InventoryItemBase(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=50)
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    categoria: InventoryCategoryEnum
    unidad_medida: str = Field(..., min_length=1, max_length=20)
    stock_minimo: Decimal = Field(default=0, ge=0)
    stock_maximo: Optional[Decimal] = Field(None, ge=0)
    ubicacion: Optional[str] = Field(None, max_length=100)


class InventoryItemCreate(InventoryItemBase):
    stock_actual: Decimal = Field(default=0, ge=0)
    costo_promedio: Decimal = Field(default=0, ge=0)


class InventoryItemUpdate(BaseModel):
    codigo: Optional[str] = Field(None, min_length=1, max_length=50)
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = None
    categoria: Optional[InventoryCategoryEnum] = None
    unidad_medida: Optional[str] = Field(None, min_length=1, max_length=20)
    stock_minimo: Optional[Decimal] = Field(None, ge=0)
    stock_maximo: Optional[Decimal] = Field(None, ge=0)
    ubicacion: Optional[str] = Field(None, max_length=100)


class InventoryItemResponse(InventoryItemBase):
    id: int
    stock_actual: Decimal
    costo_promedio: Decimal
    ultimo_costo: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Computed
    stock_bajo: Optional[bool] = None
    valor_inventario: Optional[Decimal] = None

    class Config:
        from_attributes = True


# ==================== INVENTORY MOVEMENT SCHEMAS ====================

class InventoryMovementBase(BaseModel):
    inventory_item_id: int
    tipo: MovementTypeEnum
    razon: MovementReasonEnum
    cantidad: Decimal = Field(..., gt=0)
    fecha_movimiento: datetime
    costo_unitario: Decimal = Field(default=0, ge=0)
    referencia: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class InventoryMovementCreate(InventoryMovementBase):
    purchase_order_id: Optional[int] = None


class InventoryMovementResponse(InventoryMovementBase):
    id: int
    numero: str
    stock_resultante: Decimal
    purchase_order_id: Optional[int] = None
    usuario_id: int
    created_at: datetime
    
    # Related item info (minimal)
    item_codigo: Optional[str] = None
    item_nombre: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== SUMMARY SCHEMAS ====================

class InventorySummary(BaseModel):
    """Summary for dashboard"""
    total_productos: int
    productos_stock_bajo: int
    valor_total_inventario: Decimal
    movimientos_hoy: int


class LowStockItemResponse(BaseModel):
    """For low stock alerts"""
    id: int
    codigo: str
    nombre: str
    stock_actual: Decimal
    stock_minimo: Decimal
    unidad_medida: str
    diferencia: Decimal  # How much below minimum

    class Config:
        from_attributes = True

class InventoryItemWithMovementsResponse(InventoryItemResponse):
    movements: List[InventoryMovementResponse] = []

    class Config:
        from_attributes = True
