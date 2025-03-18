from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status, BackgroundTasks
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
from app.services.events.service_events import ServiceEventHandler

class ServiceService:
    """Servicio para gestionar categorías y servicios SEO"""
    
    def __init__(self, db: Session, background_tasks: Optional[BackgroundTasks] = None):
        """
        Inicializa el servicio con la sesión de base de datos
        
        Args:
            db: Sesión de SQLAlchemy
            background_tasks: Gestor de tareas en segundo plano (opcional)
        """
        self.db = db
        self.background_tasks = background_tasks
        self.event_handler = ServiceEventHandler(db, background_tasks) if background_tasks else None
    
    # [...] Mantener el resto de métodos intactos [...]
    
    # Actualizar el método create_service_request
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
        
        # Emitir evento de creación si está disponible el manejador de eventos
        if self.event_handler:
            self.event_handler.emit_service_request_created(
                service_request.id, 
                service_request.service_id, 
                service_request.user_id
            )
        
        return service_request
    
    # Actualizar el método update_service_request
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
        
        # Guardar estado anterior para verificar cambios
        old_status = service_request.status
        
        # Actualizar solo los campos proporcionados
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(service_request, key, value)
        
        service_request.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(service_request)
        
        # Comprobar si cambió el estado y emitir evento correspondiente
        if self.event_handler and old_status != service_request.status:
            self.event_handler.emit_service_request_status_changed(
                service_request.id,
                service_request.service_id,
                service_request.user_id,
                old_status,
                service_request.status
            )
        
        return service_request
    
    # [...] Mantener el resto de métodos intactos [...]
class ServiceEventHandler:
    """Manejador de eventos relacionados con servicios"""
    
    def __init__(self, db: Session, background_tasks: BackgroundTasks):
        """
        Inicializa el manejador de eventos
        
        Args:
            db: Sesión de base de datos
            background_tasks: Gestor de tareas en segundo plano de FastAPI
        """
        self.db = db
        self.background_tasks = background_tasks
        self.listeners = {}
    
    def register_listener(self, event_type: str, callback: Callable) -> None:
        """
        Registra un nuevo listener para un tipo de evento
        
        Args:
            event_type: Tipo de evento (usar constantes de SERVICE_EVENTS)
            callback: Función a llamar cuando ocurra el evento
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        
        self.listeners[event_type].append(callback)
    
    def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Emite un evento, notificando a todos los listeners registrados
        
        Args:
            event_type: Tipo de evento
            data: Datos del evento
        """
        if event_type not in self.listeners:
            return
        
        for callback in self.listeners[event_type]:
            # Ejecutar callbacks en segundo plano
            self.background_tasks.add_task(callback, data)
    
    def emit_service_request_created(self, request_id: int, service_id: int, user_id: int) -> None:
        """
        Emite un evento cuando se crea una nueva solicitud de servicio
        
        Args:
            request_id: ID de la solicitud creada
            service_id: ID del servicio solicitado
            user_id: ID del usuario que creó la solicitud
        """
        self.emit(SERVICE_EVENTS["SERVICE_REQUEST_CREATED"], {
            "request_id": request_id,
            "service_id": service_id,
            "user_id": user_id,
            "status": "pending"
        })
    
    def emit_service_request_status_changed(
        self, 
        request_id: int, 
        service_id: int, 
        user_id: int, 
        old_status: str, 
        new_status: str
    ) -> None:
        """
        Emite un evento cuando cambia el estado de una solicitud
        
        Args:
            request_id: ID de la solicitud
            service_id: ID del servicio
            user_id: ID del usuario propietario
            old_status: Estado anterior
            new_status: Nuevo estado
        """
        self.emit(SERVICE_EVENTS["SERVICE_REQUEST_STATUS_CHANGED"], {
            "request_id": request_id,
            "service_id": service_id,
            "user_id": user_id,
            "old_status": old_status,
            "new_status": new_status
        })    