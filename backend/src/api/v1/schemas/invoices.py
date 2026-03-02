from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from src.models.invoices import InvoiceType, InvoiceStatus, PaymentMethod

# ==================== PAYMENTS ====================
class PaymentBase(BaseModel):
    invoice_id: int
    fecha_pago: date
    monto: float
    metodo_pago: PaymentMethod
    referencia: Optional[str] = None
    archivo_comprobante: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int
    usuario_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ==================== INVOICES ====================
class InvoiceBase(BaseModel):
    numero_factura: str
    folio_fiscal: Optional[str] = None
    tipo: InvoiceType
    estatus: InvoiceStatus = InvoiceStatus.PENDIENTE
    fecha_factura: date
    fecha_vencimiento: Optional[date] = None
    subtotal: float
    iva: float = 0.0
    total: float
    monto_pagado: float = 0.0
    archivo_pdf: Optional[str] = None
    archivo_xml: Optional[str] = None
    proveedor_id: Optional[int] = None
    cliente_id: Optional[int] = None
    purchase_order_id: Optional[int] = None
    trip_id: Optional[int] = None
    concepto: str

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    estatus: Optional[InvoiceStatus] = None
    fecha_vencimiento: Optional[date] = None
    monto_pagado: Optional[float] = None
    archivo_pdf: Optional[str] = None
    archivo_xml: Optional[str] = None

class InvoiceResponse(InvoiceBase):
    id: int
    saldo_pendiente: float
    esta_vencida: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class InvoiceExpandedResponse(InvoiceResponse):
    payments: List[PaymentResponse] = []
