from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, projects, domains
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

# Incluir routers
app.include_router(auth.router, tags=["auth"])
app.include_router(projects.router, tags=["projects"])
app.include_router(domains.router, tags=["domains"])

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