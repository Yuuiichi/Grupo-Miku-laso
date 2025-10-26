from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, Query
from typing import Optional, List
import psycopg2
from config import config
app = FastAPI()

CATEGORIAS_VALIDAS={
    "literatura_chilena",
    "tecnico_español",
    "novela",
    "ciencia_ficcion",
    "historia",
    "infantil",
    "accion",
    "guerra",
    "romance"
    #podemos agregar más!
} 
#----------ESQUEMAS----------#
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

#----------FIN ESQUEMAS----------#








#----------FUNCIONES----------#

#Esta función establece la conexión con la base de datos,pero no se encarga de cerrarla (!)
def connection():
    params = config() #Hace lectura del archivo ini
    print("Estableciendo conexión con la DB")
    return psycopg2.connect(**params)

async def verificacion():
    print("Verificando rol")
    '''
    Lógica de verificación.
    '''
    return True 

def ingresar_documento(data: dict):
    conn = None
    query = """
    INSERT INTO documento (tipo, titulo, autor, editorial, anio, edicion, categoria, tipo_medio)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id;
    """
    values = (
        data.get('tipo'),
        data.get('titulo'),
        data.get('autor'),
        data.get('editorial'),
        data.get('anio'),
        data.get('edicion'),
        data.get('categoria'),
        data.get('tipo_medio')
    )
    try:
        conn= connection()
        cur= conn.cursor()
        cur.execute(query, values) #(query a entregar a la base de datos, INSERT...)

        nuevo_id = cur.fetchone()[0] #ID que retorna la query

        conn.commit()
        cur.close()
        print(f"Ingreso a la bd correcto, nuevo ID: {nuevo_id}")
        
        #Respuesta para el frontend:
        
        return nuevo_id
    except Exception:
        print(Exception)
        if conn:
            conn.rollback()
        raise Exception
    finally:
        if conn:
            conn.close()
            print("Conexión a la BD cerrada")

def listar_documentos (page: int, size: int):
    conn = None

    offset = (page - 1) * size  # para que no entregue siempre los mismos size elementos y vaya 'avanzando'

    query_data= '''
        SELECT id, tipo, titulo, autor, editorial, anio, edicion, categoria, tipo_medio
        FROM documento
        ORDER BY id
        LIMIT %s  OFFSET %s;
    '''
    query_count = "SELECT COUNT(*) FROM documento;" #Contar el número total de documentos que existen en la tabla 'documento'.

    try:
        conn = connection()
        cur = conn.cursor()

        cur.execute(query_count)
        total_items = cur.fetchone()[0]

        cur.execute (query_data, (size, offset))
        columnas = cur.fetchall()

        columnas_f= [desc[0] for desc in cur.description]
        documentos = [dict(zip(columnas_f, columna)) for columna in columnas]

        cur.close()

        return documentos, total_items
    except Exception:
        print(f"Error al listar {Exception}")
        if conn:
            conn.rollback()
        raise Exception
    
    finally:
        if conn:
            conn.close()
            print("Conexión a la BD cerrada")

def busqueda_basica (busqueda: str, page:int, size:int):
    conn= None
    offset = (page-1)*size
    termino_ilike = f"%{busqueda}"

    query_data = """
        SELECT id, tipo,titulo,autor,editorial,anio,edicion,categoria,tipo_medio
        FROM documento
        WHERE titulo ILIKE %s OR autor ILIKE %s
        ORDER BY id
        LIMIT %s OFFSET %s;
    """
    query_count = """
        SELECT COUNT(*) FROM documento
        WHERE titulo ILIKE %s OR autor ILIKE %s;
    """

    try:
        conn = connection()
        cur = conn.cursor()

        #Query de conteo
        cur.execute (query_count, (termino_ilike, termino_ilike))
        total_items = cur.futchone()[0]

        #Query de datos 

        cur.execute(query_count, (termino_ilike, termino_ilike))
        rows = cur.fetchall()

        #tupla a dicc
        columnas = [desc[0] for desc in cur.description]
        documentos = [dict(zip(columnas, row)) for row in rows]
        cur.close()
        return documentos, total_items
    except Exception:
        print(f"Error en la busqueda básica, error: {Exception}")
        if conn:
            conn.rollback()
        raise Exception
    finally:
        if conn:
            conn.close()

#NO VOY A HACER LA BUSQUEDA AVANZADA XDDD

