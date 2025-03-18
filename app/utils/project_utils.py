from sqlalchemy.orm import Session

from app.db.models import Project, User, ProjectPermission

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
    
    # Consultar la tabla ProjectPermission
    permission = db.query(ProjectPermission).filter(
        ProjectPermission.project_id == project_id,
        ProjectPermission.user_id == user.id
    ).first()
    
    if permission and permission.permission_level in permission_levels.get(required_permission, []):
        return True
    
    return False