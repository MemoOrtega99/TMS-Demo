"""
Modelos de usuarios, roles y permisos.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class Role(BaseModel):
    """
    Roles del sistema con permisos granulares.
    """
    __tablename__ = "roles"
    
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    
    # Permisos como lista de strings
    # ["users.read", "users.write", "drivers.read", "operations.write", ...]
    permissions = Column(JSONB, default=list)
    
    # Relación con usuarios
    users = relationship("User", back_populates="role")


class User(BaseModel):
    """
    Usuarios del sistema.
    """
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Datos personales
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True, index=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Rol
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="users")
    
    # Preferencias
    preferences = Column(JSONB, default=dict)


# Roles predefinidos del sistema (se crean en seed)
DEFAULT_ROLES = [
    {
        "name": "admin",
        "description": "Administrador del Sistema - Control Total",
        "permissions": ["*"]  # Acceso a todo
    },
    {
        "name": "coordinador",
        "description": "Coordinador de Viajes - Logística y Asignación",
        "permissions": [
            "operations.read", "operations.write",
            "drivers.read", "vehicles.read",
            "assignments.write"
        ]
    },
    {
        "name": "rastreo",
        "description": "Ejecutivo de Rastreo - Monitoreo y Evidencias",
        "permissions": [
            "operations.read", "operations.update_status",
            "expenses.write", "evidence.write"
        ]
    },
    {
        "name": "compras",
        "description": "Encargado de Compras - Abastecimiento",
        "permissions": [
            "suppliers.read", "suppliers.write",
            "purchase_orders.read", "purchase_orders.write",
            "inventory.read", "inventory.write",
            "invoices.write"
        ]
    },
    {
        "name": "diesel",
        "description": "Encargado Diesel - Combustible y Servicio",
        "permissions": [
            "vehicles.read", "vehicles.update_km",
            "fuel.read", "fuel.write"
        ]
    },
    {
        "name": "carta_porte",
        "description": "Encargado Carta Porte - Cumplimiento Fiscal",
        "permissions": [
            "operations.read",
            "carta_porte.read", "carta_porte.write"
        ]
    },
    {
        "name": "finanzas",
        "description": "CxP / CxC - Control de Facturas",
        "permissions": [
            "invoices.read", "invoices.write",
            "expenses.read", "expenses.validate",
            "reports.read"
        ]
    },
    {
        "name": "auxiliar",
        "description": "Auxiliar Contable - Documentación",
        "permissions": [
            "drivers.read", "drivers.update_documents",
            "vehicles.read", "vehicles.update_documents",
            "invoices.write"
        ]
    },
]
