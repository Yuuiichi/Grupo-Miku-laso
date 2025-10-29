# app/models/documento.py
"""
Modelo stub de Documento.
Solo lo necesario para que Ejemplar funcione.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Documento(Base):
    """
    Stub temporal del modelo Documento.
    Será reemplazado cuando se integre ROL 2.
    """
    __tablename__ = "documentos"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False, default="libro")
    titulo = Column(String(255), nullable=False, default="Sin título")
    autor = Column(String(255), nullable=False, default="Sin autor")
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)