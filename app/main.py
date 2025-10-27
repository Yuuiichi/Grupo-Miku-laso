from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_tables

# Importar routers
from app.api import ejemplares

# Crear instancia de FastAPI
app = FastAPI(
    title="Sistema de Biblioteca Municipal - Grupo Miku-laso",
    description="API Backend para gestión de préstamos de biblioteca",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas al iniciar
@app.on_event("startup")
def on_startup():
    create_tables()
    print("🚀 API iniciada correctamente")

# Rutas básicas
@app.get("/")
def root():
    return {
        "message": "API Sistema de Biblioteca Municipal - Grupo Miku-laso",
        "docs": "/docs",
        "integrantes": [
            "Cristóbal Espinoza",
            "Sebastián Canales", 
            "Diego Sierra",
            "Adán Contreras",
            "Joaquín Viveros"
        ],
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "grupo": "Miku-laso"}

# Registrar router de ejemplares (ROL 3)
app.include_router(ejemplares.router, prefix="/api")

# Cuando otros roles estén listos, descomentar:
# from app.api import auth, documentos, prestamos, usuarios, reservas
# app.include_router(auth.router, prefix="/api")
# app.include_router(documentos.router, prefix="/api")
# app.include_router(prestamos.router, prefix="/api")
# app.include_router(usuarios.router, prefix="/api")
# app.include_router(reservas.router, prefix="/api")
