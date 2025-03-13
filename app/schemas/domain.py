from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, validator, HttpUrl

class DomainBase(BaseModel):
    """Esquema base para un dominio."""
    url: str
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True

class DomainCreate(DomainBase):
    """Esquema para crear un dominio."""
    project_id: int

class DomainUpdate(BaseModel):
    """Esquema para actualizar un dominio."""
    url: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class DomainValidation(BaseModel):
    """Esquema para validar un dominio."""
    url: str
    is_valid: bool
    validation_errors: Optional[List[str]] = None
    status_code: Optional[int] = None
    ip_address: Optional[str] = None
    redirect_url: Optional[str] = None

class DomainInDBBase(DomainBase):
    """Esquema base para el dominio en base de datos."""
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    last_checked: Optional[datetime] = None
    status: Optional[str] = None
    
    class Config:
        orm_mode = True

class Domain(DomainInDBBase):
    """Esquema para devolver un dominio."""
    pass

class DomainDetail(Domain):
    """Esquema para devolver un dominio con detalles adicionales."""
    validation_result: Optional[DomainValidation] = None
    analytics_summary: Optional[Dict[str, Any]] = None