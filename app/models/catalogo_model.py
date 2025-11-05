from app.database import connection
from fastapi import HTTPException
from typing import Optional, Dict, List, Tuple

# --- LÓGICA DE BD PARA 'Catalogo' y 'Categorias' (Búsquedas y Listados) ---
# (Funciones movidas desde main.py)

def listar_documentos(page: int, size: int) -> Tuple[List[dict], int]:
    conn = None
    offset = (page - 1) * size

    query_data= '''
        SELECT id, tipo, titulo, autor, editorial, anio, edicion, categoria, tipo_medio
        FROM documento
        ORDER BY id
        LIMIT %s OFFSET %s;
    '''
    query_count = "SELECT COUNT(*) FROM documento;"

    try:
        conn = connection()
        cur = conn.cursor()

        cur.execute(query_count)
        total_items = cur.fetchone()[0]

        cur.execute(query_data, (size, offset))
        rows = cur.fetchall() 

        columnas_f= [desc[0] for desc in cur.description]
        documentos = [dict(zip(columnas_f, row)) for row in rows] 

        return documentos, total_items
    except Exception as e:
        print(f"Error en DB (listar_documentos): {e}")
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail="Error interno al listar documentos")
    finally:
        if conn:
            cur.close()
            conn.close()
            print("Conexión a la BD cerrada")

def busqueda_basica(busqueda: str, page:int, size:int) -> Tuple[List[dict], int]:
    conn = None
    offset = (page-1) * size
    
    termino_ilike = f"%{busqueda}%" 

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

        cur.execute(query_count, (termino_ilike, termino_ilike))
        
        total_items = cur.fetchone()[0] 

        
        cur.execute(query_data, (termino_ilike, termino_ilike, size, offset))
        rows = cur.fetchall()

        columnas = [desc[0] for desc in cur.description]
        documentos = [dict(zip(columnas, row)) for row in rows]
        
        return documentos, total_items
    except Exception as e:
        print(f"Error en DB (busqueda_basica): {e}")
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail="Error interno en búsqueda básica")
    finally:
        if conn:
            cur.close()
            conn.close()
            print("Conexión a la BD cerrada")

def lista_categorias() -> List[dict]:
    conn = None
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

        categorias = [{"categoria": row[0], "conteo": row[1]} for row in rows]
        
        return categorias
    except Exception as e:
        print(f"Error en DB (lista_categorias): {e}")
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail="Error interno al listar categorías")
    finally:
        if conn:
            cur.close()
            conn.close()
            print("Conexión a la BD cerrada.")

def documento_por_categoria(categoria: str, page: int, size: int) -> Tuple[List[dict], int]:
    conn = None
    offset = (page-1)*size
    query_data="""
        SELECT id, tipo, titulo, autor, editorial, anio, edicion, categoria, tipo_medio
        FROM documento
        WHERE categoria = %s
        ORDER BY id
        LIMIT %s OFFSET %s;
    """
    query_count = """
        SELECT COUNT(*) FROM documento
        WHERE categoria = %s;
    """
    try:
        conn = connection()
        cur = conn.cursor()
        
        cur.execute(query_count, (categoria,))
        total_items = cur.fetchone()[0]

        cur.execute(query_data,(categoria, size, offset))
        rows = cur.fetchall()

        columnas =[desc[0] for desc in cur.description]
        documentos = [dict(zip(columnas,row)) for row in rows]

        return documentos, total_items
    except Exception as e:
        print(f"Error en DB (documento_por_categoria): {e}")
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail="Error interno al listar por categoría")
    finally:
        if conn:
            cur.close()
            conn.close()
            print("Conexión BD cerrada.")
