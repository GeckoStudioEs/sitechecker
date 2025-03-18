# app/api/endpoints/audit.py
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.audit import AuditSettings, AuditSummary, AuditResponse, AuditStatusResponse
from app.services.audit.audit_service import AuditService
from app.db.models import User, Project, SiteAudit
from app.utils.permissions import check_project_permission

router = APIRouter()

@router.post("/{project_id}/audits", response_model=AuditResponse, status_code=status.HTTP_201_CREATED)
async def start_audit(
    project_id: int,
    settings: AuditSettings,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Inicia una nueva auditoría del sitio
    
    - **project_id**: ID del proyecto
    - **settings**: Configuración de la auditoría
    """
    # Verificar si el usuario tiene permiso para acceder a este proyecto
    if not check_project_permission(db, current_user.id, project_id, "edit"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes suficientes permisos"
        )
    
    # Iniciar la auditoría
    try:
        audit_service = AuditService(db)
        audit_id = await audit_service.start_audit(project_id, settings, current_user.id)
        
        return {"audit_id": audit_id, "status": "in_progress"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar la auditoría: {str(e)}"
        )

@router.get("/audits/{audit_id}/status", response_model=Dict[str, Any])
async def get_audit_status(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el estado de una auditoría
    
    - **audit_id**: ID de la auditoría
    """
    try:
        # Obtener la auditoría
        audit = db.query(SiteAudit).filter(SiteAudit.id == audit_id).first()
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Auditoría no encontrada"
            )
        
        # Verificar si el usuario tiene permiso para acceder a este proyecto
        if not check_project_permission(db, current_user.id, audit.project_id, "view"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes suficientes permisos"
            )
        
        # Obtener el estado
        audit_service = AuditService(db)
        return audit_service.get_audit_status(audit_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el estado de la auditoría: {str(e)}"
        )

@router.get("/audits/{audit_id}/summary", response_model=AuditSummary)
async def get_audit_summary(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el resumen de una auditoría
    
    - **audit_id**: ID de la auditoría
    """
    try:
        # Obtener la auditoría
        audit = db.query(SiteAudit).filter(SiteAudit.id == audit_id).first()
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Auditoría no encontrada"
            )
        
        # Verificar si el usuario tiene permiso para acceder a este proyecto
        if not check_project_permission(db, current_user.id, audit.project_id, "view"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes suficientes permisos"
            )
        
        # Obtener el resumen para auditorías completadas
        audit_service = AuditService(db)
        return audit_service.get_audit_summary(audit_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el resumen de la auditoría: {str(e)}"
        )

@router.get("/audits/{audit_id}/issues", response_model=Dict[str, Any])
async def get_audit_issues(
    audit_id: int,
    severity: Optional[str] = Query(None, description="Filtrar por severidad (critical, warning, opportunity, notice)"),
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene problemas detectados en una auditoría
    
    - **audit_id**: ID de la auditoría
    - **severity**: Filtrar por severidad
    - **category**: Filtrar por categoría
    - **page**: Número de página para paginación
    - **page_size**: Tamaño de página para paginación
    """
    try:
        # Obtener la auditoría
        audit = db.query(SiteAudit).filter(SiteAudit.id == audit_id).first()
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Auditoría no encontrada"
            )
        
        # Verificar si el usuario tiene permiso para acceder a este proyecto
        if not check_project_permission(db, current_user.id, audit.project_id, "view"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes suficientes permisos"
            )
        
        # Obtener los problemas
        audit_service = AuditService(db)
        return audit_service.get_audit_issues(audit_id, severity, category, page, page_size)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los problemas de la auditoría: {str(e)}"
        )

@router.get("/audits/{audit_id}/pages/{url:path}", response_model=Dict[str, Any])
async def get_page_details(
    audit_id: int,
    url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene detalles completos de una página específica
    
    - **audit_id**: ID de la auditoría
    - **url**: URL de la página (codificada)
    """
    try:
        from app.utils.url_utils import decode_url
        
        # Decodificar URL
        decoded_url = decode_url(url)
        
        # Obtener la auditoría
        audit = db.query(SiteAudit).filter(SiteAudit.id == audit_id).first()
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Auditoría no encontrada"
            )
        
        # Verificar si el usuario tiene permiso para acceder a este proyecto
        if not check_project_permission(db, current_user.id, audit.project_id, "view"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes suficientes permisos"
            )
        
        # Obtener detalles de la página
        audit_service = AuditService(db)
        return audit_service.get_page_details(audit_id, decoded_url)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los detalles de la página: {str(e)}"
        )