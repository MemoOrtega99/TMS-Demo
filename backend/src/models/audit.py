"""
Modelos de auditoría y eventos del sistema.
Fundamentales para análisis IA y trazabilidad.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB

from src.core.database import Base


class AuditLog(Base):
    """
    Registro de todas las acciones del sistema.
    Usado para análisis de comportamiento e IA.
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=func.now(), index=True)
    
    # Usuario que realizó la acción
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Acción realizada
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, VIEW, LOGIN, etc.
    
    # Entidad afectada
    entity_type = Column(String(50), index=True)  # user, driver, vehicle, operation, etc.
    entity_id = Column(Integer, nullable=True)
    
    # Detalle de cambios
    changes = Column(JSONB, nullable=True)  # {field: {old: x, new: y}}
    
    # Contexto
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    extra = Column(JSONB, nullable=True)  # Metadatos adicionales


class SystemEvent(Base):
    """
    Eventos del sistema para procesamiento asíncrono.
    La IA puede suscribirse a estos eventos para reaccionar.
    """
    __tablename__ = "system_events"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Tipo de evento
    event_type = Column(String(100), nullable=False, index=True)
    # Ejemplos:
    # - operation.created
    # - operation.completed
    # - vehicle.maintenance_due
    # - cost.threshold_exceeded
    # - document.uploaded
    
    # Payload del evento
    payload = Column(JSONB, nullable=False)
    
    # Estado de procesamiento
    processed = Column(Boolean, default=False, index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)
