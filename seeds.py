"""
Script para poblar la base de datos con datos de prueba.
Ejecutar: python seeds.py
"""

from app.database import SessionLocal
from app.models.usuario import Usuario
from app.models.documento import Documento
from app.models.ejemplar import Ejemplar
from app.models.reserva import Reserva
from datetime import datetime, timedelta, date

def clear_database(db):
    """Limpiar todas las tablas (CUIDADO en producción!)"""
    print("🗑️  Limpiando base de datos...")
    
    try:
        db.query(Reserva).delete()
        db.query(Ejemplar).delete()
        db.query(Documento).delete()
        # No eliminamos usuarios para mantener admin
        db.commit()
        print("✅ Base de datos limpiada")
    except Exception as e:
        print(f"❌ Error limpiando BD: {e}")
        db.rollback()

def crear_usuarios(db):
    """Crear usuarios de prueba"""
    print("\n👥 Creando usuarios...")
    
    usuarios_data = [
        {
            "rut": "12345678-9",
            "nombres": "Admin",
            "apellidos": "Sistema",
            "email": "admin@biblioteca.cl",
            "rol": "admin",
            "activo": True
        },
        {
            "rut": "23456789-0",
            "nombres": "María",
            "apellidos": "González",
            "email": "bibliotecario@biblioteca.cl",
            "rol": "bibliotecario",
            "activo": True
        },
        {
            "rut": "34567890-1",
            "nombres": "Juan",
            "apellidos": "Pérez",
            "email": "juan.perez@email.com",
            "rol": "usuario",
            "activo": True
        },
        {
            "rut": "45678901-2",
            "nombres": "Ana",
            "apellidos": "Torres",
            "email": "ana.torres@email.com",
            "rol": "usuario",
            "activo": True
        },
        {
            "rut": "56789012-3",
            "nombres": "Pedro",
            "apellidos": "Ramírez",
            "email": "pedro.ramirez@email.com",
            "rol": "usuario",
            "activo": False  # Pendiente de activación
        }
    ]
    
    usuarios_creados = []
    
    for user_data in usuarios_data:
        # Verificar si ya existe
        usuario_existe = db.query(Usuario).filter(Usuario.rut == user_data["rut"]).first()
        
        if usuario_existe:
            print(f"⚠️  Usuario {user_data['nombres']} ya existe, saltando...")
            usuarios_creados.append(usuario_existe)
            continue
        
        usuario = Usuario(
            rut=user_data["rut"],
            nombres=user_data["nombres"],
            apellidos=user_data["apellidos"],
            email=user_data["email"],
            rol=user_data["rol"],
            activo=user_data["activo"]
        )
        usuario.set_password("password123")  # Todos con misma password para testing
        
        db.add(usuario)
        usuarios_creados.append(usuario)
        print(f"✅ Usuario creado: {usuario.nombres} {usuario.apellidos} ({usuario.rol})")
    
    db.commit()
    return usuarios_creados

