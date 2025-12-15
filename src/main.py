from fastapi import FastAPI
from fastapi.routing import APIRoute  # ← Importante: esto es lo que necesitas

import src.models.models as models
import database
from routers import series, users 


# 1. Crear Tablas (Si no existen)
models.Base.metadata.create_all(bind=database.engine)


# Función correcta para generar operationId limpio
def custom_generate_unique_id(route: APIRoute):
    return f"{route.name}"


# 2. Iniciar App
app = FastAPI(
    title="ONNXProject API",
    description="API para gestión de Anime, Manga, JAV y Doujins",
    version="0.1.0",
    generate_unique_id_function=custom_generate_unique_id,
)


# 3. Conectar los Routers
app.include_router(series.router, tags=["Series"])
app.include_router(users.router, tags=["Users"])


@app.get("/")
def read_root():
    return {
        "message": "API Activa",
        "docs": "Ve a /docs para usar la API",
    }