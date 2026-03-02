from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from src.models.notifications import NotificationType, NotificationPriority

class NotificationBase(BaseModel):
    tipo: NotificationType
    titulo: str
    mensaje: str
    prioridad: NotificationPriority = NotificationPriority.media
    leida: bool = False
    usuario_id: Optional[int] = None
    referencia_tipo: Optional[str] = None
    referencia_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    leida: Optional[bool] = None

class NotificationResponse(NotificationBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
