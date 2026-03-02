from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime
from src.models.catalogs import DriverStatus, ClientStatus, SupplierType, SupplierStatus

# ==================== DRIVERS ====================

class DriverBase(BaseModel):
    nombre: str
    apellido: str
    telefono: str
    email: Optional[EmailStr] = None
    licencia_numero: Optional[str] = None
    licencia_tipo: Optional[str] = None
    licencia_vigencia: Optional[date] = None
    fecha_ingreso: Optional[date] = None
    salario_base: Optional[float] = None
    apto_medico: Optional[str] = None
    apto_medico_vigencia: Optional[date] = None
    estatus: DriverStatus = DriverStatus.ACTIVO
    foto: Optional[str] = None

class DriverCreate(DriverBase):
    pass

class DriverUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    licencia_numero: Optional[str] = None
    licencia_tipo: Optional[str] = None
    licencia_vigencia: Optional[date] = None
    fecha_ingreso: Optional[date] = None
    salario_base: Optional[float] = None
    apto_medico: Optional[str] = None
    apto_medico_vigencia: Optional[date] = None
    estatus: Optional[DriverStatus] = None
    foto: Optional[str] = None

class DriverResponse(DriverBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== CLIENTS ====================

class ClientBase(BaseModel):
    nombre: str
    rfc: str
    direccion: str
    telefono: str
    email: Optional[EmailStr] = None
    contacto_nombre: Optional[str] = None
    dias_credito: Optional[int] = 30
    limite_credito: Optional[float] = None
    estatus: ClientStatus = ClientStatus.ACTIVO

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    nombre: Optional[str] = None
    rfc: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    contacto_nombre: Optional[str] = None
    dias_credito: Optional[int] = None
    limite_credito: Optional[float] = None
    estatus: Optional[ClientStatus] = None

class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== SUPPLIERS ====================

class SupplierBase(BaseModel):
    nombre: str
    rfc: Optional[str] = None
    tipo: SupplierType
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    contacto_nombre: Optional[str] = None
    estatus: SupplierStatus = SupplierStatus.ACTIVO

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    nombre: Optional[str] = None
    rfc: Optional[str] = None
    tipo: Optional[SupplierType] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    contacto_nombre: Optional[str] = None
    estatus: Optional[SupplierStatus] = None

class SupplierResponse(SupplierBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
