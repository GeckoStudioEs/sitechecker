from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, projects, domains
# Comentar estas importaciones hasta resolver los problemas de dependencias
from app.api.endpoints.audit import router as audit_router
from app.api.endpoints.monitoring import router as monitoring_router
from app.api.endpoints.keywords import router as keywords_router

from app.core.config import settings
from app.db.database import engine, Base

# Crear tablas en la base de datos
# En producción, usar Alembic para migraciones
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SEO Analyzer API",
    description="API para analizar y monitorear SEO de sitios web",
    version="0.1.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, limitar a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers existentes
app.include_router(auth.router, tags=["auth"])
app.include_router(projects.router, tags=["projects"])
app.include_router(domains.router, tags=["domains"])

# Comentar temporalmente hasta resolver problemas de importación
app.include_router(audit_router, prefix="/projects", tags=["audit"])
app.include_router(monitoring_router, prefix="/projects", tags=["monitoring"])
app.include_router(keywords_router, prefix="/projects", tags=["keywords"])

@app.get("/", tags=["root"])
async def root():
    """Endpoint raíz para verificar que la API está funcionando."""
    return {"message": "SEO Analyzer API está funcionando. Acceda a /docs para la documentación."}

@app.get("/health", tags=["health"])
async def health_check():
    """Endpoint para verificar el estado de salud de la API."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)