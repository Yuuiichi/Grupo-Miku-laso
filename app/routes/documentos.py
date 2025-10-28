from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from schemas.documento_schema import (
    DocumentoCrear, DocumentoOutput, DocumentoActualizar, ListaDocumentos
)

from utils.auth import require_role
# Importamos las funciones de los 'models' (que ahora son 'services')
from models import documento_model, catalogo_model 
from utils.dependencies import validacion_categoria

router = APIRouter()

"Endpoint para crear documento en la base de datos"

@router.post("/", response_model=DocumentoOutput)
async def api_creacion_documentos(
    documento_data: DocumentoCrear, 
    es_admin: bool = Depends(require_role(["admin"]))
):
    """Crea un nuevo documento."""
    print(f"los datos recibidos fueron los siguientes:{documento_data.model_dump()}")
    
    # La validación ahora lanza una excepción si falla
    validacion_categoria(documento_data.categoria) 
    
    try:
        datos_dict = documento_data.model_dump()
        nuevo_id = documento_model.ingresar_documento(datos_dict)

        documento_guardado = DocumentoOutput(id=nuevo_id, **datos_dict)
        return documento_guardado
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Error interno al crear el documento: {str(e)}")


"Endpoint para realizar un listado de documentos."
@router.get("/", response_model=ListaDocumentos)
async def api_listar_documentos(
    page: int = Query(1, ge=1), 
    size: int = Query(10, ge=1, le=100)
):
    """Lista todos los documentos (paginado)."""
    try:
        documentos_list, total = catalogo_model.listar_documentos(page=page, size=size)
        return ListaDocumentos(
            total_items=total,
            items=documentos_list
        )
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Error interno al listar documentos: {str(e)}")



#Endpoint para buscar un documento, recibiendo su ID


@router.get("/{documento_id}", response_model=DocumentoOutput)
async def api_get_documento(documento_id: int):
    """Obtiene un documento por su ID."""
    try:
        documento = documento_model.busqueda_por_id(documento_id)
        if documento is None:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        # CORRECCIÓN: Faltaba retornar el documento
        return documento
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Error interno al buscar documento: {str(e)}")



"Endpoint para actualizar el documento de la base de datos."
@router.patch("/{documento_id}", response_model=DocumentoOutput)
async def api_actualizar_documento(
    documento_id: int, 
    documento_data: DocumentoActualizar, 
    es_admin: bool = Depends(require_role(["admin"]))
):
    """Actualiza parcialmente un documento por su ID."""
    datos_a_actualizar = documento_data.model_dump(exclude_unset=True)

    if not datos_a_actualizar:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")
    
    if "categoria" in datos_a_actualizar:
        # La validación ahora lanza la excepción
        validacion_categoria(datos_a_actualizar["categoria"])
        
    try:
        documento_actualizado = documento_model.actualizar_documento(documento_id, datos_a_actualizar)

        if documento_actualizado is None:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        # CORRECCIÓN: Faltaba retornar el documento actualizado
        return documento_actualizado
    
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        # CORRECCIÓN: Typo "statuts_code"
        raise HTTPException(status_code=500, detail=f"Error interno al actualizar el archivo: {str(e)}")
