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
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")


