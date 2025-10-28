from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from schemas.documento_schema import (
    ListaDocumentos, CategoriaConteo
)
from models import catalogo_model # Importamos desde 'models'

# Routers separados para mantener la lógica limpia
router = APIRouter() # Para /catalogo
router_categorias = APIRouter() # Para /categorias


"Endpoint para realizar la busqueda básica de un documento"
""
@router.get("/buscar/", response_model=ListaDocumentos)
async def api_buscar_documentos_basico(
    q:str = Query (..., min_length=1, description = "Termino de busqueda para titulo o autor"),
    page: int = Query (1, ge=1),
    size: int = Query (10, ge=1, le=100) 
):
    """Búsqueda básica por título o autor."""
    try:
        documentos_list, total = catalogo_model.busqueda_basica(busqueda=q, page=page, size=size)
        return ListaDocumentos(
            total_items=total,
            items = documentos_list
        )
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Error interno en la busqueda básica: {str(e)}")


"Endpoint para listar categorias."
@router_categorias.get("/", response_model=List[CategoriaConteo])
async def api_listar_categorias(
    # CORRECCIÓN: Este endpoint estaba mal en tu main.py
    # El path era incorrecto y llamaba a la función equivocada.
):
    """Lista todas las categorías únicas con su conteo."""
    try:
        categorias = catalogo_model.lista_categorias()
        return categorias
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Error interno al listar las categorias: {str(e)}")


"Endpoint para listar documentos por categoria"
@router_categorias.get("/{categoria_nombre}/documentos/", response_model=ListaDocumentos)
async def api_listar_documentos_por_categoria(
    categoria_nombre: str,
    page: int = Query(1, ge=1),
    size: int = Query (10, ge=1, le=100)
):
    """Lista los documentos de una categoría específica (paginado)."""
    try:
        documentos_list, total = catalogo_model.documento_por_categoria(
            categoria=categoria_nombre, 
            page=page, 
            size=size
        )
        if total == 0 and not documentos_list:
            print(f"No se encontraron documentos para la categoria {categoria_nombre}")
        
        return ListaDocumentos(total_items=total, items=documentos_list)
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Error al listar documentos por categoria: {str(e)}")
