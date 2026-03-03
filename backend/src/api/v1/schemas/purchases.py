"""
Pydantic schemas for purchase endpoints (requisitions and purchase orders)
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


# ==================== ENUMS ====================

class RequisitionStatusEnum(str, Enum):
    BORRADOR = "borrador"
    PENDIENTE = "pendiente"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    COMPLETADA = "completada"


class PurchaseOrderStatusEnum(str, Enum):
    PENDIENTE = "pendiente"
    ENVIADA = "enviada"
    PARCIAL = "parcial"
    RECIBIDA = "recibida"
    CANCELADA = "cancelada"


# ==================== REQUISITION ITEM SCHEMAS ====================

class RequisitionItemBase(BaseModel):
    descripcion: str = Field(..., min_length=1, max_length=500)
    cantidad: Decimal = Field(..., gt=0)
    unidad: str = Field(..., min_length=1, max_length=20)
    precio_estimado: Optional[Decimal] = Field(None, ge=0)
    inventory_item_id: Optional[int] = None


class RequisitionItemCreate(RequisitionItemBase):
    pass


class RequisitionItemUpdate(BaseModel):
    descripcion: Optional[str] = Field(None, min_length=1, max_length=500)
    cantidad: Optional[Decimal] = Field(None, gt=0)
    unidad: Optional[str] = Field(None, min_length=1, max_length=20)
    precio_estimado: Optional[Decimal] = Field(None, ge=0)
    inventory_item_id: Optional[int] = None


class RequisitionItemResponse(RequisitionItemBase):
    id: int
    requisition_id: int

    class Config:
        from_attributes = True


# ==================== REQUISITION SCHEMAS ====================

class RequisitionBase(BaseModel):
    fecha: date
    fecha_requerida: Optional[date] = None
    proveedor_id: Optional[int] = None
    notes: Optional[str] = None


class RequisitionCreate(RequisitionBase):
    items: List[RequisitionItemCreate] = []


class RequisitionUpdate(BaseModel):
    fecha: Optional[date] = None
    fecha_requerida: Optional[date] = None
    proveedor_id: Optional[int] = None
    estatus: Optional[RequisitionStatusEnum] = None
    notes: Optional[str] = None


class RequisitionResponse(RequisitionBase):
    id: int
    numero: str
    solicitante_id: int
    estatus: RequisitionStatusEnum
    total_estimado: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RequisitionWithItemsResponse(RequisitionResponse):
    items: List[RequisitionItemResponse] = []
    proveedor_nombre: Optional[str] = None
    solicitante_nombre: Optional[str] = None


# ==================== PURCHASE ORDER ITEM SCHEMAS ====================

class PurchaseOrderItemBase(BaseModel):
    descripcion: str = Field(..., min_length=1, max_length=500)
    cantidad: Decimal = Field(..., gt=0)
    unidad: str = Field(..., min_length=1, max_length=20)
    precio_unitario: Decimal = Field(..., ge=0)
    inventory_item_id: Optional[int] = None


class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass


class PurchaseOrderItemUpdate(BaseModel):
    descripcion: Optional[str] = Field(None, min_length=1, max_length=500)
    cantidad: Optional[Decimal] = Field(None, gt=0)
    unidad: Optional[str] = Field(None, min_length=1, max_length=20)
    precio_unitario: Optional[Decimal] = Field(None, ge=0)
    cantidad_recibida: Optional[Decimal] = Field(None, ge=0)


class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    id: int
    purchase_order_id: int
    cantidad_recibida: Decimal
    
    # Computed
    subtotal: Optional[Decimal] = None
    pendiente_recibir: Optional[Decimal] = None

    class Config:
        from_attributes = True


# ==================== PURCHASE ORDER SCHEMAS ====================

class PurchaseOrderBase(BaseModel):
    proveedor_id: int
    fecha_orden: date
    fecha_entrega_esperada: Optional[date] = None
    notes: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    """Create PO from approved requisition"""
    requisition_id: int
    items: List[PurchaseOrderItemCreate] = []
    subtotal: Decimal = Field(..., ge=0)
    iva: Decimal = Field(default=0, ge=0)
    total: Decimal = Field(..., ge=0)


class PurchaseOrderSimpleCreate(BaseModel):
    """Direct creation of PO without requisition"""
    numero_orden: str
    proveedor_id: int
    fecha_orden: date
    fecha_entrega: Optional[date] = None
    total: Decimal
    items: int  # count
    estatus: PurchaseOrderStatusEnum = PurchaseOrderStatusEnum.PENDIENTE


class PurchaseOrderUpdate(BaseModel):
    fecha_entrega_esperada: Optional[date] = None
    fecha_entrega_real: Optional[date] = None
    estatus: Optional[PurchaseOrderStatusEnum] = None
    notes: Optional[str] = None


class PurchaseOrderResponse(PurchaseOrderBase):
    id: int
    numero: str
    requisition_id: int
    fecha_entrega_real: Optional[date] = None
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    estatus: PurchaseOrderStatusEnum
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PurchaseOrderWithDetailsResponse(PurchaseOrderResponse):
    items: List[PurchaseOrderItemResponse] = []
    proveedor_nombre: Optional[str] = None
    requisition_numero: Optional[str] = None


# ==================== RECEIVE SCHEMA ====================

class ReceiveItemSchema(BaseModel):
    """For receiving items into inventory"""
    purchase_order_item_id: int
    cantidad_recibida: Decimal = Field(..., gt=0)
    costo_unitario: Optional[Decimal] = None


class ReceiveOrderSchema(BaseModel):
    """Receive items from a purchase order"""
    items: List[ReceiveItemSchema]
    notas: Optional[str] = None
