#!/usr/bin/python
from configparser import ConfigParser
import os

def config(filename='database.ini', section='postgresql'):
    # Crear un parser
    parser = ConfigParser()
    
    # Comprobar si el archivo .ini existe
    if not os.path.exists(filename):
        raise Exception(f"Archivo de configuración {filename} no encontrado.")
        
    # Leer el archivo de configuración
    parser.read(filename)

    # Obtener la sección, por defecto 'postgresql'
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Sección {0} no encontrada en el archivo {1}'.format(section, filename))

    return db