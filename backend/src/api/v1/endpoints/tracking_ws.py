"""
WebSocket endpoint para tracking en tiempo real de viajes.
Usa un ConnectionManager simple en memoria (apropiado para demo).
Para producción se recomendaría Redis Pub/Sub.
"""
from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import json
from datetime import datetime

from src.core.database import get_db
from src.models.trips import Trip, TripComment, CommentType
from src.api.v1.schemas.trips import TripCommentCreate

router = APIRouter()


class TrackingConnectionManager:
    """Administra las conexiones WebSocket activas por trip_id."""
    def __init__(self):
        # trip_id -> lista de WebSockets activos
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, trip_id: int):
        await websocket.accept()
        if trip_id not in self.active_connections:
            self.active_connections[trip_id] = []
        self.active_connections[trip_id].append(websocket)
        print(f"[WS] Cliente conectado al tracking del viaje {trip_id}. Total: {len(self.active_connections[trip_id])}")

    def disconnect(self, websocket: WebSocket, trip_id: int):
        if trip_id in self.active_connections:
            self.active_connections[trip_id].discard(websocket) if hasattr(self.active_connections[trip_id], 'discard') else None
            try:
                self.active_connections[trip_id].remove(websocket)
            except ValueError:
                pass
            if not self.active_connections[trip_id]:
                del self.active_connections[trip_id]
        print(f"[WS] Cliente desconectado del viaje {trip_id}")

    async def broadcast_to_trip(self, trip_id: int, message: dict):
        """Envía un mensaje a todos los clientes conectados a un viaje."""
        if trip_id not in self.active_connections:
            return
        dead = []
        for ws in self.active_connections[trip_id]:
            try:
                await ws.send_text(json.dumps(message, default=str))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, trip_id)


# Instancia global del connection manager
manager = TrackingConnectionManager()


@router.websocket("/ws/trips/{trip_id}/tracking")
async def trip_tracking_websocket(
    websocket: WebSocket,
    trip_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket para el tracking en tiempo real de un viaje.
    - Al conectarse, envía el historial de comentarios existentes.
    - Luego escucha nuevos comentarios del cliente y los persiste + broadcast.
    
    Protocolo de mensajes:
      Cliente -> Servidor: { "mensaje": "...", "ubicacion": "...", "tipo": "actualizacion" }
      Servidor -> Cliente: { "type": "comment", "data": { ...TripCommentResponse } }
      Servidor -> Cliente: { "type": "history", "data": [ ...comentarios previos ] }
      Servidor -> Cliente: { "type": "ping" }
    """
    await manager.connect(websocket, trip_id)

    try:
        # 1. Enviar historial de comentarios existentes
        result = await db.execute(
            select(TripComment)
            .where(TripComment.trip_id == trip_id)
            .order_by(TripComment.created_at.asc())
        )
        comments = result.scalars().all()
        history = [
            {
                "id": c.id,
                "tipo": c.tipo.value if hasattr(c.tipo, 'value') else c.tipo,
                "mensaje": c.mensaje,
                "ubicacion": c.ubicacion,
                "usuario_id": c.usuario_id,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in comments
        ]
        await websocket.send_text(json.dumps({"type": "history", "data": history}))

        # 2. Escuchar mensajes entrantes y hacer broadcast
        while True:
            raw = await websocket.receive_text()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"type": "error", "message": "JSON inválido"}))
                continue

            mensaje = payload.get("mensaje", "").strip()
            if not mensaje:
                continue

            tipo_str = payload.get("tipo", "actualizacion")
            try:
                tipo = CommentType(tipo_str)
            except ValueError:
                tipo = CommentType.actualizacion

            # Persistir en base de datos
            comment = TripComment(
                trip_id=trip_id,
                usuario_id=payload.get("usuario_id"),  # opcional, sin auth para WS demo
                tipo=tipo,
                mensaje=mensaje,
                ubicacion=payload.get("ubicacion"),
                genera_notificacion=True,
            )
            db.add(comment)
            await db.commit()
            await db.refresh(comment)

            # Broadcast a todos los conectados al mismo viaje
            broadcast_msg = {
                "type": "comment",
                "data": {
                    "id": comment.id,
                    "tipo": comment.tipo.value if hasattr(comment.tipo, 'value') else comment.tipo,
                    "mensaje": comment.mensaje,
                    "ubicacion": comment.ubicacion,
                    "usuario_id": comment.usuario_id,
                    "created_at": comment.created_at.isoformat() if comment.created_at else datetime.utcnow().isoformat(),
                }
            }
            await manager.broadcast_to_trip(trip_id, broadcast_msg)

    except WebSocketDisconnect:
        manager.disconnect(websocket, trip_id)
    except Exception as e:
        print(f"[WS] Error en tracking de viaje {trip_id}: {e}")
        manager.disconnect(websocket, trip_id)


@router.get("/ws/trips/{trip_id}/tracking/connections")
async def get_trip_connections(trip_id: int):
    """Devuelve cuántos clientes están conectados al tracking de un viaje."""
    count = len(manager.active_connections.get(trip_id, []))
    return {"trip_id": trip_id, "connected_clients": count}
