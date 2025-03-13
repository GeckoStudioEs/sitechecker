from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Project, User, project_user
from app.schemas.project import (
    Project as ProjectSchema,
    ProjectCreate,
    ProjectUpdate,
    ProjectDetail,
    ProjectPermissionCreate,
    ProjectPermission
)

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/projects", tags=["projects"])

# Función helper para verificar los permisos del usuario en un proyecto
def check_project_permissions(
    db: Session,
    project_id: int,
    user: User,
    required_permission: str = "view"
) -> bool:
    """
    Verifica si el usuario tiene los permisos requeridos para un proyecto.
    
    Args:
        db: Sesión de base de datos
        project_id: ID del proyecto
        user: Usuario actual
        required_permission: Permiso requerido (view, edit, admin)
        
    Returns:
        True si el usuario tiene los permisos requeridos, False en caso contrario
    """
    # Si el usuario es admin, tiene todos los permisos
    if user.role == "admin":
        return True
    
    # Si el usuario es el propietario del proyecto, tiene todos los permisos
    project = db.query(Project).filter(Project.id == project_id).first()
    if project and project.owner_id == user.id:
        return True
    
    # Verificar los permisos del usuario en el proyecto
    permission_levels = {
        "view": ["view", "edit", "admin"],
        "edit": ["edit", "admin"],
        "admin": ["admin"]
    }
    
    # Consultar la tabla de relación project_user
    permission = db.query(project_user).filter(
        project_user.c.project_id == project_id,
        project_user.c.user_id == user.id
    ).first()
    
    if permission and permission.permission_level in permission_levels.get(required_permission, []):
        return True
    
    return False

