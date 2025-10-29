from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routes import auth, admin
from app.api import ejemplares

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(ejemplares.router, prefix=settings.API_V1_STR, tags=["Ejemplares"])
#router = APIRouter(prefix="/ejemplares", tags=["Ejemplares"])
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "API Sistema de Autenticación", "version": settings.VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)