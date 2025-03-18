# app/api/endpoints/monitoring.py
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.api.deps import get_db, get_current_user
from app.schemas.monitoring import MonitoringSettings, MonitoringResponse, MonitoringSummary
from app.services.monitoring.monitoring_service import MonitoringService
from app.db.models import User, Project, SiteMonitoring
from app.utils.permissions import check_project_permission

router = APIRouter()

@router.put("/{project_id}/monitoring", status_code=status.HTTP_200_OK)
async def update_monitoring_settings(
    project_id: int,
    settings: MonitoringSettings,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza la configuración de monitoreo de un proyecto
    
    - **project_id**: ID del proyecto
    - **settings**: Nueva configuración de monitoreo
    """
    # Verificar si el usuario tiene permiso para acceder a este proyecto
    if not check_project_permission(db, current_user.id, project_id, "edit"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes suficientes permisos"
        )
    
    try:
        # Actualizar configuración
        monitoring_service = MonitoringService(db)
        success = monitoring_service.update_monitoring_settings(project_id, settings)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar la configuración de monitoreo"
            )
            
        return {"message": "Configuración de monitoreo actualizada correctamente"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )

@router.post("/{project_id}/monitoring/check", response_model=MonitoringResponse)
async def start_monitoring_check(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Inicia una nueva verificación de monitoreo
    
    - **project_id**: ID del proyecto
    """
    # Verificar si el usuario tiene permiso para acceder a este proyecto
    if not check_project_permission(db, current_user.id, project_id, "edit"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes suficientes permisos"
        )
    
    try:
        # Iniciar verificación de monitoreo
        monitoring_service = MonitoringService(db)
        monitoring_id = await monitoring_service.check_site(project_id)
        
        return {"monitoring_id": monitoring_id, "status": "in_progress"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar la verificación de monitoreo: {str(e)}"
        )

@router.get("/{project_id}/monitoring/history", response_model=List[Dict[str, Any]])
async def get_monitoring_history(
    project_id: int,
    days: int = Query(30, ge=1, le=365, description="Número de días a incluir en el historial"),
    limit: int = Query(30, ge=1, le=100, description="Número máximo de registros a devolver"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene historial de verificaciones de monitoreo
    
    - **project_id**: ID del proyecto
    - **days**: Número de días a incluir en el historial
    - **limit**: Número máximo de registros a devolver
    """
    # Verificar si el usuario tiene permiso para acceder a este proyecto
    if not check_project_permission(db, current_user.id, project_id, "view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes suficientes permisos"
        )
    
    try:
        # Calcular fecha de inicio
        start_date = datetime.now() - timedelta(days=days)
        
        # Obtener historial
        monitoring_service = MonitoringService(db)
        history = monitoring_service.get_monitoring_history(project_id, start_date, None, limit)
        
        return history
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el historial: {str(e)}"
        )

@router.get("/monitoring/{monitoring_id}/changes", response_model=Dict[str, Any])
async def get_monitoring_changes(
    monitoring_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene cambios detectados en una verificación de monitoreo
    
    - **monitoring_id**: ID del registro de monitoreo
    """
    try:
        # Obtener el registro de monitoreo
        monitoring = db.query(SiteMonitoring).filter(SiteMonitoring.id == monitoring_id).first()
        if not monitoring:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro de monitoreo no encontrado"
            )
        
        # Verificar si el usuario tiene permiso para acceder a este proyecto
        if not check_project_permission(db, current_user.id, monitoring.project_id, "view"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes suficientes permisos"
            )
        
        # Obtener cambios
        monitoring_service = MonitoringService(db)
        changes = monitoring_service.get_monitoring_changes(monitoring_id)
        
        return changes
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los cambios: {str(e)}"
        )

@router.get("/{project_id}/monitoring/status", response_model=Dict[str, Any])
async def get_monitoring_status(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene estado actual de monitoreo
    
    - **project_id**: ID del proyecto
    """
    # Verificar si el usuario tiene permiso para acceder a este proyecto
    if not check_project_permission(db, current_user.id, project_id, "view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes suficientes permisos"
        )
    
    try:
        # Obtener estado
        monitoring_service = MonitoringService(db)
        status = monitoring_service.get_monitoring_status(project_id)
        
        return status
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el estado: {str(e)}"
        )

@router.get("/{project_id}/monitoring/summary", response_model=Dict[str, Any])
async def get_monitoring_summary(
    project_id: int,
    days: int = Query(30, ge=1, le=365, description="Número de días a incluir en el resumen"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene resumen de monitoreo para un período
    
    - **project_id**: ID del proyecto
    - **days**: Número de días a incluir en el resumen
    """
    # Verificar si el usuario tiene permiso para acceder a este proyecto
    if not check_project_permission(db, current_user.id, project_id, "view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes suficientes permisos"
        )
    
    try:
        # Obtener resumen
        monitoring_service = MonitoringService(db)
        summary = monitoring_service.get_monitoring_summary(project_id, days)
        
        return summary
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el resumen: {str(e)}"
        )