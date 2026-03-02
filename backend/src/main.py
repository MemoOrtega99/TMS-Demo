"""
ERP Transportista - Backend API
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from src.core.config import settings
from src.api.v1 import router as api_v1_router

app = FastAPI(
    title="ERP Transportista API",
    description="Sistema ERP integral para empresa transportista",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

from fastapi.staticfiles import StaticFiles
import os

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    err_str = str(exc)
    if "ForeignKeyViolationError" in err_str or "violates foreign key constraint" in err_str:
        return JSONResponse(
            status_code=409,
            content={"detail": "No se puede eliminar este registro porque está siendo utilizado en otras partes del sistema."}
        )
    return JSONResponse(
        status_code=400,
        content={"detail": "Error de integridad relacional en la base de datos (posible duplicado o registro en uso)."}
    )

# Routers
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "gestion-rb-backend"
    }
