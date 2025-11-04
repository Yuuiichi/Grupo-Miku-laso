from app.database import connection
from fastapi import HTTPException
from typing import Optional, Dict

# --- LÓGICA DE BD PARA EL RECURSO 'Documentos' (CRUD) ---
# (Funciones movidas desde main.py)

def ingresar_documento(data: dict) -> int:
    conn = None
    query = """
    INSERT INTO documento (tipo, titulo, autor, editorial, anio, edicion, categoria, tipo_medio)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id;
    """
    values = (
        data.get('tipo'), data.get('titulo'), data.get('autor'),
        data.get('editorial'), data.get('anio'), data.get('edicion'),
        data.get('categoria'), data.get('tipo_medio')
    )
    try:
        conn = connection()
        cur = conn.cursor()
        cur.execute(query, values)
        nuevo_id = cur.fetchone()[0]
        conn.commit()
        print(f"Ingreso a la bd correcto, nuevo ID: {nuevo_id}")
        return nuevo_id
    except Exception as e:
        print(f"Error en DB (ingresar_documento): {e}")
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail="Error interno al crear el documento")
    finally:
        if conn:
            cur.close()
            conn.close()
            print("Conexión a la BD cerrada")

def busqueda_por_id(documento_id: int) -> Optional[dict]:
    conn = None
    # CORRECCIÓN: 'editorial' estaba mal escrito en tu main.py ('editoria')
    query = """
        SELECT id, tipo, titulo, autor, editorial, anio, edicion, categoria, tipo_medio
        FROM documento
        WHERE id = %s;
    """
    try:
        conn = connection()
        cur = conn.cursor()
        cur.execute(query, (documento_id,))
        row = cur.fetchone()

        if row is None:
            return None
        
        columnas = [desc[0] for desc in cur.description]
        documento = dict(zip(columnas, row))
        return documento
    
    except Exception as e:
        print(f"Error en DB (busqueda_por_id): {e}")
        raise HTTPException(status_code=500, detail="Error interno al buscar documento por ID")
    finally:
        if conn:
            cur.close()
            conn.close()
            print("Conexión a la BD cerrada.")

def actualizar_documento(id: int, data: dict) -> Optional[dict]:
    conn = None
    set_clauses =[]
    params =[]
    
    for key, value in data.items():
        set_clauses.append(f"{key} = %s")
        params.append(value)
    
    set_query = ", ".join(set_clauses)
    params.append(id) # Añade el ID al final para el WHERE

    query_modify =f"""
        UPDATE documento
        SET {set_query}
        WHERE id = %s
        RETURNING id, tipo, titulo, autor, editorial, anio, edicion, categoria, tipo_medio;
    """
    
    try:
        conn = connection()
        cur = conn.cursor()
        cur.execute(query_modify, tuple(params))
        row = cur.fetchone()

        # Si fetchone() no devuelve nada, el ID no existía
        if row is None:
            return None
        
        conn.commit()
        columnas = [desc[0] for desc in cur.description]
        documento_actualizado = dict(zip(columnas,row))
        
        return documento_actualizado
    
    except Exception as e:
        print(f"Error en DB (actualizar_documento): {e}")
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail="Error interno al actualizar el documento")
    finally:
        if conn:
            cur.close()
            conn.close()
            print("Conexión con la BD cerrada.")
