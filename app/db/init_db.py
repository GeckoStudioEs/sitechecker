import os
import logging
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import Base, engine
from app.db.models import User, Project
from app.db.service_models import ServiceCategory, Service, ServiceRequest
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    """Inicializa la base de datos creando tablas y usuario administrador"""
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear usuario admin si no existe
    admin_email = os.getenv("FIRST_ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("FIRST_ADMIN_PASSWORD", "admin123")
    
    admin = db.query(User).filter(User.email == admin_email).first()
    if not admin:
        # Crear usuario administrador
        admin_create = UserCreate(
            email=admin_email,
            password=admin_password,
            first_name="Admin",
            last_name="User",
            role="admin"
        )
        
        admin = User(
            email=admin_create.email,
            password_hash=get_password_hash(admin_create.password),
            first_name=admin_create.first_name,
            last_name=admin_create.last_name,
            role=admin_create.role
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        logger.info(f"Usuario administrador creado: {admin_email}")
    else:
        logger.info(f"Usuario administrador ya existe: {admin_email}")