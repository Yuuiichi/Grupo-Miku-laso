from app.database import SessionLocal
from app.models.usuario import Usuario

db = SessionLocal()

# Verificar si ya existe
existe = db.query(Usuario).filter(Usuario.email == 'admin@test.cl').first()

if not existe:
    admin = Usuario(
        rut='12345678-9',
        nombres='Admin',
        apellidos='Test',
        email='admin@test.cl',
        rol='admin',
        activo=True
    )
    admin.set_password('password123')
    db.add(admin)
    db.commit()
    print('✅ Usuario admin creado')
else:
    print('⚠️  Usuario admin ya existe')

db.close()