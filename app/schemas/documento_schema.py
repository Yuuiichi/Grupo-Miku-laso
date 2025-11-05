from pydantic import BaseModel
from typing import Optional, List

# ----------ESQUEMAS----------#
# (Movidos desde main.py)

#Esquema de entrada (documento).
class DocumentoCrear(BaseModel):
    tipo: str
    titulo: str
    autor: str
    editorial:Optional[str] = None
    anio:Optional[int] = None
    edicion:Optional[str] = None
    categoria: Optional[str] = None
    tipo_medio: str

#Esquema de salida (documento).
class DocumentoOutput(DocumentoCrear):
    id:int

#Esquema de salida (listar documentos)
class ListaDocumentos(BaseModel):
    total_items: int
    items: List[DocumentoOutput]

#Esquema de salida (listar categorias)
class CategoriaConteo(BaseModel):
    categoria:str
    conteo:int

#Esquema de salida (actualizar documento)
class DocumentoActualizar(BaseModel):
    tipo: Optional[str] = None
    titulo: Optional[str] = None
    autor: Optional[str] = None
    editorial: Optional[str] = None
    anio: Optional[int] = None
    edicion: Optional[str] = None
    categoria: Optional[str] = None
    tipo_medio: Optional[str] = None
