"""
Catalog models for Soluciones-TMS
"""
from datetime import date
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, Date, Numeric, Enum as SQLEnum, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

if TYPE_CHECKING:
    from src.models.invoices import Invoice
    from src.models.purchases import PurchaseOrder
    from src.models.fleet import Vehicle

from src.models.base import BaseModel, TimestampMixin

# ==================== ENUMS ====================

class DriverStatus(str, enum.Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    VACACIONES = "VACACIONES"

class ClientStatus(str, enum.Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    SUSPENDIDO = "SUSPENDIDO"

class SupplierType(str, enum.Enum):
    COMBUSTIBLE = "COMBUSTIBLE"
    REFACCIONES = "REFACCIONES"
    SERVICIOS = "SERVICIOS"
    CASETAS = "CASETAS"
    OTRO = "OTRO"

class SupplierStatus(str, enum.Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"

# ==================== MODELS ====================

class Driver(BaseModel, TimestampMixin):
    """Operadores"""
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    licencia_numero: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    licencia_tipo: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    licencia_vigencia: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    fecha_ingreso: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    salario_base: Mapped[Optional[float]] = mapped_column(Numeric(10,2), nullable=True)
    
    apto_medico: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    apto_medico_vigencia: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    estatus: Mapped[DriverStatus] = mapped_column(SQLEnum(DriverStatus, native_enum=False), default=DriverStatus.ACTIVO)
    foto: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    vehicles: Mapped[list["Vehicle"]] = relationship("Vehicle", back_populates="chofer")


class Client(BaseModel, TimestampMixin):
    """Clientes"""
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    rfc: Mapped[str] = mapped_column(String(13), nullable=False)
    direccion: Mapped[str] = mapped_column(Text, nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    contacto_nombre: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    dias_credito: Mapped[Optional[int]] = mapped_column(Integer, default=30, nullable=True)
    limite_credito: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    estatus: Mapped[ClientStatus] = mapped_column(SQLEnum(ClientStatus, native_enum=False), default=ClientStatus.ACTIVO)

    invoices: Mapped[List["Invoice"]] = relationship("Invoice", back_populates="cliente")


class Supplier(BaseModel, TimestampMixin):
    """Proveedores"""
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    rfc: Mapped[Optional[str]] = mapped_column(String(13), nullable=True)
    tipo: Mapped[SupplierType] = mapped_column(SQLEnum(SupplierType, native_enum=False), nullable=False)
    direccion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    contacto_nombre: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    estatus: Mapped[SupplierStatus] = mapped_column(SQLEnum(SupplierStatus, native_enum=False), default=SupplierStatus.ACTIVO)

    invoices: Mapped[List["Invoice"]] = relationship("Invoice", back_populates="proveedor")
    purchase_orders: Mapped[List["PurchaseOrder"]] = relationship("PurchaseOrder", back_populates="proveedor")
