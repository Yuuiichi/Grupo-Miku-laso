# app/__init__.py
"""
Sistema de Biblioteca Municipal - Backend
"""

# app/models/__init__.py
from app.models.ejemplar import Ejemplar

__all__ = ["Ejemplar"]

# app/schemas/__init__.py
from app.schemas.ejemplar_schema import (
    EjemplarCreate,
    EjemplarResponse,
    EjemplarEstadoUpdate,
    DisponibilidadResponse
)

__all__ = [
    "EjemplarCreate",
    "EjemplarResponse", 
    "EjemplarEstadoUpdate",
    "DisponibilidadResponse"
]

# app/api/__init__.py
"""
API Routers
"""