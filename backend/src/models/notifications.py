"""
Notification models for Soluciones-TMS
"""
from typing import Optional
import enum

from sqlalchemy import String, Integer, Text, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel, TimestampMixin

class NotificationType(str, enum.Enum):
    factura_vencida = "factura_vencida"
    factura_por_vencer = "factura_por_vencer"
    viaje_programado = "viaje_programado"
    viaje_en_ruta = "viaje_en_ruta"
    viaje_completado = "viaje_completado"
    tracking_update = "tracking_update"
    stock_bajo = "stock_bajo"
    servicio_proximo = "servicio_proximo"

class NotificationPriority(str, enum.Enum):
    baja = "baja"
    media = "media"
    alta = "alta"
    urgente = "urgente"

class Notification(BaseModel, TimestampMixin):
    """Notificaciones del sistema"""
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType, native_enum=False), nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    prioridad: Mapped[NotificationPriority] = mapped_column(SQLEnum(NotificationPriority, native_enum=False), default=NotificationPriority.media)
    leida: Mapped[bool] = mapped_column(Boolean, default=False)
    
    usuario_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    referencia_tipo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'invoice', 'trip', 'vehicle', 'inventory'
    referencia_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    usuario: Mapped[Optional["User"]] = relationship("User")