@router.post("/", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
def create_project(
    *,
    db: Session = Depends(get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Crea un nuevo proyecto.
    """
    # Crear el proyecto en la base de datos
    db_project = Project(
        name=project_in.name,
        domain=project_in.domain,
        protocol=project_in.protocol,
        domain_scope=project_in.domain_scope,
        tags=project_in.tags,
        owner_id=current_user.id,
        is_active=True,
        credits_balance=100  # Valor inicial predeterminado
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Crear el objeto ProjectDetail para devolverlo
    project_detail = ProjectDetail(
        id=db_project.id,
        name=db_project.name,
        domain=db_project.domain,
        protocol=db_project.protocol,
        domain_scope=db_project.domain_scope,
        tags=db_project.tags,
        created_at=db_project.created_at,
        updated_at=db_project.updated_at,
        owner_id=db_project.owner_id,
        is_active=db_project.is_active,
        credits_balance=db_project.credits_balance,
        full_domain=f"{db_project.protocol}://{db_project.domain}"
    )
    
    return project_detail

@router.get("/", response_model=List[ProjectSchema])
def read_projects(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> Any:
    """
    Obtiene la lista de proyectos del usuario.
    """
    # Si el usuario es admin, puede ver todos los proyectos
    if current_user.role == "admin":
        query = db.query(Project)
        
        if is_active is not None:
            query = query.filter(Project.is_active == is_active)
            
        projects = query.offset(skip).limit(limit).all()
        return projects
    
    # Para usuarios normales, obtener sus proyectos propios y en los que tiene permisos
    # Primero, obtener los proyectos que posee
    owned_query = db.query(Project).filter(Project.owner_id == current_user.id)
    
    if is_active is not None:
        owned_query = owned_query.filter(Project.is_active == is_active)
    
    owned_projects = owned_query.all()
    
    # Ahora, obtener los proyectos en los que tiene permisos
    # Consultar la tabla de relación project_user
    project_ids = db.query(project_user.c.project_id).filter(
        project_user.c.user_id == current_user.id
    ).all()
    
    project_ids = [project_id[0] for project_id in project_ids]
    
    if project_ids:
        shared_query = db.query(Project).filter(Project.id.in_(project_ids))
        
        if is_active is not None:
            shared_query = shared_query.filter(Project.is_active == is_active)
            
        shared_projects = shared_query.all()
    else:
        shared_projects = []
    
    # Combinar los proyectos propios y compartidos
    projects = owned_projects + shared_projects
    
    # Eliminar duplicados
    projects = list({project.id: project for project in projects}.values())
    
    return projects

@router.get("/{project_id}", response_model=ProjectDetail)
def read_project(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Obtiene un proyecto por su ID.
    """
    # Verificar si el proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Verificar si el usuario tiene permisos para ver el proyecto
    if not check_project_permissions(db, project_id, current_user, "view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este proyecto"
        )
    
    # Crear el objeto ProjectDetail para devolverlo
    project_detail = ProjectDetail(
        id=project.id,
        name=project.name,
        domain=project.domain,
        protocol=project.protocol,
        domain_scope=project.domain_scope,
        tags=project.tags,
        created_at=project.created_at,
        updated_at=project.updated_at,
        owner_id=project.owner_id,
        is_active=project.is_active,
        credits_balance=project.credits_balance,
        full_domain=f"{project.protocol}://{project.domain}"
    )
    
    return project_detail

@router.put("/{project_id}", response_model=ProjectDetail)
def update_project(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Actualiza un proyecto.
    """
    # Verificar si el proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Verificar si el usuario tiene permisos para editar el proyecto
    if not check_project_permissions(db, project_id, current_user, "edit"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar este proyecto"
        )
    
    # Actualizar los campos del proyecto
    update_data = project_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    # Crear el objeto ProjectDetail para devolverlo
    project_detail = ProjectDetail(
        id=project.id,
        name=project.name,
        domain=project.domain,
        protocol=project.protocol,
        domain_scope=project.domain_scope,
        tags=project.tags,
        created_at=project.created_at,
        updated_at=project.updated_at,
        owner_id=project.owner_id,
        is_active=project.is_active,
        credits_balance=project.credits_balance,
        full_domain=f"{project.protocol}://{project.domain}"
    )
    
    return project_detail

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Elimina un proyecto.
    """
    # Verificar si el proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Verificar si el usuario tiene permisos para eliminar el proyecto
    # Solo el propietario o un admin pueden eliminar un proyecto
    if current_user.role != "admin" and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este proyecto"
        )
    
    # Eliminar el proyecto
    db.delete(project)
    db.commit()
    
    return None

@router.post("/{project_id}/users", response_model=ProjectPermission)
def add_user_to_project(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    permission_in: ProjectPermissionCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Añade un usuario a un proyecto con ciertos permisos.
    """
    # Verificar si el proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Verificar si el usuario tiene permisos para añadir usuarios al proyecto
    if not check_project_permissions(db, project_id, current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para añadir usuarios a este proyecto"
        )
    
    # Verificar si el usuario a añadir existe
    user_to_add = db.query(User).filter(User.id == permission_in.user_id).first()
    
    if not user_to_add:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar si el usuario ya tiene permisos en el proyecto
    existing_permission = db.query(project_user).filter(
        project_user.c.project_id == project_id,
        project_user.c.user_id == permission_in.user_id
    ).first()
    
    if existing_permission:
        # Actualizar el permiso existente
        db.execute(
            project_user.update().where(
                project_user.c.project_id == project_id,
                project_user.c.user_id == permission_in.user_id
            ).values(
                permission_level=permission_in.permission_level,
                created_by=current_user.id
            )
        )
    else:
        # Crear un nuevo permiso
        db.execute(
            project_user.insert().values(
                project_id=project_id,
                user_id=permission_in.user_id,
                permission_level=permission_in.permission_level,
                created_by=current_user.id
            )
        )
    
    db.commit()
    
    # Obtener el permiso recién creado o actualizado
    new_permission = db.query(project_user).filter(
        project_user.c.project_id == project_id,
        project_user.c.user_id == permission_in.user_id
    ).first()
    
    return ProjectPermission(
        project_id=project_id,
        user_id=permission_in.user_id,
        permission_level=permission_in.permission_level,
        created_at=new_permission.created_at
    )

@router.delete("/{project_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_from_project(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Elimina un usuario de un proyecto.
    """
    # Verificar si el proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Verificar si el usuario tiene permisos para eliminar usuarios del proyecto
    if not check_project_permissions(db, project_id, current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar usuarios de este proyecto"
        )
    
    # Verificar si el usuario a eliminar existe y tiene permisos en el proyecto
    existing_permission = db.query(project_user).filter(
        project_user.c.project_id == project_id,
        project_user.c.user_id == user_id
    ).first()
    
    if not existing_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no tiene permisos en este proyecto"
        )
    
    # Verificar que no se está intentando eliminar al propietario del proyecto
    if project.owner_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar al propietario del proyecto"
        )
    
    # Eliminar el permiso
    db.execute(
        project_user.delete().where(
            project_user.c.project_id == project_id,
            project_user.c.user_id == user_id
        )
    )
    
    db.commit()
    
    return None

@router.get("/{project_id}/users", response_model=List[ProjectPermission])
def get_project_users(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Obtiene la lista de usuarios que tienen permisos en un proyecto.
    """
    # Verificar si el proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Verificar si el usuario tiene permisos para ver los usuarios del proyecto
    if not check_project_permissions(db, project_id, current_user, "view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver los usuarios de este proyecto"
        )
    
    # Obtener los permisos de los usuarios en el proyecto
    permissions = db.query(project_user).filter(
        project_user.c.project_id == project_id
    ).all()
    
    # Convertir los permisos a objetos ProjectPermission
    project_permissions = [
        ProjectPermission(
            project_id=permission.project_id,
            user_id=permission.user_id,
            permission_level=permission.permission_level,
            created_at=permission.created_at
        )
        for permission in permissions
    ]
    
    return project_permissions