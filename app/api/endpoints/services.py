from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_active_superuser
from app.db.models import User
from app.services.services.service_service import ServiceService
from app.schemas.services import (
    ServiceCategoryCreate, ServiceCategoryUpdate, ServiceCategoryInDB, ServiceCategoryWithServices,
    ServiceCreate, ServiceUpdate, ServiceInDB, ServiceWithCategory,
    ServiceRequestCreate, ServiceRequestUpdate, ServiceRequestInDB, ServiceRequestWithDetails,
    ServiceCategorySummary, ServiceSummary
)

router = APIRouter()

# ========== Rutas para Administración de Categorías ==========

@router.post("/categories", response_model=ServiceCategoryInDB, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: ServiceCategoryCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Crea una nueva categoría de servicios (requiere permisos de administrador)
    """
    service = ServiceService(db)
    return service.create_category(category)

@router.get("/categories", response_model=List[ServiceCategorySummary])
async def read_categories(
    skip: int = 0, 
    limit: int = 100,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todas las categorías de servicios
    """
    service = ServiceService(db)
    # Usar include_inactive solo si es administrador
    if not current_user.role == "admin":
        include_inactive = False
    
    categories = service.get_categories(skip, limit, include_inactive)
    # Convertir a resumen con conteo de servicios
    return service.get_categories_summary()

@router.get("/categories/{category_id}", response_model=ServiceCategoryWithServices)
async def read_category(
    category_id: int = Path(..., description="ID de la categoría"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene una categoría por su ID, incluyendo sus servicios
    """
    service = ServiceService(db)
    category = service.get_category(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría no encontrada: {category_id}"
        )
    
    # Para usuarios no administradores, filtrar servicios inactivos
    if current_user.role == "admin":
        return category
    else:
        category.services = [s for s in category.services if s.is_active]
        return category

@router.get("/categories/slug/{slug}", response_model=ServiceCategoryWithServices)
async def read_category_by_slug(
    slug: str = Path(..., description="Slug de la categoría"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene una categoría por su slug, incluyendo sus servicios
    """
    service = ServiceService(db)
    category = service.get_category_by_slug(slug)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría no encontrada: {slug}"
        )
    
    # Para usuarios no administradores, filtrar servicios inactivos
    if current_user.role == "admin":
        return category
    else:
        category.services = [s for s in category.services if s.is_active]
        return category

@router.put("/categories/{category_id}", response_model=ServiceCategoryInDB)
async def update_category(
    category_id: int,
    category: ServiceCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Actualiza una categoría existente (requiere permisos de administrador)
    """
    service = ServiceService(db)
    updated_category = service.update_category(category_id, category)
    if not updated_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría no encontrada: {category_id}"
        )
    return updated_category

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Elimina una categoría (requiere permisos de administrador)
    """
    service = ServiceService(db)
    result = service.delete_category(category_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría no encontrada: {category_id}"
        )
    return None

# ========== Rutas para Administración de Servicios ==========

@router.post("/services", response_model=ServiceInDB, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: ServiceCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Crea un nuevo servicio (requiere permisos de administrador)
    """
    service = ServiceService(db)
    return service.create_service(service_data)

@router.get("/services", response_model=List[ServiceSummary])
async def read_services(
    skip: int = 0, 
    limit: int = 100,
    category_id: Optional[int] = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todos los servicios, opcionalmente filtrados por categoría
    """
    service = ServiceService(db)
    # Usar include_inactive solo si es administrador
    if not current_user.role == "admin":
        include_inactive = False
    
    services = service.get_services(skip, limit, category_id, include_inactive)
    
    # Convertir a resumen con nombre de categoría
    result = []
    for svc in services:
        result.append(ServiceSummary(
            id=svc.id,
            name=svc.name,
            slug=svc.slug,
            description=svc.description,
            benefits=svc.benefits,
            price=svc.price,
            category_id=svc.category_id,
            category_name=svc.category.name if svc.category else ""
        ))
    
    return result

@router.get("/services/{service_id}", response_model=ServiceWithCategory)
async def read_service(
    service_id: int = Path(..., description="ID del servicio"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un servicio por su ID, incluyendo su categoría
    """
    service = ServiceService(db)
    service_obj = service.get_service(service_id)
    if not service_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio no encontrado: {service_id}"
        )
    
    # Verificar si es activo para usuarios no administradores
    if not current_user.role == "admin" and not service_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio no encontrado: {service_id}"
        )
    
    return service_obj

@router.get("/services/slug/{slug}", response_model=ServiceWithCategory)
async def read_service_by_slug(
    slug: str = Path(..., description="Slug del servicio"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un servicio por su slug, incluyendo su categoría
    """
    service = ServiceService(db)
    service_obj = service.get_service_by_slug(slug)
    if not service_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio no encontrado: {slug}"
        )
    
    # Verificar si es activo para usuarios no administradores
    if not current_user.role == "admin" and not service_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio no encontrado: {slug}"
        )
    
    return service_obj

@router.put("/services/{service_id}", response_model=ServiceInDB)
async def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Actualiza un servicio existente (requiere permisos de administrador)
    """
    service = ServiceService(db)
    updated_service = service.update_service(service_id, service_data)
    if not updated_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio no encontrado: {service_id}"
        )
    return updated_service

@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Elimina un servicio (requiere permisos de administrador)
    """
    service = ServiceService(db)
    result = service.delete_service(service_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio no encontrado: {service_id}"
        )
    return None

# ========== Rutas para Solicitudes de Servicio ==========

@router.post("/requests", response_model=ServiceRequestInDB, status_code=status.HTTP_201_CREATED)
async def create_service_request(
    request_data: ServiceRequestCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea una nueva solicitud de servicio
    """
    service = ServiceService(db)
    return service.create_service_request(request_data, current_user.id)

@router.get("/requests", response_model=List[ServiceRequestWithDetails])
async def read_service_requests(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todas las solicitudes de servicio del usuario actual
    (los administradores pueden ver todas las solicitudes)
    """
    service = ServiceService(db)
    
    # Si es administrador, puede ver todas las solicitudes
    if current_user.role == "admin":
        service_requests = service.get_service_requests(skip, limit, None, None, status)
    else:
        # Si no es administrador, solo puede ver sus propias solicitudes
        service_requests = service.get_service_requests(skip, limit, current_user.id, None, status)
    
    # Enriquecer con información adicional
    result = []
    for req in service_requests:
        # Obtener detalles adicionales
        req_detail = ServiceRequestWithDetails(
            **{k: getattr(req, k) for k in req.__dict__ if not k.startswith('_')},
            service=req.service,
            project_name=req.project.name if req.project else None,
            user_email=req.user.email if req.user else ""
        )
        result.append(req_detail)
    
    return result

@router.get("/requests/{request_id}", response_model=ServiceRequestWithDetails)
async def read_service_request(
    request_id: int = Path(..., description="ID de la solicitud"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene una solicitud de servicio por su ID
    """
    service = ServiceService(db)
    service_request = service.get_service_request(request_id)
    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solicitud no encontrada: {request_id}"
        )
    
    # Verificar que sea el propietario o un administrador
    if service_request.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para ver esta solicitud"
        )
    
    # Agregar detalles adicionales
    return ServiceRequestWithDetails(
        **{k: getattr(service_request, k) for k in service_request.__dict__ if not k.startswith('_')},
        service=service_request.service,
        project_name=service_request.project.name if service_request.project else None,
        user_email=service_request.user.email if service_request.user else ""
    )

@router.put("/requests/{request_id}", response_model=ServiceRequestInDB)
async def update_service_request(
    request_id: int,
    request_data: ServiceRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza una solicitud de servicio existente (solo administradores pueden actualizar ciertos campos)
    """
    service = ServiceService(db)
    
    # Verificar que exista la solicitud
    existing_request = service.get_service_request(request_id)
    if not existing_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solicitud no encontrada: {request_id}"
        )
    
    # Verificar permisos
    is_admin = current_user.role == "admin"
    is_owner = existing_request.user_id == current_user.id
    
    if not (is_admin or is_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para actualizar esta solicitud"
        )
    
    # Si no es administrador, limitar campos que puede actualizar
    if not is_admin:
        # Los usuarios normales solo pueden actualizar el mensaje y campos personalizados
        update_data = ServiceRequestUpdate(
            message=request_data.message,
            custom_fields=request_data.custom_fields
        )
    else:
        update_data = request_data
    
    updated_request = service.update_service_request(request_id, update_data)
    return updated_request

@router.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Elimina una solicitud de servicio (requiere permisos de administrador)
    """
    service = ServiceService(db)
    result = service.delete_service_request(request_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solicitud no encontrada: {request_id}"
        )
    return None

# ========== Rutas Públicas y Resúmenes ==========

@router.get("/featured", response_model=List[ServiceSummary])
async def read_featured_services(
    limit: int = Query(6, ge=1, le=12, description="Número máximo de servicios a devolver"),
    db: Session = Depends(get_db)
):
    """
    Obtiene los servicios destacados (endpoint público)
    """
    service = ServiceService(db)
    featured_services = service.get_featured_services(limit)
    
    # Convertir a resumen con nombre de categoría
    result = []
    for svc in featured_services:
        result.append(ServiceSummary(
            id=svc.id,
            name=svc.name,
            slug=svc.slug,
            description=svc.description,
            benefits=svc.benefits,
            price=svc.price,
            category_id=svc.category_id,
            category_name=svc.category.name if svc.category else ""
        ))
    
    return result

@router.get("/categories/{category_slug}/services", response_model=List[ServiceSummary])
async def read_services_by_category_slug(
    category_slug: str = Path(..., description="Slug de la categoría"),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los servicios de una categoría específica por su slug (endpoint público)
    """
    service = ServiceService(db)
    services = service.get_services_by_category_slug(category_slug)
    
    # Convertir a resumen con nombre de categoría
    result = []
    for svc in services:
        result.append(ServiceSummary(
            id=svc.id,
            name=svc.name,
            slug=svc.slug,
            description=svc.description,
            benefits=svc.benefits,
            price=svc.price,
            category_id=svc.category_id,
            category_name=svc.category.name if svc.category else ""
        ))
    
    return result