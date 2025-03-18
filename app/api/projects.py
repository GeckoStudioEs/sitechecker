from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db.database import get_db
from app.db.models import User, Project, ProjectPermission
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from app.api.deps import get_current_user
from app.utils.permissions import check_project_permission

router = APIRouter()

class AddUserRequest(BaseModel):
    user_id: int
    permission_level: str = Field(..., description="Nivel de permiso: view, edit, admin")

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Crea un nuevo proyecto asociado al usuario actual.
    """
    project = Project(
        name=project_in.name,
        domain=project_in.domain,
        protocol=project_in.protocol,
        domain_scope=project_in.domain_scope,
        owner_id=current_user.id,
        tags=project_in.tags or []
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("/", response_model=ProjectListResponse)
def read_projects(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    search: Optional[str] = Query(None, description="Buscar por nombre o dominio")
):
    """
    Obtiene todos los proyectos a los que tiene acceso el usuario actual.
    """
    # Consulta base: proyectos propios o con permisos
    query = db.query(Project).filter(
        (Project.owner_id == current_user.id) | 
        (Project.id.in_(
            db.query(ProjectPermission.project_id)
            .filter(ProjectPermission.user_id == current_user.id)
        ))
    )
    
    # Aplicar filtro de búsqueda si existe
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Project.name.ilike(search_term)) | 
            (Project.domain.ilike(search_term))
        )
    
    # Contar total de resultados
    total = query.count()
    
    # Aplicar paginación
    projects = query.order_by(Project.name).offset(skip).limit(limit).all()
    
    return {
        "items": projects,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit if limit > 0 else 1
    }

@router.get("/{project_id}", response_model=ProjectResponse)
def read_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Obtiene un proyecto específico por ID.
    """
    # Verificar si el usuario tiene permiso para acceder a este proyecto
    if not check_project_permission(db, current_user.id, project_id, "view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a este proyecto"
        )
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proyecto no encontrado: {project_id}"
        )
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int, 
    project_in: ProjectUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza un proyecto existente.
    """
    # Verificar si el usuario tiene permiso para editar este proyecto
    if not check_project_permission(db, current_user.id, project_id, "edit"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar este proyecto"
        )
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proyecto no encontrado: {project_id}"
        )
    
    # Actualizar solo los campos proporcionados
    update_data = project_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Elimina un proyecto.
    """
    # Verificar si el usuario tiene permiso para administrar este proyecto
    if not check_project_permission(db, current_user.id, project_id, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este proyecto"
        )
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proyecto no encontrado: {project_id}"
        )
    
    db.delete(project)
    db.commit()
    return None

@router.post("/{project_id}/users", status_code=status.HTTP_200_OK)
def add_user_to_project(
    project_id: int, 
    user_request: AddUserRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Añade un usuario a un proyecto con un nivel de permiso específico.
    """
    # Verificar si el usuario tiene permiso para administrar este proyecto
    if not check_project_permission(db, current_user.id, project_id, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para administrar este proyecto"
        )
    
    # Verificar si el proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proyecto no encontrado: {project_id}"
        )
    
    # Verificar si el usuario a añadir existe
    user = db.query(User).filter(User.id == user_request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario no encontrado: {user_request.user_id}"
        )
    
    # Verificar si ya existe el permiso
    existing_permission = db.query(ProjectPermission).filter(
        ProjectPermission.project_id == project_id,
        ProjectPermission.user_id == user_request.user_id
    ).first()
    
    if existing_permission:
        # Actualizar el nivel de permiso
        existing_permission.permission_level = user_request.permission_level
        db.add(existing_permission)
    else:
        # Crear nuevo permiso
        permission = ProjectPermission(
            project_id=project_id,
            user_id=user_request.user_id,
            permission_level=user_request.permission_level,
            created_by=current_user.id
        )
        db.add(permission)
    
    db.commit()
    return {"message": "Usuario añadido al proyecto con éxito"}

@router.delete("/{project_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_from_project(
    project_id: int, 
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Elimina un usuario de un proyecto.
    """
    # Verificar si el usuario tiene permiso para administrar este proyecto
    if not check_project_permission(db, current_user.id, project_id, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para administrar este proyecto"
        )
    
    # Verificar si existe el permiso
    permission = db.query(ProjectPermission).filter(
        ProjectPermission.project_id == project_id,
        ProjectPermission.user_id == user_id
    ).first()
    
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {user_id} no encontrado en el proyecto {project_id}"
        )
    
    db.delete(permission)
    db.commit()
    return None

@router.get("/{project_id}/users", status_code=status.HTTP_200_OK)
def get_project_users(
    project_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene los usuarios con acceso a un proyecto y sus niveles de permiso.
    """
    # Verificar si el usuario tiene permiso para ver este proyecto
    if not check_project_permission(db, current_user.id, project_id, "view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este proyecto"
        )
    
    # Verificar si el proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proyecto no encontrado: {project_id}"
        )
    
    # Obtener usuarios con permisos
    user_permissions = db.query(
        User.id, User.email, User.first_name, User.last_name, 
        ProjectPermission.permission_level
    ).join(
        ProjectPermission, User.id == ProjectPermission.user_id
    ).filter(
        ProjectPermission.project_id == project_id
    ).all()
    
    # Añadir owner del proyecto
    owner = db.query(
        User.id, User.email, User.first_name, User.last_name
    ).filter(User.id == project.owner_id).first()
    
    result = {
        "owner": {
            "id": owner.id,
            "email": owner.email,
            "first_name": owner.first_name,
            "last_name": owner.last_name,
            "permission_level": "owner"
        } if owner else None,
        "users": [
            {
                "id": user_id,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "permission_level": permission_level
            }
            for user_id, email, first_name, last_name, permission_level in user_permissions
        ]
    }
    
    return result