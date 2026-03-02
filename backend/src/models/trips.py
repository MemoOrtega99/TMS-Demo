"""
Trip models for Soluciones-TMS.
Includes Trip, TripExpense, DieselLoad, and TripComment models.
"""
from datetime import date, datetime
from typing import Optional, List, TYPE_CHECKING
import enum

from sqlalchemy import String, Integer, Text, Date, DateTime, Numeric, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from src.models.base import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from src.models.catalogs import Client, Driver
    from src.models.fleet import Vehicle, Trailer, Dolly
    from src.models.invoices import Invoice
    from src.models.user import User

# ==================== ENUMS ====================

class TripStatus(str, enum.Enum):
    programado = "programado"
    asignado = "asignado"
    en_ruta = "en_ruta"
    completado = "completado"
    cancelado = "cancelado"

class ExpenseType(str, enum.Enum):
    caseta = "caseta"
    viaticos = "viaticos"
    combustible = "combustible"
    maniobras = "maniobras"
    pension = "pension"
    estacionamiento = "estacionamiento"
    otro = "otro"

class DieselLoadType(str, enum.Enum):
    patio = "patio"
    gasolinera = "gasolinera"

class CommentType(str, enum.Enum):
    actualizacion = "actualizacion"
    incidencia = "incidencia"
    documento = "documento"
    estatus_change = "estatus_change"

# ==================== MODELS ====================

class Trip(BaseModel, TimestampMixin):
    """Viajes"""
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_viaje: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    
    # Asignación
    cliente_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("clients.id"), nullable=True)
    chofer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("drivers.id"), nullable=True)
    vehiculo_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("vehicles.id"), nullable=True)
    remolque1_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("trailers.id"), nullable=True)
    remolque2_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("trailers.id"), nullable=True)
    dolly_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("dollies.id"), nullable=True)
    
    # Ruta
    origen: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    destino: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    distancia_km: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Carga
    tipo_carga: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    peso_toneladas: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    contenedores: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Fechas
    fecha_programada: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_salida: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_entrega_estimada: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_entrega_real: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Kilometraje
    km_salida: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    km_llegada: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Facturación
    tarifa_cliente: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    estatus: Mapped[TripStatus] = mapped_column(SQLEnum(TripStatus, native_enum=False), default=TripStatus.programado)

    # Relaciones
    cliente: Mapped[Optional["Client"]] = relationship("Client")
    chofer: Mapped[Optional["Driver"]] = relationship("Driver")
    vehiculo: Mapped[Optional["Vehicle"]] = relationship("Vehicle")
    remolque1: Mapped[Optional["Trailer"]] = relationship("Trailer", foreign_keys=[remolque1_id])
    remolque2: Mapped[Optional["Trailer"]] = relationship("Trailer", foreign_keys=[remolque2_id])
    dolly: Mapped[Optional["Dolly"]] = relationship("Dolly")
    
    expenses: Mapped[List["TripExpense"]] = relationship("TripExpense", back_populates="trip", cascade="all, delete-orphan")
    diesel_loads: Mapped[List["DieselLoad"]] = relationship("DieselLoad", back_populates="trip")
    invoices: Mapped[List["Invoice"]] = relationship("Invoice", back_populates="trip")
    comments: Mapped[List["TripComment"]] = relationship("TripComment", back_populates="trip", cascade="all, delete-orphan", order_by="desc(TripComment.created_at)")


class TripExpense(BaseModel, TimestampMixin):
    """Gastos de Viaje"""
    __tablename__ = "trip_expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey("trips.id"), nullable=False)
    
    tipo_gasto: Mapped[ExpenseType] = mapped_column(SQLEnum(ExpenseType, native_enum=False), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    monto: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    fecha_gasto: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    trip: Mapped["Trip"] = relationship("Trip", back_populates="expenses")


class DieselLoad(BaseModel, TimestampMixin):
    """Cargas de Diesel"""
    __tablename__ = "diesel_loads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicles.id"), nullable=False)
    trip_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("trips.id"), nullable=True)
    chofer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("drivers.id"), nullable=True)
    
    tipo: Mapped[DieselLoadType] = mapped_column(SQLEnum(DieselLoadType, native_enum=False), nullable=False)
    litros: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    costo_por_litro: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    costo_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    km_odometro: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fecha_carga: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    vehiculo: Mapped["Vehicle"] = relationship("Vehicle")
    trip: Mapped[Optional["Trip"]] = relationship("Trip", back_populates="diesel_loads")
    chofer: Mapped[Optional["Driver"]] = relationship("Driver")


class TripComment(BaseModel, TimestampMixin):
    """Comentarios / Timeline de Tracking"""
    __tablename__ = "trip_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey("trips.id"), nullable=False)
    usuario_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    tipo: Mapped[CommentType] = mapped_column(SQLEnum(CommentType, native_enum=False), default=CommentType.actualizacion)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    ubicacion: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    genera_notificacion: Mapped[bool] = mapped_column(Boolean, default=True)

    trip: Mapped["Trip"] = relationship("Trip", back_populates="comments")
    usuario: Mapped[Optional["User"]] = relationship("User")
