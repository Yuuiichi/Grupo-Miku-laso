from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.prestamos import Prestamo, DetallePrestamo
from app.models.ejemplar import Ejemplar
from app.utils.dates import calcular_fecha_devolucion
from app.schemas.prestamo import PrestamoCreate, PrestamoResponse
from app.database import get_db

router = APIRouter(prefix="/prestamos", tags=["Prestamos"])

@router.post("/registrar", response_model=PrestamoResponse)
def registrar_prestamo(data: PrestamoCreate, db: Session = Depends(get_db)):

    '''
    Registra un nuevo préstamo con sus detalles en el sistema.
    '''

    puede_prestar = True
    if not puede_prestar:
        raise HTTPException(status_code=400, detail="El usuario no puede realizar más préstamos.")
    
    ejemplares = db.query(Ejemplar).filter(Ejemplar.id.in_(data.ejemplar_ids)).all()
    if len(ejemplares) != len(data.ejemplar_ids):
        raise HTTPException(status_code=404, detail="Uno o más ejemplares no existen.")
    for ejemplar in ejemplares:
        if ejemplar.estado != 'disponible':
            raise HTTPException(status_code=400, detail=f"El ejemplar {ejemplar.id} no está disponible para préstamo.")
        
    prestamo = Prestamo(
        tipo_prestamo=data.tipo_prestamo,
        usuario_id=data.usuario_id,
        bibliotecario_id=data.bibliotecario_id,
        fecha_prestamo=datetime.now(),
        hora_prestamo=datetime.now().time(),
        estado="activo"
    )
    db.add(prestamo)
    db.commit()
    db.refresh(prestamo)

    for ejemplar in ejemplares:
        detalle = DetallePrestamo(
            prestamo_id = prestamo.id,
            ejemplar_id = ejemplar.id
        )
        db.add(detalle)
        ejemplar.estado = 'prestado'

        fecha_estimada = calcular_fecha_devolucion(data.tipo_prestamo, ejemplar.tipo_documento)
        prestamo.fecha_devolucion_estimada = fecha_estimada
        prestamo.hora_devolucion_estimada = fecha_estimada.time()
    
    db.commit()
    db.refresh(prestamo)

    return prestamo

@router.get("/activos", response_model=PrestamoResponse)
def listar_prestamos_activos(
    usuario_id: Optional[int] = Query(None, description="ID del usuario para filtrar préstamos (opcional)"),
    page: int = Query(1, ge=1, description="Pagina de resultados (opcional)"),
    size: int = Query(20, ge=1, le=200, description="Número de resultados por página (opcional)"),
    db: Session = Depends(get_db)
):
    
    '''
    Lista los préstamos activos, con opción de filtrar por usuario y paginación.
    '''

    query = db.query(Prestamo).filter(Prestamo.estado == 'activo')

    if usuario_id is not None:
        query = query.filter(Prestamo.usuario_id == usuario_id)
    
    offset = (page - 1) * size
    
    prestamos = query.order_by(Prestamo.fecha_prestamo.desc()).offset(offset).limit(size).all()

    return prestamos