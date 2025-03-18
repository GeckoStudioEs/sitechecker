import socket
import requests
from typing import Any, List, Optional
from datetime import datetime
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Project, User
from app.utils.project_utils import check_project_permissions
from app.schemas.domain import (
    Domain as DomainSchema,
    DomainCreate,
    DomainUpdate,
    DomainDetail,
    DomainValidation
)
from app.utils.url_utils import is_valid_url, normalize_url, get_domain

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/domains", tags=["domains"])

@router.post("/validate", response_model=DomainValidation)
async def validate_domain(
    *,
    url: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Valida un dominio antes de añadirlo a un proyecto.
    """
    validation_errors = []
    is_valid = True
    status_code = None
    ip_address = None
    redirect_url = None
    
    # Verificar formato de URL
    if not is_valid_url(url):
        is_valid = False
        validation_errors.append("La URL no tiene un formato válido")
        return DomainValidation(
            url=url,
            is_valid=is_valid,
            validation_errors=validation_errors
        )
    
    # Normalizar URL
    normalized_url = normalize_url(url)
    
    # Extraer dominio
    domain = get_domain(normalized_url)
    
    try:
        # Intentar resolver IP
        ip_address = socket.gethostbyname(domain)
    except socket.gaierror:
        is_valid = False
        validation_errors.append("No se pudo resolver el dominio")
    
    # Intentar acceder a la URL
    try:
        response = requests.head(
            normalized_url, 
            timeout=10, 
            allow_redirects=True,
            headers={"User-Agent": settings.USER_AGENT}
        )
        status_code = response.status_code
        
        # Verificar si hubo redirección
        if response.url != normalized_url:
            redirect_url = response.url
        
        # Verificar código de respuesta
        if status_code >= 400:
            is_valid = False
            validation_errors.append(f"El servidor respondió con código {status_code}")
            
    except requests.RequestException as e:
        is_valid = False
        validation_errors.append(f"Error al conectar con el servidor: {str(e)}")
    
    return DomainValidation(
        url=normalized_url,
        is_valid=is_valid,
        validation_errors=validation_errors,
        status_code=status_code,
        ip_address=ip_address,
        redirect_url=redirect_url
    )

@router.post("/", response_model=DomainDetail)
async def create_domain(
    *,
    db: Session = Depends(get_db),
    domain_in: DomainCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Crea un nuevo dominio para un proyecto.
    """
    # Verificar si el proyecto existe
    project = db.query(Project).filter(Project.id == domain_in.project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Verificar si el usuario tiene permisos para añadir dominios al proyecto
    if not check_project_permissions(db, domain_in.project_id, current_user, "edit"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para añadir dominios a este proyecto"
        )
    
    # Validar el dominio
    validation_result = await validate_domain(url=domain_in.url, current_user=current_user)
    
    # Crear el dominio en la base de datos
    # Nota: Aquí deberíamos crear un modelo Domain, pero como no lo hemos definido en models.py,
    # solo simularemos la creación y devolveremos un objeto DomainDetail
    
    # En un caso real, crearíamos el modelo y lo guardaríamos en la base de datos
    # db_domain = Domain(
    #     url=validation_result.url,
    #     name=domain_in.name,
    #     description=domain_in.description,
    #     project_id=domain_in.project_id,
    #     is_active=domain_in.is_active,
    #     status="active" if validation_result.is_valid else "error"
    # )
    # 
    # db.add(db_domain)
    # db.commit()
    # db.refresh(db_domain)
    
    # Simulación de dominio creado
    domain_detail = DomainDetail(
        id=1,  # En un caso real, este sería el ID generado
        url=validation_result.url,
        name=domain_in.name or get_domain(validation_result.url),
        description=domain_in.description,
        project_id=domain_in.project_id,
        is_active=domain_in.is_active,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_checked=datetime.utcnow(),
        status="active" if validation_result.is_valid else "error",
        validation_result=validation_result,
        analytics_summary=None
    )
    
    return domain_detail

@router.get("/project/{project_id}", response_model=List[DomainSchema])
async def get_project_domains(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> Any:
    """
    Obtiene la lista de dominios de un proyecto.
    """
    # Verificar si el proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Verificar si el usuario tiene permisos para ver los dominios del proyecto
    if not check_project_permissions(db, project_id, current_user, "view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver los dominios de este proyecto"
        )
    
    # En un caso real, consultaríamos los dominios del proyecto en la base de datos
    # domains = db.query(Domain).filter(Domain.project_id == project_id)
    #
    # if is_active is not None:
    #     domains = domains.filter(Domain.is_active == is_active)
    #
    # domains = domains.offset(skip).limit(limit).all()
    
    # Simulación de dominios
    domains = [
        DomainSchema(
            id=1,
            url="https://example.com",
            name="Example",
            description="Dominio de ejemplo",
            project_id=project_id,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_checked=datetime.utcnow(),
            status="active"
        )
    ]
    
    return domains

@router.get("/{domain_id}", response_model=DomainDetail)
async def get_domain(
    *,
    db: Session = Depends(get_db),
    domain_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Obtiene un dominio por su ID.
    """
    # En un caso real, consultaríamos el dominio en la base de datos
    # domain = db.query(Domain).filter(Domain.id == domain_id).first()
    #
    # if not domain:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Dominio no encontrado"
    #     )
    #
    # # Verificar si el usuario tiene permisos para ver el dominio
    # if not check_project_permissions(db, domain.project_id, current_user, "view"):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="No tienes permisos para ver este dominio"
    #     )
    
    # Simulación de dominio
    domain_detail = DomainDetail(
        id=domain_id,
        url="https://example.com",
        name="Example",
        description="Dominio de ejemplo",
        project_id=1,  # En un caso real, este sería el ID del proyecto
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_checked=datetime.utcnow(),
        status="active",
        validation_result=DomainValidation(
            url="https://example.com",
            is_valid=True,
            status_code=200,
            ip_address="93.184.216.34",
            redirect_url=None
        ),
        analytics_summary=None
    )
    
    return domain_detail

@router.put("/{domain_id}", response_model=DomainDetail)
async def update_domain(
    *,
    db: Session = Depends(get_db),
    domain_id: int,
    domain_in: DomainUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Actualiza un dominio.
    """
    # En un caso real, consultaríamos el dominio en la base de datos
    # domain = db.query(Domain).filter(Domain.id == domain_id).first()
    #
    # if not domain:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Dominio no encontrado"
    #     )
    #
    # # Verificar si el usuario tiene permisos para editar el dominio
    # if not check_project_permissions(db, domain.project_id, current_user, "edit"):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="No tienes permisos para editar este dominio"
    #     )
    #
    # # Actualizar los campos del dominio
    # update_data = domain_in.dict(exclude_unset=True)
    #
    # for field, value in update_data.items():
    #     setattr(domain, field, value)
    #
    # db.commit()
    # db.refresh(domain)
    
    # Simulación de dominio actualizado
    domain_detail = DomainDetail(
        id=domain_id,
        url=domain_in.url or "https://example.com",
        name=domain_in.name or "Example Updated",
        description=domain_in.description or "Dominio de ejemplo actualizado",
        project_id=1,  # En un caso real, este sería el ID del proyecto
        is_active=domain_in.is_active if domain_in.is_active is not None else True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_checked=datetime.utcnow(),
        status="active",
        validation_result=DomainValidation(
            url="https://example.com",
            is_valid=True,
            status_code=200,
            ip_address="93.184.216.34",
            redirect_url=None
        ),
        analytics_summary=None
    )
    
    return domain_detail

@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_domain(
    *,
    db: Session = Depends(get_db),
    domain_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Elimina un dominio.
    """
    # En un caso real, consultaríamos el dominio en la base de datos
    # domain = db.query(Domain).filter(Domain.id == domain_id).first()
    #
    # if not domain:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Dominio no encontrado"
    #     )
    #
    # # Verificar si el usuario tiene permisos para eliminar el dominio
    # if not check_project_permissions(db, domain.project_id, current_user, "edit"):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="No tienes permisos para eliminar este dominio"
    #     )
    #
    # # Eliminar el dominio
    # db.delete(domain)
    # db.commit()