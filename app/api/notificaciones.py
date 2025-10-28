from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date
from app.database import get_db
from app.models.usuario import Usuario
from app.models.log_notificaciones import LogNotificacion
from app.schemas.notificacion_schema import (
    EmailRequest,
    NotificacionLog,
    RecordatorioRequest,
    NotificacionResponse
)
from app.utils.auth import get_current_user, require_role
from app.services.email_service import email_service

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

# ============================================
# DÍA 4: NOTIFICACIONES Y RECORDATORIOS
# ============================================

@router.post("/recordatorios-vencidos", response_model=NotificacionResponse)
async def enviar_recordatorios_masivos(
    request: RecordatorioRequest = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["admin", "bibliotecario"]))
):
    """
    Enviar recordatorios masivos a usuarios con préstamos vencidos.
    
    TODO: Este endpoint debe integrarse con ROL 4 para obtener:
    - Lista de usuarios con préstamos vencidos
    - Detalles de cada préstamo vencido
    - Días de atraso
    
    Por ahora está preparado pero necesita la función de ROL 4.
    """
    
    # Registrar en log
    log = LogNotificacion.crear_log(
        usuario_id=usuario.id,
        tipo="confirmacion_prestamo",
        asunto="Confirmación de préstamo",
        destinatario=usuario.email,
        exitoso=email_exitoso
    )
    db.add(log)
    db.commit()
    
    return {
        "success": email_exitoso,
        "message": "Email de confirmación enviado" if email_exitoso else "Error al enviar email",
        "data": {
            "prestamo_id": prestamo_id,
            "usuario_email": usuario.email,
            "enviado": email_exitoso
        }
    }

@router.post("/email-custom", response_model=dict)
async def enviar_email_personalizado(
    email_data: EmailRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["admin"]))
):
    """
    Enviar email personalizado a un usuario (solo admin).
    Útil para comunicaciones especiales.
    """
    # Buscar usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == email_data.destinatario).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario con ese email no encontrado"
        )
    
    # Enviar email
    if email_data.html:
        contenido = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f4f4f4; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Biblioteca Estación Central</h1>
                </div>
                <div class="content">
                    {email_data.mensaje}
                </div>
                <div class="footer">
                    <p>&copy; 2025 Biblioteca Estación Central</p>
                </div>
            </div>
        </body>
        </html>
        """
    else:
        contenido = email_data.mensaje
    
    email_exitoso = email_service.send_email(
        to=email_data.destinatario,
        subject=email_data.asunto,
        html_content=contenido
    )
    
    # Registrar en log
    log = LogNotificacion.crear_log(
        usuario_id=usuario.id,
        tipo="email_personalizado",
        asunto=email_data.asunto,
        destinatario=email_data.destinatario,
        exitoso=email_exitoso
    )
    db.add(log)
    db.commit()
    
    return {
        "success": email_exitoso,
        "message": "Email enviado exitosamente" if email_exitoso else "Error al enviar email"
    }

@router.get("/historial", response_model=List[NotificacionLog])
async def ver_historial_notificaciones(
    usuario_id: Optional[int] = Query(None, description="Filtrar por usuario"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de notificación"),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["admin", "bibliotecario"]))
):
    """
    Ver historial de notificaciones enviadas.
    Útil para auditoría y verificar envíos.
    """
    query = db.query(LogNotificacion)
    
    if usuario_id:
        query = query.filter(LogNotificacion.usuario_id == usuario_id)
    
    if tipo:
        query = query.filter(LogNotificacion.tipo == tipo)
    
    if fecha_desde:
        query = query.filter(LogNotificacion.fecha_envio >= fecha_desde)
    
    if fecha_hasta:
        fecha_hasta_end = datetime.combine(fecha_hasta, datetime.max.time())
        query = query.filter(LogNotificacion.fecha_envio <= fecha_hasta_end)
    
    logs = query.order_by(LogNotificacion.fecha_envio.desc()).offset(skip).limit(limit).all()
    
    return logs

@router.get("/historial/usuario/{usuario_id}", response_model=List[NotificacionLog])
async def ver_historial_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Ver historial de notificaciones de un usuario específico.
    El usuario puede ver su propio historial, admin puede ver cualquiera.
    """
    # Verificar permisos
    if current_user.id != usuario_id and current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este historial"
        )
    
    logs = db.query(LogNotificacion).filter(
        LogNotificacion.usuario_id == usuario_id
    ).order_by(LogNotificacion.fecha_envio.desc()).limit(50).all()
    
    return logs

@router.get("/estadisticas", response_model=dict)
async def obtener_estadisticas_notificaciones(
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["admin"]))
):
    """
    Estadísticas de notificaciones enviadas.
    """
    query = db.query(LogNotificacion)
    
    if fecha_desde:
        query = query.filter(LogNotificacion.fecha_envio >= fecha_desde)
    
    if fecha_hasta:
        fecha_hasta_end = datetime.combine(fecha_hasta, datetime.max.time())
        query = query.filter(LogNotificacion.fecha_envio <= fecha_hasta_end)
    
    total = query.count()
    exitosos = query.filter(LogNotificacion.enviado_exitosamente == True).count()
    fallidos = query.filter(LogNotificacion.enviado_exitosamente == False).count()
    
    # Estadísticas por tipo
    from sqlalchemy import func
    por_tipo = db.query(
        LogNotificacion.tipo,
        func.count(LogNotificacion.id).label("total")
    ).group_by(LogNotificacion.tipo).all()
    
    return {
        "total_notificaciones": total,
        "exitosos": exitosos,
        "fallidos": fallidos,
        "tasa_exito": round((exitosos / total * 100) if total > 0 else 0, 2),
        "por_tipo": [
            {"tipo": tipo, "total": total}
            for tipo, total in por_tipo
        ],
        "periodo": {
            "desde": fecha_desde,
            "hasta": fecha_hasta
        }
    }