def crear_documentos(db):
    """Crear documentos de prueba"""
    print("\n📚 Creando documentos...")
    
    documentos_data = [
        {
            "tipo": "libro",
            "titulo": "Cien Años de Soledad",
            "autor": "Gabriel García Márquez",
            "editorial": "Sudamericana",
            "año": 1967,
            "edicion": "Primera",
            "categoria": "literatura_chilena",
            "tipo_medio": "fisico"
        },
        {
            "tipo": "libro",
            "titulo": "La Casa de los Espíritus",
            "autor": "Isabel Allende",
            "editorial": "Plaza & Janés",
            "año": 1982,
            "categoria": "literatura_chilena",
            "tipo_medio": "fisico"
        },
        {
            "tipo": "libro",
            "titulo": "El Principito",
            "autor": "Antoine de Saint-Exupéry",
            "editorial": "Gallimard",
            "año": 1943,
            "categoria": "literatura_francesa",
            "tipo_medio": "fisico"
        },
        {
            "tipo": "libro",
            "titulo": "Python para Principiantes",
            "autor": "John Smith",
            "editorial": "Tech Books",
            "año": 2023,
            "categoria": "tecnico_español",
            "tipo_medio": "fisico"
        },
        {
            "tipo": "libro",
            "titulo": "Clean Code",
            "autor": "Robert C. Martin",
            "editorial": "Prentice Hall",
            "año": 2008,
            "categoria": "tecnico_ingles",
            "tipo_medio": "fisico"
        },
        {
            "tipo": "audio",
            "titulo": "Historia de Chile - Audiolibro",
            "autor": "Varios autores",
            "editorial": "Biblioteca Nacional",
            "año": 2020,
            "categoria": "historia",
            "tipo_medio": "cd"
        },
        {
            "tipo": "video",
            "titulo": "Documental: La Patagonia",
            "autor": "Documentalistas Chile",
            "editorial": "TVN",
            "año": 2019,
            "categoria": "documental",
            "tipo_medio": "dvd"
        },
        {
            "tipo": "revista",
            "titulo": "National Geographic - Edición Especial",
            "autor": "National Geographic Society",
            "editorial": "National Geographic",
            "año": 2024,
            "categoria": "ciencia",
            "tipo_medio": "fisico"
        },
        {
            "tipo": "libro",
            "titulo": "Don Quijote de la Mancha",
            "autor": "Miguel de Cervantes",
            "editorial": "Cátedra",
            "año": 1605,
            "categoria": "literatura_española",
            "tipo_medio": "fisico"
        },
        {
            "tipo": "libro",
            "titulo": "Harry Potter y la Piedra Filosofal",
            "autor": "J.K. Rowling",
            "editorial": "Salamandra",
            "año": 1997,
            "categoria": "literatura_inglesa",
            "tipo_medio": "fisico"
        }
    ]
    
    documentos_creados = []
    
    for doc_data in documentos_data:
        documento = Documento(**doc_data)
        db.add(documento)
        documentos_creados.append(documento)
        print(f"✅ Documento creado: {documento.titulo} ({documento.tipo})")
    
    db.commit()
    
    # Refrescar para obtener IDs
    for doc in documentos_creados:
        db.refresh(doc)
    
    return documentos_creados

def crear_ejemplares(db, documentos):
    """Crear ejemplares de cada documento"""
    print("\n📖 Creando ejemplares...")
    
    ejemplares_creados = []
    ubicaciones = ["A1-E1", "A1-E2", "A2-E1", "A2-E2", "A3-E1", "B1-E1", "B2-E1"]
    estados = ["disponible", "prestado", "en_sala"]
    
    for doc in documentos:
        # Crear 3-5 ejemplares por documento
        num_ejemplares = 3 if doc.tipo == "revista" else 5
        
        for i in range(num_ejemplares):
            codigo = f"{doc.tipo.upper()[:3]}-{doc.id:03d}-{i+1:02d}"
            ubicacion = ubicaciones[i % len(ubicaciones)]
            
            # La mayoría disponibles, algunos prestados
            if i == 0 and doc.id % 3 == 0:
                estado = "prestado"
            elif i == 1 and doc.id % 4 == 0:
                estado = "en_sala"
            else:
                estado = "disponible"
            
            ejemplar = Ejemplar(
                documento_id=doc.id,
                codigo=codigo,
                ubicacion=ubicacion,
                estado=estado
            )
            
            db.add(ejemplar)
            ejemplares_creados.append(ejemplar)
        
        print(f"✅ {num_ejemplares} ejemplares creados para: {doc.titulo}")
    
    db.commit()
    
    # Refrescar para obtener IDs
    for ej in ejemplares_creados:
        db.refresh(ej)
    
    return ejemplares_creados

