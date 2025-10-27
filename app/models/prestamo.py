from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from database import Base


class Prestamo(Base):
    __tablename__ = "prestamos"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    libro_id = Column(Integer, nullable=False)  # Se vinculará con ROL 4
    
    # Estados: "prestado", "devuelto", "vencido"
    estado = Column(String(20), default="prestado", nullable=False)
    
    fecha_prestamo = Column(DateTime(timezone=True), server_default=func.now())
    fecha_devolucion_estimada = Column(DateTime(timezone=True), nullable=False)
    fecha_devolucion_real = Column(DateTime(timezone=True), nullable=True)
    
    # Información adicional
    observaciones = Column(String(500), nullable=True)
    renovaciones = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relación con Usuario
    usuario = relationship("Usuario", backref="prestamos")
    
    def esta_vencido(self) -> bool:
        """Verificar si el préstamo está vencido"""
        if self.estado == "prestado":
            return datetime.utcnow() < self.fecha_devolucion_estimada
        return False
    
    def calcular_dias_atraso(self) -> int:
        """Calcular días de atraso"""
        if self.estado == "prestado" and self.esta_vencido():
            delta = datetime.utcnow() - self.fecha_devolucion_estimada
            return max(0, delta.days)
        return 0
    
    @staticmethod
    def crear_prestamo(usuario_id: int, libro_id: int, dias_prestamo: int = 14):
        """Factory para crear nuevo préstamo"""
        return Prestamo(
            usuario_id=usuario_id,
            libro_id=libro_id,
            fecha_devolucion_estimada=datetime.utcnow() + timedelta(days=dias_prestamo)
        )