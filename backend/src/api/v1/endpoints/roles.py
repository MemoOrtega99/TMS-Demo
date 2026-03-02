"""
Roles CRUD endpoints
"""
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core import get_db
from src.models import User, Role
from src.api.v1.endpoints.auth import get_current_user, require_permission

router = APIRouter()


# === Schemas ===

class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    
    class Config:
        from_attributes = True


class RoleUpdate(BaseModel):
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


# === Endpoints ===

@router.get("", response_model=List[RoleResponse])
async def list_roles(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Listar todos los roles (cualquier usuario autenticado — se usa en dropdowns).
    """
    result = await db.execute(
        select(Role).where(Role.is_deleted == False).order_by(Role.name)
    )
    return result.scalars().all()


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener rol por ID.
    """
    result = await db.execute(
        select(Role).where(Role.id == role_id, Role.is_deleted == False)
    )
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    return role


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_in: RoleUpdate,
    current_user: Annotated[User, Depends(require_permission("users.write"))],
    db: AsyncSession = Depends(get_db),
):
    """
    Actualizar rol (solo admin — requiere users.write).
    No se permite modificar el nombre para evitar romper referencias.
    """
    result = await db.execute(
        select(Role).where(Role.id == role_id, Role.is_deleted == False)
    )
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Admin role can't have permissions removed
    if role.name == "admin" and role_in.permissions is not None and "*" not in role_in.permissions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede quitar el acceso total al rol admin"
        )
    
    update_data = role_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(role, field, value)
    
    await db.commit()
    await db.refresh(role)
    
    return role
