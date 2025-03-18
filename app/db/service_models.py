from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, JSON, Float
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base

class ServiceCategory(Base):
    """Categoría de servicios disponibles"""
    __tablename__ = "service_category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    slug = Column(String(100), unique=True, nullable=False)
    icon = Column(String(100))
    is_active = Column(Boolean, default=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    services = relationship("Service", back_populates="category")

class Service(Base):
    """Servicio individual disponible para contratación"""
    __tablename__ = "service"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("service_category.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    detailed_description = Column(Text)
    benefits = Column(ARRAY(String), default=[])
    price = Column(Float)
    price_type = Column(String(20), default="fixed")  # fixed, hourly, monthly
    duration = Column(String(50))  # Estimación de duración
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    custom_fields = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    category = relationship("ServiceCategory", back_populates="services")
    requests = relationship("ServiceRequest", back_populates="service")

class ServiceRequest(Base):
    """Solicitud de servicio por parte de un usuario"""
    __tablename__ = "service_request"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("service.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=True)
    status = Column(String(20), default="pending")  # pending, approved, in_progress, completed, cancelled
    message = Column(Text)
    custom_fields = Column(JSON)  # Campos personalizados según el servicio
    admin_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    service = relationship("Service", back_populates="requests")
    user = relationship("User")
    project = relationship("Project")