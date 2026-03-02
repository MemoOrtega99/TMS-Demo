"""
Users CRUD endpoints
"""
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.core import get_db, get_password_hash
from src.models import User, Role
from src.api.v1.endpoints.auth import get_current_user, require_permission

router = APIRouter()


# === Schemas ===

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None
    role_id: int


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class RoleInfo(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    phone: Optional[str]
    role_id: int
    role: Optional[RoleInfo] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    pages: int


# === Endpoints ===

@router.get("", response_model=UserListResponse)
async def list_users(
    current_user: Annotated[User, Depends(require_permission("users.read"))],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
):
    """
    Listar usuarios con paginación (requiere users.read).
    """
    query = select(User).options(selectinload(User.role)).where(User.is_deleted == False)
    
    if search:
        query = query.where(
            (User.name.ilike(f"%{search}%")) | 
            (User.email.ilike(f"%{search}%"))
        )
    
    # Total
    count_query = select(func.count()).select_from(
        select(User).where(User.is_deleted == False).subquery()
    )
    if search:
        count_query = select(func.count()).select_from(
            select(User).where(
                User.is_deleted == False,
                (User.name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
            ).subquery()
        )
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Paginación
    query = query.order_by(User.name).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return UserListResponse(
        items=users,
        total=total,
        page=page,
        pages=(total + size - 1) // size
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: Annotated[User, Depends(require_permission("users.read"))],
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener usuario por ID (requiere users.read).
    """
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    current_user: Annotated[User, Depends(require_permission("users.write"))],
    db: AsyncSession = Depends(get_db),
):
    """
    Crear nuevo usuario (requiere users.write).
    """
    # Verificar email único
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verificar rol existe
    result = await db.execute(select(Role).where(Role.id == user_in.role_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role not found"
        )
    
    # Crear usuario
    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        name=user_in.name,
        phone=user_in.phone,
        role_id=user_in.role_id,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Reload with role
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user.id)
    )
    user = result.scalar_one()
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: Annotated[User, Depends(require_permission("users.write"))],
    db: AsyncSession = Depends(get_db),
):
    """
    Actualizar usuario (requiere users.write).
    """
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Actualizar campos
    update_data = user_in.model_dump(exclude_unset=True)
    
    # Handle password change
    if "password" in update_data and update_data["password"]:
        user.password_hash = get_password_hash(update_data.pop("password"))
    elif "password" in update_data:
        update_data.pop("password")
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: Annotated[User, Depends(require_permission("users.write"))],
    db: AsyncSession = Depends(get_db),
):
    """
    Eliminar usuario — soft delete (requiere users.write).
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propia cuenta"
        )
    
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Soft delete
    user.is_deleted = True
    user.deleted_by = current_user.id
    
    await db.commit()
    
    return None