def crear_reservas(db, usuarios, documentos):
    """Crear algunas reservas de prueba"""
    print("\n📅 Creando reservas...")
    
    # Solo usuarios normales (no admin ni bibliotecario)
    usuarios_normales = [u for u in usuarios if u.rol == "usuario" and u.activo]
    
    if not usuarios_normales:
        print("⚠️  No hay usuarios normales activos, saltando reservas...")
        return []
    
    reservas_data = [
        {
            "usuario": usuarios_normales[0],
            "documento": documentos[0],
            "fecha_reserva": date.today() + timedelta(days=3),
            "estado": "pendiente"
        },
        {
            "usuario": usuarios_normales[0],
            "documento": documentos[2],
            "fecha_reserva": date.today() + timedelta(days=5),
            "estado": "pendiente"
        },
        {
            "usuario": usuarios_normales[1] if len(usuarios_normales) > 1 else usuarios_normales[0],
            "documento": documentos[4],
            "fecha_reserva": date.today() + timedelta(days=2),
            "estado": "activa"
        }
    ]
    
    reservas_creadas = []
    
    for res_data in reservas_data:
        reserva = Reserva(
            usuario_id=res_data["usuario"].id,
            documento_id=res_data["documento"].id,
            fecha_reserva=res_data["fecha_reserva"],
            estado=res_data["estado"]
        )
        
        db.add(reserva)
        reservas_creadas.append(reserva)
        print(f"✅ Reserva creada: {res_data['usuario'].nombres} -> {res_data['documento'].titulo}")
    
    db.commit()
    return reservas_creadas

def mostrar_resumen(db):
    """Mostrar resumen de datos creados"""
    print("\n" + "="*60)
    print("📊 RESUMEN DE DATOS CREADOS")
    print("="*60)
    
    total_usuarios = db.query(Usuario).count()
    usuarios_activos = db.query(Usuario).filter(Usuario.activo == True).count()
    
    total_documentos = db.query(Documento).count()
    total_ejemplares = db.query(Ejemplar).count()
    ejemplares_disponibles = db.query(Ejemplar).filter(Ejemplar.estado == "disponible").count()
    
    total_reservas = db.query(Reserva).count()
    reservas_pendientes = db.query(Reserva).filter(Reserva.estado == "pendiente").count()
    
    print(f"👥 Usuarios: {total_usuarios} ({usuarios_activos} activos)")
    print(f"📚 Documentos: {total_documentos}")
    print(f"📖 Ejemplares: {total_ejemplares} ({ejemplares_disponibles} disponibles)")
    print(f"📅 Reservas: {total_reservas} ({reservas_pendientes} pendientes)")
    print("="*60)
    
    # Mostrar credenciales de acceso
    print("\n🔑 CREDENCIALES DE ACCESO")
    print("="*60)
    print("Admin:")
    print("  Email: admin@biblioteca.cl")
    print("  Password: password123")
    print("\nBibliotecario:")
    print("  Email: bibliotecario@biblioteca.cl")
    print("  Password: password123")
    print("\nUsuario normal:")
    print("  Email: juan.perez@email.com")
    print("  Password: password123")
    print("="*60)

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🌱 INICIANDO SEED DE BASE DE DATOS")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Preguntar si limpiar BD
        respuesta = input("\n¿Limpiar base de datos antes de crear datos? (s/n): ")
        if respuesta.lower() == 's':
            clear_database(db)
        
        # Crear datos
        usuarios = crear_usuarios(db)
        documentos = crear_documentos(db)
        ejemplares = crear_ejemplares(db, documentos)
        reservas = crear_reservas(db, usuarios, documentos)
        
        # Mostrar resumen
        mostrar_resumen(db)
        
        print("\n✅ Seed completado exitosamente!")
        print("🚀 Puedes iniciar el servidor con: uvicorn app.main:app --reload")
        print("📖 Documentación: http://localhost:8000/docs\n")
        
    except Exception as e:
        print(f"\n❌ Error durante el seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()