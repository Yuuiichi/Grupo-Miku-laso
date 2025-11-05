#!/usr/bin/env python3
"""Setup inicial con stub de documento"""

print("🚀 Setup del sistema...")
print()

# 1. Crear tablas
print("📋 Creando tablas...")
from app.database import create_tables
create_tables()
print()

# 2. Crear usuarios
print("👤 Creando usuarios...")
from app.database import SessionLocal
from app.models.usuario import Usuario
from app.models.documento import Documento
from app.models.ejemplar import Ejemplar

db = SessionLocal()

try:
    # Usuarios
    usuarios = [
        {'rut': '12345678-9', 'nombres': 'Admin', 'apellidos': 'Test', 
         'email': 'admin@test.cl', 'rol': 'admin', 'activo': True},
        {'rut': '23456789-0', 'nombres': 'Biblio', 'apellidos': 'Test',
         'email': 'biblio@test.cl', 'rol': 'bibliotecario', 'activo': True},
        {'rut': '34567890-1', 'nombres': 'Usuario', 'apellidos': 'Test',
         'email': 'usuario@test.cl', 'rol': 'usuario', 'activo': True}
    ]
    
    for user_data in usuarios:
        existe = db.query(Usuario).filter(Usuario.email == user_data['email']).first()
        if not existe:
            usuario = Usuario(**user_data)
            usuario.set_password('password123')
            db.add(usuario)
            print(f"✅ {user_data['rol']}: {user_data['email']}")
    
    db.commit()
    print()
    
    # 3. Crear documentos stub
    print("📚 Creando documentos de prueba...")
    
    if db.query(Documento).count() == 0:
        docs = [
            Documento(tipo='libro', titulo='Cien Años de Soledad', autor='García Márquez'),
            Documento(tipo='libro', titulo='Don Quijote', autor='Cervantes'),
            Documento(tipo='libro', titulo='El Principito', autor='Saint-Exupéry')
        ]
        for doc in docs:
            db.add(doc)
        db.commit()
        print(f"✅ {len(docs)} documentos creados")
    else:
        print("⚠️  Ya existen documentos")
    
    print()
    
    # 4. Crear ejemplares
    print("📖 Creando ejemplares de prueba...")
    
    if db.query(Ejemplar).count() == 0:
        documentos = db.query(Documento).all()
        ejemplares_creados = 0
        
        for i, doc in enumerate(documentos, 1):
            for j in range(1, 4):  # 3 ejemplares por documento
                ej = Ejemplar(
                    documento_id=doc.id,
                    codigo=f"LIB-{i:03d}-{j:02d}",
                    ubicacion=f"A{i}-E{j}",
                    estado="disponible"
                )
                db.add(ej)
                ejemplares_creados += 1
        
        db.commit()
        print(f"✅ {ejemplares_creados} ejemplares creados")
    else:
        print("⚠️  Ya existen ejemplares")
    
    print()
    print('='*60)
    print('✅ Setup completado exitosamente')
    print('='*60)
    print()
    print('🔑 CREDENCIALES:')
    print('   admin@test.cl / password123 (admin)')
    print('   biblio@test.cl / password123 (bibliotecario)')
    print('   usuario@test.cl / password123 (usuario)')
    print()
    print('🚀 Iniciar: uvicorn app.main:app --reload')
    print('📚 Docs: http://localhost:8000/docs')
    print()

except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()