def busqueda_por_id (documento_id: int):
    conn = None
    query = """
        SELECT id, tipo, titulo, autor, editoria, anio, edicion, categoria, tipo_medio
        FROM documento
        WHERE id = %s;
    """

    try:
        conn = connection()
        cur = conn.cursor()
        cur.execute(query, (documento_id,))
        row= cur.fetchone()

        if row is None:
            return None
        
        #Tupla a Dicc
        columnas = [desc[0] for desc in cur.description]
        documento = dict(zip(columnas, row))

        cur.close()
        return documento
    
    except Exception:
        print(f"Error en la base de datos busqueda ID, error: {Exception}")
        raise Exception
    finally:
        if conn:
            conn.close()
            print("Conexión a la BD cerrada.")

#DIA 3
def lista_categorias():
        conn= None
        query = """
            SELECT categoria, COUNT(*) as conteo
            FROM documento
            WHERE categoria IS NOT NULL
            GROUP BY categoria
            ORDER BY categoria ASC;
        """

        try:
            conn = connection()
            cur = conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()

            #Convertimos tuplas en dicc
            categorias = [{"categoria": row[0], "conteo": row[1]} for row in rows]

            cur.close()
            return categorias
        
        except Exception:
            print(f"Error en la base de datos (al listar categorias), error: {Exception}")
            if conn:
                conn.rollback()
            raise Exception
        finally:
            if conn:
                conn.close()
                print("Conexión a la BD cerrada.")

def documento_por_categoria(categoria: str, page: int, size: int):
    conn= None
    offset = (page-1)*size
    query_data="""
        SELECT id, tipo, titulo, autor, editorial, anio, edicion, categoria, tipo_medio
        FROM documento
        WHERE categoria = %s
        ORDER by id;
    """
    query_count = """
        SELECT COUNT(*) FROM documento
        WHERE categoria = %s;
    """

    try:
        conn = connection()
        cur = conn.cursor()
        #Query de conteo
        cur.execute(query_count, (categoria,))
        total_items = cur.fetchone()[0]


        #Query de datos
        cur.execute(query_data,(categoria, size, offset))
        rows = cur.fetchall()

        #Tupla a dicc
        columnas =[desc[0] for desc in cur.description]
        documentos = [dict(zip(columnas,row)) for row in rows]

        cur.close()
        return documentos, total_items
    except Exception:
        print(f"Error en la base de datos (documentos por categoria), error: {Exception}")
        if conn: conn.rollback()
        raise Exception
    finally:
        if conn:
            conn.close()
            print("Conexión BD cerrada.")

def validacion_categoria(categoria:Optional[str]):
    """
    conn = None
    #Con esta query, solamente verificamos que exista la categoria (que se haga mención a ella al menos una vez.) 
    query = 
        SELECT 1
        FROM documento
        WHERE categoria = (%s)
        LIMIT 1;
    

    try:
        conn= connection()
        cur = conn.cursor()

        #Ejecución de la query
        cur.execute(query,(categoria,))
    """
    #NO NECESITAMOS INGRESAR A LA BASE DE DATOS PARA COMPROBAR 
    # SI UNA CATEGORIA ES VALIDA, BASTA CON AGREGAR UN SET CON CATEGORIAS
    # 'BASE' PERMITIDAS.
    if categoria is None:
        return True #Esto porque categoria es opcional dentro de nuestro modelo
    elif categoria not in CATEGORIAS_VALIDAS:
        return False
    else:
        return True
    
#DIA 4
#Ojo acá, me huele raro como está compuesta la función
#Actualizar documento
def actualizar_documento (id: int, data: dict):
    conn = None
    #SOLUCIÓN SUPER INTELIGENTE PARA MANEJAR LA ACTUALIZACIÓN PARCIAL DE UN DOCUMENTO
    set_clauses =[]
    params =[]
    query_modify = "" 
    for key, value in data.items():
        set_clauses.append(f"{key} = %s")
        params.append(value)
    
    if not set_clauses:
        return None
    
    set_query = ", ".join(set_clauses)

    params.append(id)

    #Nos aseguramos de que el archivo efectivamente exista.
    if busqueda_por_id (id) is not None:
        query_modify =f"""
        UPDATE documento
        set {set_query}
        WHERE id = %s
        RETURNING id, tipo, titulo, autor, editorial, anio, edicion, categoria, tipo_medio;
    """
    if busqueda_por_id is None:
        return None #Debo arreglar esta parte
    
    try:
        conn = connection()
        cur = conn.cursor()
        cur.execute(query_modify, tuple(params))
        row = cur.fetchone()

        if row is None:
            return None
        
        conn.commit()

        #Convertir fila en dicc
        columnas = [desc[0] for desc in cur.description]
        documento_actualizado = dict(zip(columnas,row))

        cur.close()
        return documento_actualizado
    except Exception:
        print(f"Error en la base de datos al actualizar documento, error: {Exception}")
        if conn:
            conn.rollback()
        raise Exception
    finally:
        if conn:
            conn.close()
            print("Conexión con la BD cerrada.")

