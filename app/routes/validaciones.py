from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import logging

from database import get_db
from models.usuario import Usuario
from models.prestamo import Prestamo
from utils.auth import get_current_user, require_role
from utils.validators import validar_rut, formatear_rut

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/validaciones", tags=["Validaciones"])

#Schemes

class EstadoUsuarioResponse(BaseModel):
    puede_prestar: bool
    razones: List[str]
    prestamos_activos: int
    prestamos_vencidos: int
    sancionado: bool
    fecha_sancion_hasta: Optional[datetime]

class AplicarSancionRequest(BaseModel):
    usuario_id: int
    dias_sancion: int
    motivo: Optional[str] = "Atraso en devolución"

class SancionCalculadaResponse(BaseModel):
    dias_atraso: int
    dias_sancion: int
    formula: str


def calcular_sancion(dias_atraso: int) -> int:
    if dias_atraso <= 0:
        return 0
    
    dias_sancion = dias_atraso * 2
    
    # Aplicar mínimo y máximo
    if dias_sancion < 3:
        dias_sancion = 3
    elif dias_sancion > 30:
        dias_sancion = 30
    
    logger.info(f"Sanción calculada: {dias_atraso} días de atraso = {dias_sancion} días de sanción")
    
    return dias_sancion


def verificar_prestamos_vencidos(usuario_id: int, db: Session) -> tuple[bool, int]:
    prestamos_vencidos = db.query(Prestamo).filter(
        Prestamo.usuario_id == usuario_id,
        Prestamo.estado == "prestado",
        Prestamo.fecha_devolucion_estimada < datetime.utcnow()
    ).count()
    
    return prestamos_vencidos > 0, prestamos_vencidos


def contar_prestamos_activos(usuario_id: int, db: Session) -> int:
    return db.query(Prestamo).filter(
        Prestamo.usuario_id == usuario_id,
        Prestamo.estado == "prestado"
    ).count()

@router.get("/puede-prestar/{rut}", response_model=dict)
async def puede_prestar(
    rut: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Validar y formatear RUT
    if not validar_rut(rut):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="RUT inválido"
        )
    
    rut_formateado = formatear_rut(rut)
    
    # Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.rut == rut_formateado).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    puede = True
    razones = []
    
    # 1. Verificar si está sancionado
    if usuario.esta_sancionado():
        puede = False
        razones.append(f"Usuario sancionado hasta {usuario.fecha_sancion_hasta}")
        logger.warning(f"Préstamo rechazado para {rut}: usuario sancionado")
    
    # 2. Verificar préstamos vencidos
    tiene_vencidos, cantidad_vencidos = verificar_prestamos_vencidos(usuario.id, db)
    if tiene_vencidos:
        puede = False
        razones.append(f"Tiene {cantidad_vencidos} préstamo(s) vencido(s)")
        logger.warning(f"Préstamo rechazado para {rut}: {cantidad_vencidos} préstamos vencidos")
    
    # 3. Verificar límite de préstamos activos (máx 3)
    prestamos_activos = contar_prestamos_activos(usuario.id, db)
    if prestamos_activos >= 3:
        puede = False
        razones.append(f"Límite de préstamos alcanzado ({prestamos_activos}/3)")
        logger.warning(f"Préstamo rechazado para {rut}: límite alcanzado ({prestamos_activos}/3)")
    
    if puede:
        logger.info(f"Usuario {rut} puede solicitar préstamo")
    
    return {
        "success": True,
        "data": {
            "puede": puede,
            "razones": razones,
            "prestamos_activos": prestamos_activos,
            "usuario": {
                "rut": usuario.rut,
                "nombres": usuario.nombres,
                "apellidos": usuario.apellidos
            }
        }
    }


@router.get("/calcular-sancion/{dias_atraso}", response_model=SancionCalculadaResponse)
async def calcular_sancion_endpoint(
    dias_atraso: int,
    current_user: Usuario = Depends(require_role(["bibliotecario", "admin"]))
):

    if dias_atraso < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los días de atraso no pueden ser negativos"
        )
    
    dias_sancion = calcular_sancion(dias_atraso)
    
    return SancionCalculadaResponse(
        dias_atraso=dias_atraso,
        dias_sancion=dias_sancion,
        formula=f"{dias_atraso} días × 2 = {dias_sancion} días (mín: 3, máx: 30)"
    )


