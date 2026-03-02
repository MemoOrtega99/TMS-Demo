from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from src.models.fleet import VehicleType, VehicleStatus, TrailerType, UnitStatus, ServiceType

# ==================== VEHICLES ====================
class VehicleBase(BaseModel):
    numero_economico: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    placas: Optional[str] = None
    numero_serie: Optional[str] = None
    tipo_vehiculo: VehicleType = VehicleType.TRACTO
    capacidad_tanque: Optional[float] = None
    km_actual: Optional[int] = 0
    chofer_id: Optional[int] = None
    estatus: VehicleStatus = VehicleStatus.DISPONIBLE
    proximo_servicio_km: Optional[int] = None
    fecha_proximo_servicio: Optional[date] = None

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    numero_economico: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    placas: Optional[str] = None
    numero_serie: Optional[str] = None
    tipo_vehiculo: Optional[VehicleType] = None
    capacidad_tanque: Optional[float] = None
    km_actual: Optional[int] = None
    chofer_id: Optional[int] = None
    estatus: Optional[VehicleStatus] = None
    proximo_servicio_km: Optional[int] = None
    fecha_proximo_servicio: Optional[date] = None

class VehicleResponse(VehicleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ==================== TRAILERS ====================
class TrailerBase(BaseModel):
    numero_economico: str
    tipo: TrailerType
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    placas: Optional[str] = None
    capacidad_carga_ton: Optional[float] = None
    estatus: UnitStatus = UnitStatus.DISPONIBLE

class TrailerCreate(TrailerBase):
    pass

class TrailerUpdate(BaseModel):
    numero_economico: Optional[str] = None
    tipo: Optional[TrailerType] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    placas: Optional[str] = None
    capacidad_carga_ton: Optional[float] = None
    estatus: Optional[UnitStatus] = None

class TrailerResponse(TrailerBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ==================== DOLLIES ====================
class DollyBase(BaseModel):
    numero_economico: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    placas: Optional[str] = None
    estatus: UnitStatus = UnitStatus.DISPONIBLE

class DollyCreate(DollyBase):
    pass

class DollyUpdate(BaseModel):
    numero_economico: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    placas: Optional[str] = None
    estatus: Optional[UnitStatus] = None

class DollyResponse(DollyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ==================== VEHICLE SERVICES ====================
class VehicleServiceBase(BaseModel):
    vehicle_id: int
    tipo_servicio: ServiceType
    descripcion: Optional[str] = None
    km_servicio: int
    fecha_servicio: date
    costo: Optional[float] = None
    proveedor: Optional[str] = None
    proximo_servicio_km: Optional[int] = None

class VehicleServiceCreate(VehicleServiceBase):
    pass

class VehicleServiceUpdate(BaseModel):
    tipo_servicio: Optional[ServiceType] = None
    descripcion: Optional[str] = None
    km_servicio: Optional[int] = None
    fecha_servicio: Optional[date] = None
    costo: Optional[float] = None
    proveedor: Optional[str] = None
    proximo_servicio_km: Optional[int] = None

class VehicleServiceResponse(VehicleServiceBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
