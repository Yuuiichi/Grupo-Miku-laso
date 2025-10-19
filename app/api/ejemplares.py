from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.ejemplar import Ejemplar
from app.schemas.ejemplar_schema import (
    EjemplarCreate, 
    EjemplarResponse, 
    EjemplarEstadoUpdate,
    DisponibilidadResponse
)

router = APIRouter(prefix="/ejemplares", tags=["Ejemplares"])

ESTADOS_VALIDOS = ["disponible", "prestado", "en_sala", "devuelto", "mantenimiento", "perdido"]

# ============================================
# ENDPOINT 1: Crear ejemplar
# ============================================
@router.post("/", response_model=EjemplarResponse, status_code=status.HTTP_201_CREATED)
def crear_ejemplar(ejemplar: EjemplarCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo ejemplar de un documento.
    Solo bibliotecarios/admin pueden crear ejemplares.
    """
    # Verificar que el código no exista
    existe = db.query(Ejemplar).filter(Ejemplar.codigo == ejemplar.codigo).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un ejemplar con el código {ejemplar.codigo}"
        )
    
    # TODO: Verificar que documento_id exista (cuando ROL 2 esté listo)
    
    nuevo_ejemplar = Ejemplar(
        documento_id=ejemplar.documento_id,
        codigo=ejemplar.codigo,
        ubicacion=ejemplar.ubicacion,
        estado="disponible"
    )
    
    db.add(nuevo_ejemplar)
    db.commit()
    db.refresh(nuevo_ejemplar)
    
    return nuevo_ejemplar


# ============================================
# ENDPOINT 2: Listar ejemplares de un documento
# ============================================
@router.get("/documento/{documento_id}", response_model=List[EjemplarResponse])
def listar_ejemplares_documento(documento_id: int, db: Session = Depends(get_db)):
    """
    Obtener todos los ejemplares de un documento específico.
    Usado por ROL 2 para mostrar disponibilidad en la búsqueda.
    """
    ejemplares = db.query(Ejemplar).filter(
        Ejemplar.documento_id == documento_id
    ).all()
    
    return ejemplares


# ============================================
# ENDPOINT 3: Ver disponibilidad de un documento
# ============================================
@router.get("/documento/{documento_id}/disponibilidad", response_model=DisponibilidadResponse)
def obtener_disponibilidad(documento_id: int, db: Session = Depends(get_db)):
    """
    Obtener conteo de disponibilidad de un documento.
    
    FUNCIÓN CLAVE para ROL 2 (búsqueda) y ROL 4 (préstamos).
    """
    ejemplares = db.query(Ejemplar).filter(
        Ejemplar.documento_id == documento_id
    ).all()
    
    if not ejemplares:
        return DisponibilidadResponse(
            disponibles=0,
            prestados=0,
            en_sala=0,
            mantenimiento=0,
            total=0,
            puede_solicitar=False
        )
    
    # Contar por estado
    disponibles = sum(1 for e in ejemplares if e.estado == "disponible")
    prestados = sum(1 for e in ejemplares if e.estado == "prestado")
    en_sala = sum(1 for e in ejemplares if e.estado == "en_sala")
    mantenimiento = sum(1 for e in ejemplares if e.estado == "mantenimiento")
    
    return DisponibilidadResponse(
        disponibles=disponibles,
        prestados=prestados,
        en_sala=en_sala,
        mantenimiento=mantenimiento,
        total=len(ejemplares),
        puede_solicitar=disponibles > 0
    )


# ============================================
# ENDPOINT 4: Actualizar estado de ejemplar
# ============================================
@router.patch("/{ejemplar_id}/estado", response_model=EjemplarResponse)
def actualizar_estado_ejemplar(
    ejemplar_id: int, 
    estado_update: EjemplarEstadoUpdate, 
    db: Session = Depends(get_db)
):
    """
    Cambiar el estado de un ejemplar.
    Usado por ROL 4 cuando se registra un préstamo o devolución.
    """
    ejemplar = db.query(Ejemplar).filter(Ejemplar.id == ejemplar_id).first()
    
    if not ejemplar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ejemplar con id {ejemplar_id} no encontrado"
        )
    
    # Validar estado
    nuevo_estado = estado_update.estado.lower()
    if nuevo_estado not in ESTADOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Estados válidos: {', '.join(ESTADOS_VALIDOS)}"
        )
    
    ejemplar.estado = nuevo_estado
    db.commit()
    db.refresh(ejemplar)
    
    return ejemplar


# ============================================
# ENDPOINT 5: Buscar ejemplar por código
# ============================================
@router.get("/codigo/{codigo}", response_model=EjemplarResponse)
def buscar_por_codigo(codigo: str, db: Session = Depends(get_db)):
    """
    Buscar un ejemplar específico por su código único.
    Usado al momento de devoluciones (ROL 4).
    """
    ejemplar = db.query(Ejemplar).filter(Ejemplar.codigo == codigo).first()
    
    if not ejemplar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe ejemplar con código {codigo}"
        )
    
    return ejemplar


# ============================================
# ENDPOINT 6: Listar ejemplares disponibles
# ============================================
@router.get("/disponibles", response_model=List[EjemplarResponse])
def listar_disponibles(documento_id: int = None, db: Session = Depends(get_db)):
    """
    Listar todos los ejemplares disponibles.
    Opcionalmente filtrar por documento_id.
    """
    query = db.query(Ejemplar).filter(Ejemplar.estado == "disponible")
    
    if documento_id:
        query = query.filter(Ejemplar.documento_id == documento_id)
    
    ejemplares = query.all()
    return ejemplares


# ============================================
# FUNCIONES AUXILIARES para otros roles
# ============================================

def marcar_prestado(ejemplar_id: int, db: Session) -> bool:
    """
    Función para ROL 4: Marcar ejemplar como prestado.
    Retorna True si fue exitoso, False si no estaba disponible.
    """
    ejemplar = db.query(Ejemplar).filter(Ejemplar.id == ejemplar_id).first()
    
    if not ejemplar:
        return False
    
    if ejemplar.estado != "disponible":
        return False
    
    ejemplar.estado = "prestado"
    db.commit()
    return True


def marcar_devuelto(ejemplar_id: int, db: Session) -> bool:
    """
    Función para ROL 4: Marcar ejemplar como devuelto.
    Después de 30 min debería cambiar a disponible (simplificado: directo a disponible).
    """
    ejemplar = db.query(Ejemplar).filter(Ejemplar.id == ejemplar_id).first()
    
    if not ejemplar:
        return False
    
    if ejemplar.estado not in ["prestado", "en_sala"]:
        return False
    
    # Simplificado: cambiar directo a disponible
    ejemplar.estado = "disponible"
    db.commit()
    return True


def get_disponibilidad_rapida(documento_id: int, db: Session) -> dict:
    """
    Función rápida para ROL 2: solo retorna si hay disponibles y cuántos.
    """
    disponibles = db.query(Ejemplar).filter(
        Ejemplar.documento_id == documento_id,
        Ejemplar.estado == "disponible"
    ).count()
    
    return {
        "disponibles": disponibles,
        "puede_solicitar": disponibles > 0
    }