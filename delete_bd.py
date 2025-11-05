#!/usr/bin/env python3
"""Limpia todas las tablas de la BD"""

from app.database import engine, Base

print("🗑️  Eliminando todas las tablas...")

# Importar todos los modelos
from app.models.usuario import Usuario
from app.models.documento import Documento
from app.models.ejemplar import Ejemplar
from app.models.biblioteca import Biblioteca
from app.models.prestamos import Prestamo

Base.metadata.drop_all(bind=engine)
print("✅ Tablas eliminadas")

print("\n📋 Recreando tablas...")
Base.metadata.create_all(bind=engine)
print("✅ Tablas recreadas")