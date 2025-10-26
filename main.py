from fastapi import FastAPI
from routes import documentos, catalogo

app = FastAPI()

# Incluir los routers de los diferentes módulos
# 'documentos.router' maneja /documentos/, /documentos/{id}
# 'catalogo.router' maneja /catalogo/
# 'catalogo.router_categorias' maneja /categorias/
app.include_router(documentos.router, prefix="/documentos", tags=["Documentos"])
app.include_router(catalogo.router, prefix="/catalogo", tags=["Catálogo"])
app.include_router(catalogo.router_categorias, prefix="/categorias", tags=["Categorías"])

@app.get("/")
async def root():
    return {"message": "Biblioteca API"}

