# app/utils/permissions.py
from sqlalchemy.orm import Session
from app.db.models import Project, ProjectPermission, User

def check_project_permission(db: Session, user_id: int, project_id: int, required_level: str) -> bool:
    """
    Verifica si un usuario tiene el nivel de permisos requerido para un proyecto
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        project_id: ID del proyecto
        required_level: Nivel de permisos requerido ('view', 'edit', 'admin')
        
    Returns:
        True si el usuario tiene el nivel de permisos requerido, False en caso contrario
    """
    # Verificar si el usuario es dueño del proyecto
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return False
        
    # El dueño del proyecto siempre tiene todos los permisos
    if project.owner_id == user_id:
        return True
        
    # Verificar si el usuario es administrador
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.role == 'admin':
        return True
        
    # Verificar permisos específicos del proyecto
    permission = db.query(ProjectPermission).filter(
        ProjectPermission.project_id == project_id,
        ProjectPermission.user_id == user_id
    ).first()
    
    if not permission:
        return False
        
    # Verificar nivel de permisos
    if required_level == 'view':
        # Cualquier nivel de permisos permite ver
        return permission.permission_level in ['view', 'edit', 'admin']
    elif required_level == 'edit':
        # Solo edit y admin pueden editar
        return permission.permission_level in ['edit', 'admin']
    elif required_level == 'admin':
        # Solo admin puede administrar
        return permission.permission_level == 'admin'
        
    return False