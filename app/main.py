from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, create_tables

# Importar todos los routers
from app.routes import auth, admin  # ROL 1 (ya existentes)
from app.api import ejemplares  # ROL 3
from app.api import usuarios, reservas, notificaciones  # ROL 5

# Crear tablas en la base de datos
create_tables()

# Inicializar FastAPI
app = FastAPI(
    title="Sistema de Biblioteca Municipal - Estación Central",
    version="1.0.0",
    description="API Backend para gestión de préstamos, reservas y catálogo de biblioteca",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# REGISTRAR ROUTERS
# ============================================

# ROL 1: Autenticación y validaciones (ya existentes)
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["Autenticación"])
app.include_router(admin.router, prefix=settings.API_V1_STR, tags=["Admin"])

# ROL 3: Ejemplares y disponibilidad
app.include_router(ejemplares.router, prefix=settings.API_V1_STR, tags=["Ejemplares"])

# ROL 5: Usuarios, reservas y notificaciones
app.include_router(usuarios.router, prefix=settings.API_V1_STR, tags=["Usuarios"])
app.include_router(reservas.router, prefix=settings.API_V1_STR, tags=["Reservas"])
app.include_router(notificaciones.router, prefix=settings.API_V1_STR, tags=["Notificaciones"])

# TODO: Agregar cuando estén listos
# from app.api import documentos, catalogo  # ROL 2
# from app.api import prestamos, devoluciones  # ROL 4
# app.include_router(documentos.router, prefix=settings.API_V1_STR, tags=["Documentos"])
# app.include_router(catalogo.router, prefix=settings.API_V1_STR, tags=["Catálogo"])
# app.include_router(prestamos.router, prefix=settings.API_V1_STR, tags=["Préstamos"])
# app.include_router(devoluciones.router, prefix=settings.API_V1_STR, tags=["Devoluciones"])

# ============================================
# ENDPOINTS GENERALES
# ============================================

@app.get("/")
def root():
    """Endpoint raíz - Información de la API"""
    return {
        "message": "🏛️ API Sistema de Biblioteca Municipal",
        "version": "1.0.0",
        "biblioteca": "Estación Central",
        "docs": "/docs",
        "endpoints": {
            "autenticacion": f"{settings.API_V1_STR}/auth",
            "usuarios": f"{settings.API_V1_STR}/usuarios",
            "ejemplares": f"{settings.API_V1_STR}/ejemplares",
            "reservas": f"{settings.API_V1_STR}/reservas",
            "notificaciones": f"{settings.API_V1_STR}/notificaciones"
        }
    }

@app.get("/health")
def health_check():
    """Health check - Verificar que la API está funcionando"""
    return {
        "status": "ok",
        "message": "Sistema operativo",
        "timestamp": "2025-10-27"
    }

@app.get("/info")
def info():
    """Información del sistema"""
    return {
        "nombre": "Sistema de Biblioteca Municipal",
        "version": "1.0.0",
        "biblioteca": "Estación Central",
        "descripcion": "Sistema para gestión de préstamos, reservas y catálogo bibliográfico",
        "roles_implementados": [
            "ROL 1: Autenticación y Validaciones",
            "ROL 3: Ejemplares y Disponibilidad",
            "ROL 5: Usuarios, Reservas y Notificaciones"
        ],
        "roles_pendientes": [
            "ROL 2: Documentos y Catálogo",
            "ROL 4: Préstamos y Devoluciones"
        ],
        "total_endpoints": "48 (planificados)"
    }

# ============================================
# EVENTOS DE INICIO/CIERRE
# ============================================

@app.on_event("startup")
async def startup_event():
    """Ejecutar al iniciar la aplicación"""
    print("=" * 60)
    print("🏛️  SISTEMA DE BIBLIOTECA MUNICIPAL - ESTACIÓN CENTRAL")
    print("=" * 60)
    print("✅ Base de datos conectada")
    print("✅ Tablas creadas/verificadas")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔐 Autenticación: JWT Bearer Token")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Ejecutar al cerrar la aplicación"""
    print("🔴 Cerrando sistema de biblioteca...")

# ============================================
# EJECUTAR APLICACIÓN
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n🚀 Iniciando servidor de desarrollo...")
    print("📖 Documentación interactiva: http://localhost:8000/docs")
    print("📘 Documentación alternativa: http://localhost:8000/redoc")
    print("\n⚠️  Presiona CTRL+C para detener\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