@router.delete("/limpiar-logs", response_model=dict)
async def limpiar_logs_antiguos(
    dias: int = Query(90, ge=30, description="Eliminar logs más antiguos que X días"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["admin"]))
):
    """
    Limpiar logs de notificaciones antiguas.
    Por defecto elimina logs mayores a 90 días.
    Mínimo 30 días para no borrar logs recientes.
    """
    from datetime import timedelta
    
    fecha_limite = datetime.utcnow() - timedelta(days=dias)
    
    logs_eliminados = db.query(LogNotificacion).filter(
        LogNotificacion.fecha_envio < fecha_limite
    ).delete()
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Se eliminaron {logs_eliminados} logs de notificaciones",
        "logs_eliminados": logs_eliminados,
        "fecha_limite": fecha_limite
    }

# ============================================
# FUNCIONES AUXILIARES para integración
# ============================================

def notificar_nuevo_usuario(usuario_id: int, db: Session) -> bool:
    """
    Función auxiliar para enviar email de bienvenida.
    Llamar después de activar la cuenta.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        return False
    
    # Aquí podrías crear un template específico de bienvenida
    # Por ahora usamos el genérico
    
    return True

def notificar_cambio_password(usuario_id: int, db: Session) -> bool:
    """
    Función auxiliar para notificar cambio de contraseña.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        return False
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>Cambio de contraseña</h2>
        <p>Hola {usuario.nombres},</p>
        <p>Tu contraseña ha sido cambiada exitosamente.</p>
        <p>Si no realizaste este cambio, contacta inmediatamente con el administrador.</p>
        <p>Saludos,<br>Biblioteca Estación Central</p>
    </body>
    </html>
    """
    
    email_exitoso = email_service.send_email(
        to=usuario.email,
        subject="Cambio de contraseña - Biblioteca EC",
        html_content=html
    )
    
    # Log
    log = LogNotificacion.crear_log(
        usuario_id=usuario.id,
        tipo="cambio_password",
        asunto="Cambio de contraseña",
        destinatario=usuario.email,
        exitoso=email_exitoso
    )
    db.add(log)
    db.commit()
    
    return email_exitoso
 TODO: Obtener préstamos vencidos desde ROL 4
    # from app.api.prestamos import obtener_prestamos_vencidos_agrupados
    # prestamos_vencidos = obtener_prestamos_vencidos_agrupados(db)
    
    # SIMULACIÓN temporal (comentar cuando ROL 4 esté listo)
    prestamos_vencidos = {}
    
    if not prestamos_vencidos:
        return NotificacionResponse(
            success=True,
            total_enviados=0,
            total_fallidos=0,
            detalles=[],
            mensaje="No hay usuarios con préstamos vencidos"
        )
    
    enviados = 0
    fallidos = 0
    detalles = []
    
    # Enviar un email por usuario con todos sus préstamos vencidos
    for usuario_id, prestamos in prestamos_vencidos.items():
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        
        if not usuario:
            continue
        
        # Preparar lista de préstamos para el email
        prestamos_email = [
            {
                "documento": p["documento_titulo"],
                "fecha_devolucion": p["fecha_devolucion"].strftime("%d/%m/%Y"),
                "dias_atraso": p["dias_atraso"]
            }
            for p in prestamos
        ]
        
        # Enviar email
        email_exitoso = email_service.send_recordatorio_vencido(
            to=usuario.email,
            nombre=f"{usuario.nombres} {usuario.apellidos}",
            prestamos_vencidos=prestamos_email
        )
        
        # Registrar en log
        log = LogNotificacion.crear_log(
            usuario_id=usuario.id,
            tipo="recordatorio_vencido",
            asunto="Recordatorio de préstamos vencidos",
            destinatario=usuario.email,
            exitoso=email_exitoso,
            error=None if email_exitoso else "Error al enviar email"
        )
        db.add(log)
        
        if email_exitoso:
            enviados += 1
            # TODO: Marcar préstamos como notificados en ROL 4
        else:
            fallidos += 1
        
        detalles.append({
            "usuario_id": usuario.id,
            "usuario_email": usuario.email,
            "total_prestamos_vencidos": len(prestamos),
            "enviado": email_exitoso
        })
    
    db.commit()
    
    return NotificacionResponse(
        success=True,
        total_enviados=enviados,
        total_fallidos=fallidos,
        detalles=detalles,
        mensaje=f"Se enviaron {enviados} recordatorios, {fallidos} fallaron"
    )

@router.post("/confirmacion-prestamo/{prestamo_id}", response_model=dict)
async def enviar_confirmacion_prestamo(
    prestamo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["admin", "bibliotecario"]))
):
    """
    Enviar email de confirmación de préstamo.
    
    TODO: Integrar con ROL 4 para obtener datos del préstamo.
    Debe ser llamado automáticamente al crear un préstamo.
    """
    
    # TODO: Obtener datos del préstamo desde ROL 4
    # from app.api.prestamos import obtener_prestamo_completo
    # prestamo_info = obtener_prestamo_completo(prestamo_id, db)
    
    # SIMULACIÓN temporal
    prestamo_info = {
        "id": prestamo_id,
        "tipo": "domicilio",
        "fecha_prestamo": "27/10/2025",
        "documentos": []
    }
    
    usuario_id = 1  # TODO: obtener del préstamo real
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Enviar email
    email_exitoso = email_service.send_confirmacion_prestamo(
        to=usuario.email,
        nombre=f"{usuario.nombres} {usuario.apellidos}",
        prestamo_info=prestamo_info
    )
    
    #