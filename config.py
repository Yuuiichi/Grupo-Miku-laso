import os
from dotenv import load_dotenv

# Carga variables de un archivo .env si existe
# (esto es útil para desarrollo local SIN Docker)
load_dotenv()

def config():
    """
    Lee la configuración de la base de datos desde las variables de entorno.
    """
    
    # Lee las variables de entorno que definiste en docker-compose.yml
    # .get('DB_HOST', 'localhost') significa: usa 'DB_HOST', pero si no existe, usa 'localhost'
    db_params = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'dbname': os.environ.get('DB_NAME'),
        'port': os.environ.get('DB_PORT', '5432')
    }
    
    # Valida que las variables críticas existan
    if not db_params['user'] or not db_params['password'] or not db_params['dbname']:
        print("¡Error! Variables de entorno de la base de datos no configuradas.")
        print("Asegúrate de que DB_USER, DB_PASSWORD, y DB_NAME estén definidas.")
        # En un caso real, podrías lanzar una excepción:
        # raise ValueError("Variables de base de datos críticas no están configuradas.")
        # Por ahora, solo retornamos un diccionario incompleto para que falle la conexión
    
    return db_params

if __name__ == '__main__':
    # Esto te permite probar si el config.py está leyendo bien
    print("Leyendo configuración...")
    params = config()
    print("Host:", params.get('host'))
    print("Usuario:", params.get('user'))
    print("Base de Datos:", params.get('dbname'))
    if not params.get('user'):
        print("\n¡Configuración incompleta! Revisa tus variables de entorno o tu archivo .env")