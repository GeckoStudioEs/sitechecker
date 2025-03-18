from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.db.service_models import ServiceCategory, Service, ServiceRequest
from app.db.models import User, Project
from app.schemas.services import (
    ServiceCategoryCreate, ServiceCategoryUpdate, 
    ServiceCreate, ServiceUpdate, 
    ServiceRequestCreate, ServiceRequestUpdate,
    ServiceCategorySummary, ServiceSummary
)

class ServiceService:
    """Servicio para gestionar categorías y servicios SEO"""
    
    def __init__(self, db: Session):
        """
        Inicializa el servicio con la sesión de base de datos
        
        Args:
            db: Sesión de SQLAlchemy
        """
        self.db = db
    
    # ========== Métodos para Categorías de Servicios ==========
    
    def create_category(self, data: ServiceCategoryCreate) -> ServiceCategory:
        """
        Crea una nueva categoría de servicios
        
        Args:
            data: Datos de la categoría a crear
        
        Returns:
            La categoría creada
        """
        # Comprobar si ya existe una categoría con el mismo slug
        existing = self.db.query(ServiceCategory).filter(ServiceCategory.slug == data.slug).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una categoría con el slug '{data.slug}'"
            )
        
        # Crear nueva categoría
        category = ServiceCategory(**data.model_dump())
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def get_categories(self, skip: int = 0, limit: int = 100, include_inactive: bool = False) -> List[ServiceCategory]:
        """
        Obtiene todas las categorías de servicios
        
        Args:
            skip: Número de categorías a saltar (para paginación)
            limit: Número máximo de categorías a devolver
            include_inactive: Si es True, incluye categorías inactivas
        
        Returns:
            Lista de categorías
        """
        query = self.db.query(ServiceCategory)
        
        if not include_inactive:
            query = query.filter(ServiceCategory.is_active == True)
        
        return query.order_by(ServiceCategory.order).offset(skip).limit(limit).all()
    
    def get_category(self, category_id: int) -> Optional[ServiceCategory]:
        """
        Obtiene una categoría por su ID
        
        Args:
            category_id: ID de la categoría
        
        Returns:
            La categoría encontrada o None
        """
        return self.db.query(ServiceCategory).filter(ServiceCategory.id == category_id).first()
    
    def get_category_by_slug(self, slug: str) -> Optional[ServiceCategory]:
        """
        Obtiene una categoría por su slug
        
        Args:
            slug: Slug de la categoría
        
        Returns:
            La categoría encontrada o None
        """
        return self.db.query(ServiceCategory).filter(ServiceCategory.slug == slug).first()
    
    def update_category(self, category_id: int, data: ServiceCategoryUpdate) -> Optional[ServiceCategory]:
        """
        Actualiza una categoría existente
        
        Args:
            category_id: ID de la categoría a actualizar
            data: Datos actualizados
        
        Returns:
            La categoría actualizada o None si no existe
        """
        category = self.get_category(category_id)
        if not category:
            return None
        
        # Si se está actualizando el slug, comprobar que no exista ya
        if data.slug and data.slug != category.slug:
            existing = self.db.query(ServiceCategory).filter(ServiceCategory.slug == data.slug).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe una categoría con el slug '{data.slug}'"
                )
        
        # Actualizar solo los campos proporcionados
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(category, key, value)
        
        category.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def delete_category(self, category_id: int) -> bool:
        """
        Elimina una categoría por su ID
        
        Args:
            category_id: ID de la categoría a eliminar
        
        Returns:
            True si se eliminó correctamente, False si no existe
        """
        category = self.get_category(category_id)
        if not category:
            return False
        
        self.db.delete(category)
        self.db.commit()
        
        return True
    
    # ========== Métodos para Servicios ==========
    
    def create_service(self, data: ServiceCreate) -> Service:
        """
        Crea un nuevo servicio
        
        Args:
            data: Datos del servicio a crear
        
        Returns:
            El servicio creado
        """
        # Comprobar si existe la categoría
        category = self.get_category(data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No existe la categoría con ID {data.category_id}"
            )
        
        # Comprobar si ya existe un servicio con el mismo slug
        existing = self.db.query(Service).filter(Service.slug == data.slug).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un servicio con el slug '{data.slug}'"
            )
        
        # Crear nuevo servicio
        service = Service(**data.model_dump())
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        
        return service
    
    def get_services(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        category_id: Optional[int] = None,
        include_inactive: bool = False
    ) -> List[Service]:
        """
        Obtiene todos los servicios, opcionalmente filtrados por categoría
        
        Args:
            skip: Número de servicios a saltar (para paginación)
            limit: Número máximo de servicios a devolver
            category_id: ID de la categoría para filtrar (opcional)
            include_inactive: Si es True, incluye servicios inactivos
        
        Returns:
            Lista de servicios
        """
        query = self.db.query(Service)
        
        if category_id:
            query = query.filter(Service.category_id == category_id)
        
        if not include_inactive:
            query = query.filter(Service.is_active == True)
        
        return query.order_by(Service.category_id, Service.order).offset(skip).limit(limit).all()
    
    def get_service(self, service_id: int) -> Optional[Service]:
        """
        Obtiene un servicio por su ID
        
        Args:
            service_id: ID del servicio
        
        Returns:
            El servicio encontrado o None
        """
        return self.db.query(Service).filter(Service.id == service_id).first()
    
    def get_service_by_slug(self, slug: str) -> Optional[Service]:
        """
        Obtiene un servicio por su slug
        
        Args:
            slug: Slug del servicio
        
        Returns:
            El servicio encontrado o None
        """
        return self.db.query(Service).filter(Service.slug == slug).first()
    
    def update_service(self, service_id: int, data: ServiceUpdate) -> Optional[Service]:
        """
        Actualiza un servicio existente
        
        Args:
            service_id: ID del servicio a actualizar
            data: Datos actualizados
        
        Returns:
            El servicio actualizado o None si no existe
        """
        service = self.get_service(service_id)
        if not service:
            return None
        
        # Si se está actualizando la categoría, comprobar que exista
        if data.category_id and data.category_id != service.category_id:
            category = self.get_category(data.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No existe la categoría con ID {data.category_id}"
                )
        
        # Si se está actualizando el slug, comprobar que no exista ya
        if data.slug and data.slug != service.slug:
            existing = self.db.query(Service).filter(Service.slug == data.slug).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un servicio con el slug '{data.slug}'"
                )
        
        # Actualizar solo los campos proporcionados
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(service, key, value)
        
        service.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(service)
        
        return service
    
    def delete_service(self, service_id: int) -> bool:
        """
        Elimina un servicio por su ID
        
        Args:
            service_id: ID del servicio a eliminar
        
        Returns:
            True si se eliminó correctamente, False si no existe
        """
        service = self.get_service(service_id)
        if not service:
            return False
        
        self.db.delete(service)
        self.db.commit()
        
        return True
    
    # ========== Métodos para Solicitudes de Servicio ==========
    
    def create_service_request(self, data: ServiceRequestCreate, user_id: int) -> ServiceRequest:
        """
        Crea una nueva solicitud de servicio
        
        Args:
            data: Datos de la solicitud
            user_id: ID del usuario que realiza la solicitud
        
        Returns:
            La solicitud creada
        """
        # Comprobar si existe el servicio
        service = self.get_service(data.service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No existe el servicio con ID {data.service_id}"
            )
        
        # Comprobar si existe el proyecto (si se proporciona)
        if data.project_id:
            project = self.db.query(Project).filter(Project.id == data.project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No existe el proyecto con ID {data.project_id}"
                )
        
        # Crear nueva solicitud
        request_data = data.model_dump()
        request_data["user_id"] = user_id
        
        service_request = ServiceRequest(**request_data)
        self.db.add(service_request)
        self.db.commit()
        self.db.refresh(service_request)
        
        return service_request
    
    def get_service_requests(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        user_id: Optional[int] = None,
        service_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[ServiceRequest]:
        """
        Obtiene todas las solicitudes de servicio, opcionalmente filtradas
        
        Args:
            skip: Número de solicitudes a saltar (para paginación)
            limit: Número máximo de solicitudes a devolver
            user_id: ID del usuario para filtrar (opcional)
            service_id: ID del servicio para filtrar (opcional)
            status: Estado de la solicitud para filtrar (opcional)
        
        Returns:
            Lista de solicitudes
        """
        query = self.db.query(ServiceRequest)
        
        if user_id:
            query = query.filter(ServiceRequest.user_id == user_id)
        
        if service_id:
            query = query.filter(ServiceRequest.service_id == service_id)
        
        if status:
            query = query.filter(ServiceRequest.status == status)
        
        return query.order_by(ServiceRequest.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_service_request(self, request_id: int) -> Optional[ServiceRequest]:
        """
        Obtiene una solicitud de servicio por su ID
        
        Args:
            request_id: ID de la solicitud
        
        Returns:
            La solicitud encontrada o None
        """
        return self.db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    
    def update_service_request(self, request_id: int, data: ServiceRequestUpdate) -> Optional[ServiceRequest]:
        """
        Actualiza una solicitud de servicio existente
        
        Args:
            request_id: ID de la solicitud a actualizar
            data: Datos actualizados
        
        Returns:
            La solicitud actualizada o None si no existe
        """
        service_request = self.get_service_request(request_id)
        if not service_request:
            return None
        
        # Actualizar solo los campos proporcionados
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(service_request, key, value)
        
        service_request.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(service_request)
        
        return service_request
    
    def delete_service_request(self, request_id: int) -> bool:
        """
        Elimina una solicitud de servicio por su ID
        
        Args:
            request_id: ID de la solicitud a eliminar
        
        Returns:
            True si se eliminó correctamente, False si no existe
        """
        service_request = self.get_service_request(request_id)
        if not service_request:
            return False
        
        self.db.delete(service_request)
        self.db.commit()
        
        return True
    
    # ========== Métodos de Resumen y Estadísticas ==========
    
    def get_categories_summary(self) -> List[Dict[str, Any]]:
        """
        Obtiene un resumen de las categorías con el número de servicios en cada una
        
        Returns:
            Lista de categorías con conteo de servicios
        """
        # Consulta para obtener el conteo de servicios por categoría
        categories_with_count = self.db.query(
            ServiceCategory,
            func.count(Service.id).label('services_count')
        ).outerjoin(
            Service, ServiceCategory.id == Service.category_id
        ).filter(
            ServiceCategory.is_active == True
        ).group_by(
            ServiceCategory.id
        ).order_by(
            ServiceCategory.order
        ).all()
        
        result = []
        for category, count in categories_with_count:
            result.append({
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "description": category.description,
                "icon": category.icon,
                "services_count": count
            })
        
        return result
    
    def get_featured_services(self, limit: int = 6) -> List[Service]:
        """
        Obtiene los servicios destacados
        
        Args:
            limit: Número máximo de servicios a devolver
        
        Returns:
            Lista de servicios destacados
        """
        return self.db.query(Service).filter(
            Service.is_active == True,
            Service.is_featured == True
        ).order_by(Service.order).limit(limit).all()
    
    def get_services_by_category_slug(self, category_slug: str) -> List[Service]:
        """
        Obtiene todos los servicios de una categoría específica por su slug
        
        Args:
            category_slug: Slug de la categoría
        
        Returns:
            Lista de servicios en la categoría
        """
        category = self.get_category_by_slug(category_slug)
        if not category:
            return []
        
        return self.db.query(Service).filter(
            Service.category_id == category.id,
            Service.is_active == True
        ).order_by(Service.order).all()