"""
Script para poblar la BD con ejemplares de prueba.
Ejecutar DESPUÉS de que ROL 2 haya creado los documentos.
"""

from app.database import SessionLocal
from app.models.ejemplar import Ejemplar

def crear_ejemplares_prueba():
    db = SessionLocal()
    
    ejemplares = [
        # Documento 1: Los Juegos del Hambre (3 ejemplares)
        Ejemplar(documento_id=1, codigo="LIT-ESP-001-01", estado="disponible", ubicacion="A3-E2"),
        Ejemplar(documento_id=1, codigo="LIT-ESP-001-02", estado="disponible", ubicacion="A3-E2"),
        Ejemplar(documento_id=1, codigo="LIT-ESP-001-03", estado="prestado", ubicacion="A3-E2"),
        
        # Documento 2: En Llamas (2 ejemplares)
        Ejemplar(documento_id=2, codigo="LIT-ESP-002-01", estado="disponible", ubicacion="A3-E3"),
        Ejemplar(documento_id=2, codigo="LIT-ESP-002-02", estado="en_sala", ubicacion="A3-E3"),
        
        # Documento 3: Sinsajo (4 ejemplares)
        Ejemplar(documento_id=3, codigo="LIT-ESP-003-01", estado="disponible", ubicacion="A3-E4"),
        Ejemplar(documento_id=3, codigo="LIT-ESP-003-02", estado="disponible", ubicacion="A3-E4"),
        Ejemplar(documento_id=3, codigo="LIT-ESP-003-03", estado="disponible", ubicacion="A3-E4"),
        Ejemplar(documento_id=3, codigo="LIT-ESP-003-04", estado="mantenimiento", ubicacion="A3-E4"),
        
        # Documento 4: Harry Potter (5 ejemplares)
        Ejemplar(documento_id=4, codigo="LIT-ING-001-01", estado="disponible", ubicacion="B2-E1"),
        Ejemplar(documento_id=4, codigo="LIT-ING-001-02", estado="disponible", ubicacion="B2-E1"),
        Ejemplar(documento_id=4, codigo="LIT-ING-001-03", estado="disponible", ubicacion="B2-E1"),
        Ejemplar(documento_id=4, codigo="LIT-ING-001-04", estado="prestado", ubicacion="B2-E1"),
        Ejemplar(documento_id=4, codigo="LIT-ING-001-05", estado="prestado", ubicacion="B2-E1"),
        
        # Documento 5: 1984 (3 ejemplares)
        Ejemplar(documento_id=5, codigo="LIT-ING-002-01", estado="disponible", ubicacion="B2-E5"),
        Ejemplar(documento_id=5, codigo="LIT-ING-002-02", estado="disponible", ubicacion="B2-E5"),
        Ejemplar(documento_id=5, codigo="LIT-ING-002-03", estado="disponible", ubicacion="B2-E5"),
    ]
    
    for ejemplar in ejemplares:
        db.add(ejemplar)
    
    db.commit()
    print(f"✅ {len(ejemplares)} ejemplares creados exitosamente")
    db.close()

if __name__ == "__main__":
    crear_ejemplares_prueba()