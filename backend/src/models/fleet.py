"""
Fleet models for Soluciones-TMS
"""
from datetime import date
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, Date, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

if TYPE_CHECKING:
    from src.models.catalogs import Driver

from src.models.base import BaseModel, TimestampMixin

# ==================== ENUMS ====================

class VehicleType(str, enum.Enum):
    TRACTO = "TRACTO"
    TORTON = "TORTON"
    RABON = "RABON"

class VehicleStatus(str, enum.Enum):
    DISPONIBLE = "DISPONIBLE"
    EN_RUTA = "EN_RUTA"
    TALLER = "TALLER"
    BAJA = "BAJA"

class TrailerType(str, enum.Enum):
    CAJA_SECA = "CAJA_SECA"
    PLATAFORMA = "PLATAFORMA"
    REFRIGERADO = "REFRIGERADO"
    TANQUE = "TANQUE"

class UnitStatus(str, enum.Enum):
    DISPONIBLE = "DISPONIBLE"
    EN_USO = "EN_USO"
    TALLER = "TALLER"
    BAJA = "BAJA"

class ServiceType(str, enum.Enum):
    PREVENTIVO = "PREVENTIVO"
    CORRECTIVO = "CORRECTIVO"
    LLANTAS = "LLANTAS"
    AFINACION = "AFINACION"

# ==================== MODELS ====================

class Vehicle(BaseModel, TimestampMixin):
    """Unidades (Tractocamiones)"""
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_economico: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    
    marca: Mapped[str] = mapped_column(String(50), nullable=True)
    modelo: Mapped[str] = mapped_column(String(50), nullable=True)
    anio: Mapped[int] = mapped_column(Integer, nullable=True)
    placas: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    numero_serie: Mapped[str] = mapped_column(String(50), nullable=True)
    
    tipo_vehiculo: Mapped[VehicleType] = mapped_column(SQLEnum(VehicleType, native_enum=False), default=VehicleType.TRACTO)
    capacidad_tanque: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    km_actual: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    
    chofer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("drivers.id"), nullable=True)
    estatus: Mapped[VehicleStatus] = mapped_column(SQLEnum(VehicleStatus, native_enum=False), default=VehicleStatus.DISPONIBLE)
    
    proximo_servicio_km: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fecha_proximo_servicio: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    chofer: Mapped[Optional["Driver"]] = relationship("Driver", back_populates="vehicles")
    services: Mapped[List["VehicleService"]] = relationship("VehicleService", back_populates="vehicle", cascade="all, delete-orphan")


class VehicleService(BaseModel, TimestampMixin):
    """Historial de mantenimiento de unidades"""
    __tablename__ = "vehicle_services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicles.id"), nullable=False)
    
    tipo_servicio: Mapped[ServiceType] = mapped_column(SQLEnum(ServiceType, native_enum=False), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    km_servicio: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_servicio: Mapped[date] = mapped_column(Date, nullable=False)
    
    costo: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    proveedor: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    proximo_servicio_km: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="services")


class Trailer(BaseModel, TimestampMixin):
    """Remolques"""
    __tablename__ = "trailers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_economico: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    tipo: Mapped[TrailerType] = mapped_column(SQLEnum(TrailerType, native_enum=False), nullable=False)
    
    marca: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    modelo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    anio: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    placas: Mapped[str] = mapped_column(String(15), nullable=True)
    
    capacidad_carga_ton: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    estatus: Mapped[UnitStatus] = mapped_column(SQLEnum(UnitStatus, native_enum=False), default=UnitStatus.DISPONIBLE)


class Dolly(BaseModel, TimestampMixin):
    """Dollies"""
    __tablename__ = "dollies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_economico: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    
    marca: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    modelo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    anio: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    placas: Mapped[str] = mapped_column(String(15), nullable=True)
    
    estatus: Mapped[UnitStatus] = mapped_column(SQLEnum(UnitStatus, native_enum=False), default=UnitStatus.DISPONIBLE)
