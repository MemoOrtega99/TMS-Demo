"""
Endpoints for Notifications
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.api.v1.endpoints.auth import get_current_user
from src.models.user import User
from src.models.notifications import Notification
from src.api.v1.schemas.notifications import NotificationResponse, NotificationUpdate
from src.api.v1.schemas.pagination import PaginatedResponse

router = APIRouter()

@router.get("/notifications", response_model=PaginatedResponse[NotificationResponse], tags=["Notificaciones"])
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Notification).where(Notification.usuario_id == current_user.id)
    count_query = select(func.count()).select_from(Notification).where(Notification.usuario_id == current_user.id)
    
    if unread_only:
        query = query.where(Notification.leida == False)
        count_query = count_query.where(Notification.leida == False)
        
    total = await db.scalar(count_query)
    query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=items,
        total=total if total else 0,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )

@router.get("/notifications/unread-count", tags=["Notificaciones"])
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(func.count()).select_from(Notification).where(
        Notification.usuario_id == current_user.id,
        Notification.leida == False
    )
    count = await db.scalar(query)
    return {"unread_count": count or 0}

@router.put("/notifications/{notification_id}/read", response_model=NotificationResponse, tags=["Notificaciones"])
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Notification).where(
        Notification.id == notification_id, 
        Notification.usuario_id == current_user.id
    ))
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
        
    notification.leida = True
    await db.commit()
    await db.refresh(notification)
    return notification

@router.put("/notifications/read-all", tags=["Notificaciones"])
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = update(Notification).where(
        Notification.usuario_id == current_user.id,
        Notification.leida == False
    ).values(leida=True)
    
    await db.execute(stmt)
    await db.commit()
    
    return {"message": "Todas las notificaciones han sido marcadas como leídas"}
