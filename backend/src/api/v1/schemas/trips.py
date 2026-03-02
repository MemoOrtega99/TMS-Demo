from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from src.models.trips import TripStatus, ExpenseType, DieselLoadType, CommentType

# ==================== TRIP COMMENTS ====================
class TripCommentBase(BaseModel):
    trip_id: int
    usuario_id: Optional[int] = None
    tipo: CommentType = CommentType.actualizacion
    mensaje: str
    ubicacion: Optional[str] = None
    genera_notificacion: bool = True

class TripCommentCreate(TripCommentBase):
    pass

class TripCommentResponse(TripCommentBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ==================== TRIP EXPENSES ====================
class TripExpenseBase(BaseModel):
    trip_id: int
    tipo_gasto: ExpenseType
    descripcion: Optional[str] = None
    monto: float
    fecha_gasto: Optional[date] = None

class TripExpenseCreate(TripExpenseBase):
    pass

class TripExpenseResponse(TripExpenseBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ==================== DIESEL LOADS ====================
class DieselLoadBase(BaseModel):
    vehicle_id: int
    trip_id: Optional[int] = None
    chofer_id: Optional[int] = None
    tipo: DieselLoadType
    litros: float
    costo_por_litro: Optional[float] = None
    costo_total: float
    km_odometro: Optional[int] = None
    fecha_carga: datetime

class DieselLoadCreate(DieselLoadBase):
    pass

class DieselLoadResponse(DieselLoadBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ==================== TRIPS ====================
class TripBase(BaseModel):
    numero_viaje: str
    cliente_id: Optional[int] = None
    chofer_id: Optional[int] = None
    vehiculo_id: Optional[int] = None
    remolque1_id: Optional[int] = None
    remolque2_id: Optional[int] = None
    dolly_id: Optional[int] = None
    origen: Optional[str] = None
    destino: Optional[str] = None
    distancia_km: Optional[int] = None
    tipo_carga: Optional[str] = None
    peso_toneladas: Optional[float] = None
    contenedores: Optional[List[str]] = None
    fecha_programada: Optional[date] = None
    fecha_salida: Optional[datetime] = None
    fecha_entrega_estimada: Optional[date] = None
    fecha_entrega_real: Optional[datetime] = None
    km_salida: Optional[int] = None
    km_llegada: Optional[int] = None
    tarifa_cliente: Optional[float] = None
    estatus: TripStatus = TripStatus.programado

class TripCreate(TripBase):
    pass

class TripUpdate(BaseModel):
    estatus: Optional[TripStatus] = None
    chofer_id: Optional[int] = None
    vehiculo_id: Optional[int] = None
    remolque1_id: Optional[int] = None
    remolque2_id: Optional[int] = None
    dolly_id: Optional[int] = None
    fecha_salida: Optional[datetime] = None
    fecha_entrega_real: Optional[datetime] = None
    km_salida: Optional[int] = None
    km_llegada: Optional[int] = None
    tarifa_cliente: Optional[float] = None

class TripResponse(TripBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TripExpandedResponse(TripResponse):
    expenses: List[TripExpenseResponse] = []
    diesel_loads: List[DieselLoadResponse] = []
    comments: List[TripCommentResponse] = []