@router.post("/aplicar-sancion", response_model=dict)
async def aplicar_sancion(
    sancion_data: AplicarSancionRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["bibliotecario", "admin"]))
):

    # Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.id == sancion_data.usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Validar días de sanción
    if sancion_data.dias_sancion < 1 or sancion_data.dias_sancion > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los días de sanción deben estar entre 1 y 30"
        )
    
    # Calcular fecha de fin de sanción
    fecha_sancion = datetime.utcnow() + timedelta(days=sancion_data.dias_sancion)
    
    # Si ya está sancionado, extender la sanción
    if usuario.fecha_sancion_hasta and usuario.fecha_sancion_hasta > datetime.utcnow():
        fecha_sancion = usuario.fecha_sancion_hasta + timedelta(days=sancion_data.dias_sancion)
    
    usuario.fecha_sancion_hasta = fecha_sancion
    db.commit()
    
    # Log de acción
    logger.warning(
        f"SANCIÓN APLICADA | Usuario: {usuario.rut} | "
        f"Días: {sancion_data.dias_sancion} | "
        f"Hasta: {fecha_sancion} | "
        f"Motivo: {sancion_data.motivo} | "
        f"Aplicada por: {current_user.rut}"
    )
    
    return {
        "success": True,
        "message": f"Sanción de {sancion_data.dias_sancion} días aplicada exitosamente",
        "data": {
            "usuario_id": usuario.id,
            "rut": usuario.rut,
            "nombres": f"{usuario.nombres} {usuario.apellidos}",
            "dias_sancion": sancion_data.dias_sancion,
            "fecha_sancion_hasta": fecha_sancion,
            "motivo": sancion_data.motivo,
            "aplicada_por": f"{current_user.nombres} {current_user.apellidos}"
        }
    }

@router.get("/estado-usuario/{rut}", response_model=dict)
async def estado_usuario(
    rut: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["bibliotecario", "admin"]))
):
    # Validar RUT
    if not validar_rut(rut):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="RUT inválido"
        )
    
    rut_formateado = formatear_rut(rut)
    
    # Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.rut == rut_formateado).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Obtener información de préstamos
    prestamos_activos = contar_prestamos_activos(usuario.id, db)
    tiene_vencidos, prestamos_vencidos = verificar_prestamos_vencidos(usuario.id, db)
    sancionado = usuario.esta_sancionado()
    
    # Determinar estado de cuenta
    if sancionado:
        estado_cuenta = "SANCIONADO"
    elif tiene_vencidos:
        estado_cuenta = "CON_ATRASOS"
    elif prestamos_activos >= 3:
        estado_cuenta = "LIMITE_ALCANZADO"
    elif not usuario.activo:
        estado_cuenta = "INACTIVO"
    else:
        estado_cuenta = "DISPONIBLE"
    
    return {
        "success": True,
        "data": {
            "usuario": {
                "id": usuario.id,
                "rut": usuario.rut,
                "nombres": usuario.nombres,
                "apellidos": usuario.apellidos,
                "email": usuario.email,
                "activo": usuario.activo
            },
            "estado_cuenta": estado_cuenta,
            "prestamos": {
                "activos": prestamos_activos,
                "vencidos": prestamos_vencidos,
                "limite_maximo": 3,
                "puede_prestar": prestamos_activos < 3 and not tiene_vencidos and not sancionado
            },
            "sancion": {
                "sancionado": sancionado,
                "fecha_fin": usuario.fecha_sancion_hasta if sancionado else None,
                "dias_restantes": (
                    (usuario.fecha_sancion_hasta - datetime.utcnow()).days 
                    if sancionado else 0
                )
            }
        }
    }

@router.get("/estadisticas-sistema", response_model=dict)
async def estadisticas_sistema(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["admin"]))
):
    total_usuarios = db.query(Usuario).count()
    usuarios_activos = db.query(Usuario).filter(Usuario.activo == True).count()
    usuarios_sancionados = db.query(Usuario).filter(
        Usuario.fecha_sancion_hasta > datetime.utcnow()
    ).count()
    
    prestamos_activos_total = db.query(Prestamo).filter(
        Prestamo.estado == "prestado"
    ).count()
    
    prestamos_vencidos_total = db.query(Prestamo).filter(
        Prestamo.estado == "prestado",
        Prestamo.fecha_devolucion_estimada < datetime.utcnow()
    ).count()
    
    return {
        "success": True,
        "data": {
            "usuarios": {
                "total": total_usuarios,
                "activos": usuarios_activos,
                "sancionados": usuarios_sancionados
            },
            "prestamos": {
                "activos": prestamos_activos_total,
                "vencidos": prestamos_vencidos_total
            }
        }
    }