#Eliminar documento y Restaurar documento dependo del avance de los demás para llevarlo a cabo.


#DIA 5:


#----------FIN FUNCIONES----------#






#----------ENDPOINTS----------#
#Endpoint asociada a la función : ingresar_documento()
@app.post("/documentos/", response_model = DocumentoOutput)
async def api_creacion_documentos(documento_data: DocumentoCrear, es_admin: bool = Depends(verificacion)):
    print(f"los datos recibidos fueron los siguientes:{documento_data.model_dump()}") #Aqui tengo un diccionario

    try:
        datos_dict = documento_data.model_dump() #Transformo el modelo pydantic en un diccionario py
        nuevo_id = ingresar_documento(datos_dict)

        documento_guardado = DocumentoOutput(
            id = nuevo_id,
            **datos_dict
        )
        return documento_guardado #Para enviarlo al frontednd
    except Exception:
        raise HTTPException(status_code=500, detail=f"Error interno al crear el documento: {Exception}")

#Endpoint asociada a la función: listar_documentos()

@app.get("/documentos/", response_model=ListaDocumentos)
async def api_listar_documentos(page: int = Query(1, ge=1), size: int=Query(10, ge=1, le=100)):
    try:
        documentos_list, total = listar_documentos(page=page, size=size)

        return ListaDocumentos(
            total_items=total,
            items = documentos_list
        )
    except:
        raise HTTPException(status_code=500, detail= f"Error interno al listar documentos, error: {Exception}")

#Endpoint Busqueda básica        
@app.get("/catalogo/buscar", response_model=ListaDocumentos)
async def api_buscar_documentos_basico(
    q:str = Query (..., min_length=1, description = "Termino de busqueda para titulo o autor"),
    page: int = Query (1, ge=1),
    size: int = Query (10, ge=1, le=100) ):
    try:
        documentos_list, total = busqueda_basica (q=q, page=page, size=size)
        return ListaDocumentos(
            total_items=total,
            items = documentos_list
        )
    except Exception:
        raise HTTPException(status_code=500,detail = f"Error interno en la busqueda básica, error: {Exception}")

#Endpoint busqueda por ID
@app.get("/documentos/{documento_id}", response_model=DocumentoOutput)
async def api_get_documento(documento_id: int):
    try:
        documento = busqueda_por_id(documento_id)
        if documento is None:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
    except Exception:
        if isinstance(Exception, HTTPException):
            raise Exception
        raise HTTPException(status_code=500, detail= f"Error interno al buscar documento {Exception}")
    
    



#Endpoint asociada a la función: listar_categorias
@app.get("/categorias/{categoria_nombre}/documentos/", response_model= List[ListaDocumentos])
async def api_listar_categorias():
    try:
        categorias = listar_documentos()
        return categorias
    except Exception:
        raise HTTPException(status_code=500, detail= f"Error interno al listar las categorias, error: {Exception}")



#Endpoint asociada a la función: documento_por_categoria
@app.get("/categorias/{categoria_nombre}/documentos/", response_model=ListaDocumentos)
async def api_listar_documentos_por_categoria(
    categoria_nombre: str,
    page: int = Query(1, ge=1),
    size: int = Query (10, ge=1, le=100)
    ):
    try:
        documentos_list, total = documento_por_categoria(categoria_nombre=categoria_nombre, page=page, size=size)
        if total == 0 and not documentos_list:
            print(f"No se encontraron documentos para la categoria {categoria_nombre}")
        return ListaDocumentos(total_items=total, items= documentos_list)
    except Exception:
        raise HTTPException(status_code=500, detail= f"Error al listar documentos por categoria, error : {Exception}")
    
#Endpoint asociada a la función: actualizar_documento
@app.patch("/documentos/{documento_id}", response_model= DocumentoOutput)
async def api_actualizar_documento( documento_id: int, documento_data: DocumentoActualizar,es_admin:bool = Depends(verificacion)):
    datos_a_actualizar = documento_data.model_dump(exclude_unset=True)

    if not datos_a_actualizar:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")
    
    if "categoria" in datos_a_actualizar:
        if not validacion_categoria(datos_a_actualizar["categoria"]):
            raise HTTPException(status_code=400, detail=f"Categoria {datos_a_actualizar["categoria"]} no es valida" )
        
    try:
        documento_actualizado = actualizar_documento(documento_id, datos_a_actualizar)

        if documento_actualizado is None:
            raise HTTPException(status_code=404, detail= "Documento no encontrado")
    
    except Exception:
        if isinstance(Exception, HTTPException):
            raise Exception
        raise HTTPException(statuts_code=500, detail=f"Error interno al actualizar el archivo {Exception}")

#----------FIN ENDPOINTS----------#

