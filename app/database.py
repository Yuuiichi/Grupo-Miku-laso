from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# URL de conexión PostgreSQL
# Formato: postgresql://usuario:password@host:puerto/nombre_bd
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://biblioteca_user:biblioteca_pass@localhost:5432/biblioteca_db"
)

# Crear engine de SQLAlchemy
engine = create_engine(DATABASE_URL)

# Crear SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class para los modelos
Base = declarative_base()

# Dependency para FastAPI
def get_db():
    """
    Dependency que provee una sesión de BD.
    Se cierra automáticamente después de cada request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Función para crear todas las tablas
def create_tables():
    """
    Crear todas las tablas en la BD.
    Ejecutar una vez al inicio.
    """
    import app.models

    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")
    print(f"Tablas: {list(Base.metadata.tables.keys())}")


def connection(): #Creeria que funciona igual que get_db, pero la uso para ROL 2.
    """
    Establece la conexión con la base de datos utilizando DATABASE_URL desde .env .
    """
    try:

        database_url = os.getenv("DATABASE_URL")

        print("Estableciendo conexión con la DB")
        return psycopg2.connect(database_url)
    
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al conectar a la base de datos")


