"""
Modelo base con campos de auditoría para todas las entidades.
Diseño IA-Ready: incluye campos para cache de embeddings.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, DateTime, Boolean, String, func
from sqlalchemy.dialects.postgresql import JSONB

from src.core.database import Base


class BaseModel(Base):
    """
    Clase base para todos los modelos.
    Incluye campos de auditoría y soporte para IA.
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Auditoría temporal
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now()
    )
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)
    
    # Metadatos flexibles
    tags = Column(JSONB, default=list)
    notes = Column(String, nullable=True)
    
    # IA-Ready: Cache de embeddings
    content_hash = Column(String(64), nullable=True)
    embedding_updated_at = Column(DateTime(timezone=True), nullable=True)


class TimestampMixin:
    """Mixin para solo timestamps sin soft delete"""
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now()
    )
