from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
import re
import logging

from database import get_db
from models.usuario import Usuario
from utils.auth import get_current_user
from utils.validators import validar_password_fuerte

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Autenticación Avanzada"])

class CambiarPasswordRequest(BaseModel):
    password_actual: str
    password_nueva: str
    
    @validator('password_nueva')
    def validar_password_nueva(cls, v, values):
        if 'password_actual' in values and v == values['password_actual']:
            raise ValueError('La nueva contraseña debe ser diferente a la actual')
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v


class PerfilResponse(BaseModel):
    id: int
    rut: str
    nombres: str
    apellidos: str
    email: str
    rol: str
    activo: bool
    foto_url: str | None
    sancionado: bool
    fecha_sancion_hasta: str | None
    
    class Config:
        from_attributes = True
        

@router.get("/me", response_model=dict)
async def ver_perfil(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ver perfil del usuario actual
    Incluye información de sanciones y estado
    """
    from models.prestamo import Prestamo
    
    # Contar préstamos activos
    prestamos_activos = db.query(Prestamo).filter(
        Prestamo.usuario_id == current_user.id,
        Prestamo.estado == "prestado"
    ).count()
    
    # Verificar préstamos vencidos
    prestamos_vencidos = db.query(Prestamo).filter(
        Prestamo.usuario_id == current_user.id,
        Prestamo.estado == "prestado",
        Prestamo.fecha_devolucion_estimada < db.func.now()
    ).count()
    
    sancionado = current_user.esta_sancionado()
    
    return {
        "success": True,
        "data": {
            "usuario": {
                "id": current_user.id,
                "rut": current_user.rut,
                "nombres": current_user.nombres,
                "apellidos": current_user.apellidos,
                "email": current_user.email,
                "rol": current_user.rol,
                "activo": current_user.activo,
                "foto_url": current_user.foto_url
            },
            "estado": {
                "sancionado": sancionado,
                "fecha_sancion_hasta": current_user.fecha_sancion_hasta.isoformat() if sancionado else None,
                "prestamos_activos": prestamos_activos,
                "prestamos_vencidos": prestamos_vencidos,
                "puede_prestar": prestamos_activos < 3 and prestamos_vencidos == 0 and not sancionado
            }
        }
    }


@router.post("/change-password", response_model=dict)
async def cambiar_password(
    cambio_data: CambiarPasswordRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cambiar contraseña del usuario actual
    Requiere contraseña actual para validación
    """
    # Verificar contraseña actual
    if not current_user.verify_password(cambio_data.password_actual):
        logger.warning(f"Intento fallido de cambio de contraseña para usuario {current_user.rut}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña actual incorrecta"
        )
    
    # Validar fortaleza de nueva contraseña
    es_fuerte, mensaje = validar_password_fuerte(cambio_data.password_nueva)
    if not es_fuerte:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=mensaje
        )
    
    # Actualizar contraseña
    current_user.set_password(cambio_data.password_nueva)
    db.commit()
    
    logger.info(f"Contraseña cambiada exitosamente para usuario {current_user.rut}")
    
    return {
        "success": True,
        "message": "Contraseña actualizada exitosamente"
    }


@router.patch("/actualizar-perfil", response_model=dict)
async def actualizar_perfil(
    nombres: str | None = None,
    apellidos: str | None = None,
    email: EmailStr | None = None,
    foto_url: str | None = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar información del perfil del usuario
    """
    actualizado = False
    
    # Actualizar nombres
    if nombres and nombres != current_user.nombres:
        current_user.nombres = nombres
        actualizado = True
    
    # Actualizar apellidos
    if apellidos and apellidos != current_user.apellidos:
        current_user.apellidos = apellidos
        actualizado = True
    
    # Actualizar email (verificar que no exista)
    if email and email != current_user.email:
        email_existe = db.query(Usuario).filter(
            Usuario.email == email,
            Usuario.id != current_user.id
        ).first()
        
        if email_existe:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está en uso"
            )
        
        current_user.email = email
        actualizado = True
    
    # Actualizar foto
    if foto_url is not None:
        current_user.foto_url = foto_url
        actualizado = True
    
    if actualizado:
        db.commit()
        db.refresh(current_user)
        logger.info(f"Perfil actualizado para usuario {current_user.rut}")
    
    return {
        "success": True,
        "message": "Perfil actualizado exitosamente" if actualizado else "No hay cambios",
        "data": {
            "id": current_user.id,
            "rut": current_user.rut,
            "nombres": current_user.nombres,
            "apellidos": current_user.apellidos,
            "email": current_user.email,
            "foto_url": current_user.foto_url
        }
    }


@router.delete("/eliminar-cuenta", response_model=dict)
async def eliminar_cuenta(
    password: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Eliminar cuenta del usuario actual
    Requiere confirmación con contraseña
    Solo si no tiene préstamos activos
    """
    from models.prestamo import Prestamo
    
    # Verificar contraseña
    if not current_user.verify_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta"
        )
    
    # Verificar préstamos activos
    prestamos_activos = db.query(Prestamo).filter(
        Prestamo.usuario_id == current_user.id,
        Prestamo.estado == "prestado"
    ).count()
    
    if prestamos_activos > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No puedes eliminar tu cuenta con {prestamos_activos} préstamo(s) activo(s)"
        )
    
    # Desactivar cuenta en lugar de eliminar (soft delete)
    current_user.activo = False
    db.commit()
    
    logger.warning(f"Cuenta desactivada para usuario {current_user.rut}")
    
    return {
        "success": True,
        "message": "Cuenta desactivada exitosamente"
    }