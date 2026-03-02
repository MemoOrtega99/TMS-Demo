"""
Health check endpoint
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Verificar estado del servicio.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "gestion-rb-api"
    }
