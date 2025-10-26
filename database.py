import psycopg2
from config import config # Asumo que tienes config.py en la raíz
from fastapi import HTTPException

def connection():
    """
    Establece la conexión con la base de datos.
    """
    try:
        params = config() # Hace lectura del archivo ini
        print("Estableciendo conexión con la DB")
        return psycopg2.connect(**params)
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al conectar a la base de datos")

