from fastapi import APIRouter

from app.api.endpoints import users, auth, projects, domains, audit, keywords, monitoring, services

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(domains.router, prefix="/domains", tags=["domains"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(services.router, prefix="/services", tags=["services"])