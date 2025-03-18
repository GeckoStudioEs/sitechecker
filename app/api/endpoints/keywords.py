# app/api/endpoints/keywords.py
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.keywords import (
    KeywordAddRequest, KeywordResponse, KeywordDetail, 
    KeywordGroupCreate, KeywordGroupResponse, KeywordSuggestion
)
from app.services.keywords.keyword_service import KeywordService
from app.db.models import User
from app.utils.permissions import check_project_permission

router = APIRouter()

@router.post("/{project_id}/keywords", response_model=KeywordResponse)
async def add_keywords(
    project_id: int,
    request: KeywordAddRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Añade palabras clave al proyecto para seguimiento
    
    - **project_id**: ID del proyecto
    - **request**: Solicitud con palabras clave y configuración
    """
    # Verificar si el usuario tiene permiso para acceder a este proyecto
    if not check_project_permission(db, current_user.id, project_id, "edit"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes suficientes permisos"
        )
    
    try:
        # Añadir palabras clave
        keyword_service = KeywordService(db)
        added, skipped = keyword_service.add_keywords(project_id, request, current_user.id)
        
        return {"added": added, "skipped": skipped}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al añadir palabras clave: {str(e)}"
        )

@router.delete("/{project_id}/keywords", status_code=status.HTTP_200_OK)
async def delete_keywords(
    project_id: int,
    keyword_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina palabras clave del seguimiento
    
    - **project_id**: ID del proyecto
    - **keyword_ids**: Lista de IDs de palabras clave a eliminar
    """
    # Verificar si el usuario tiene permiso para acceder a este proyecto
    if not check_project_permission(db, current_user.id, project_id, "edit"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes suficientes permisos"
        )
    
    try:
        # Eliminar palabras clave
        keyword_service = KeywordService(db)
        deleted_count = keyword_service.delete_keywords(project_id, keyword_ids)
        
        return {"deleted": deleted_count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar palabras clave: {str(e)}"
        )

@router.get("/{project_id}/keywords", response_model=Dict[str, Any])
async def get_keywords(
    project_id: int,
    search: Optional[str] = Query(None, description="Texto para filtrar palabras clave"),
    group_id: Optional[int] = Query(None, description="ID del grupo para filtrar"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene palabras clave de un proyecto con paginación
    
    - **project_id**: ID del proyecto
    - **search**: Texto para filtrar palabras clave
    - **group_id**: ID del grupo para filtrar
    - **page**: Número de página
    - **page_size**: Tamaño de página
    """
    # Verificar si el usuario tiene permiso para acceder a este proyecto
    if not check_project_permission(db, current_user.id, project_id, "view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes suficientes permisos"
        )
    
    try:
        # Obtener palabras clave
        keyword_service = KeywordService(db)
        keywords = keyword_service.get_keywords(project_id, search, group_id, page, page_size)
        
        return keywords
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener palabras clave: {str(e)}"
        )

@router.get("/keywords/{keyword_id}", response_model=Dict[str, Any])
async def get_keyword_detail(
    keyword_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene detalles de una palabra clave específica
    
    - **keyword_id**: ID de la palabra clave
    """
    try:
        # Obtener palabra clave
        keyword_service = KeywordService(db)
        keyword = keyword_service.get_keyword_detail(keyword_id)
        
        # Verificar si el usuario tiene permiso para acceder al proyecto de esta palabra clave
        if not check_project_permission(db, current_user.id, keyword["project_id"], "view"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes suficientes permisos"
            )
        
        return keyword
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener detalles de la palabra clave: {str(e)}"
        )

@router.post("/{project_id}/keywords/update_positions", response_model=Dict[str, Any])
async def update_positions(
    project_id: int,
    keyword_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza las posiciones de palabras clave
    
    - **project_id**: ID del proyecto
    - **keyword_ids**: Lista opcional de IDs de palabras clave a actualizar
    """
    # Verificar si el usuario tiene permiso para acceder a este proyecto
    if not check_project_permission(db, current_user.id, project_id, "edit"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes suficientes permisos"
        )
    
    try:
        # Actualizar posiciones
        keyword_service = KeywordService(db)
        result = await keyword_service.update_positions(project_id, keyword_ids)
        
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar posiciones: {str(e)}"
        )

@router.post("/{project_id}/keyword_groups", response_model=KeywordGroupResponse)
async def create_keyword_group(
    project_id: int,
    group: KeywordGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un grupo de palabras clave
    
    - **project_id**: ID del proyecto
    - **group**: Datos del grupo a crear
    """
    # Verificar si el usuario tiene permiso para acceder a este proyecto
    if not check_project_permission(db, current_user.id, project_id, "edit"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes suficientes permisos"
        )
    
    try:
        # Crear grupo
        keyword_service = KeywordService(db)
        group_id = keyword_service.create_keyword_group(project_id, group.name, group.keyword_ids)
        
        return {
            "id": group_id,
            "name": group.name,
            "keyword_count": len(group.keyword_ids)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear grupo: {str(e)}"
        )

@router.get("/{project_id}/keyword_groups", response_model=List[Dict[str, Any]])
async def get_keyword_groups(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene grupos de palabras clave de un proyecto
    
    - **project_id**: ID del proyecto
    """
    # Verificar si el usuario tiene permiso para acceder a este proyecto
    if not check_project_permission(db, current_user.id, project_id, "view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes suficientes permisos"
        )
    
    try:
        # Obtener grupos
        keyword_service = KeywordService(db)
        groups = keyword_service.get_keyword_groups(project_id)
        
        return groups
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener grupos: {str(e)}"
        )

@router.delete("/keyword_groups/{group_id}", status_code=status.HTTP_200_OK)
async def delete_keyword_group(
    group_id: int,
    remove_keywords: bool = Query(False, description="Si es True, también elimina las palabras clave"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina un grupo de palabras clave
    
    - **group_id**: ID del grupo a eliminar
    - **remove_keywords**: Si es True, también elimina las palabras clave
    """
    try:
        # Verificar permisos del proyecto al que pertenece el grupo
        group = db.query(KeywordGroup).filter(KeywordGroup.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grupo no encontrado"
            )
            
        # Verificar si el usuario tiene permiso para acceder a este proyecto
        if not check_project_permission(db, current_user.id, group.project_id, "edit"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes suficientes permisos"
            )
        
        # Eliminar grupo
        keyword_service = KeywordService(db)
        keyword_service.delete_keyword_group(group_id, remove_keywords)
        
        return {"message": "Grupo eliminado correctamente"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar grupo: {str(e)}"
        )

@router.get("/keywords/suggestions", response_model=List[Dict[str, Any]])
async def get_keyword_suggestions(
    seed_keyword: str = Query(..., description="Palabra clave semilla"),
    country: str = Query("es", description="Código del país"),
    language: str = Query("es", description="Código del idioma"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene sugerencias de palabras clave basadas en una semilla
    
    - **seed_keyword**: Palabra clave semilla
    - **country**: Código del país
    - **language**: Código del idioma
    """
    try:
        # Obtener sugerencias
        keyword_service = KeywordService(db)
        suggestions = keyword_service.get_suggested_keywords(
            seed_keyword, country, language
        )
        
        return suggestions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener sugerencias: {str(e)}"
        )