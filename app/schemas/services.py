from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

# Base Models
class ServiceCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    slug: str
    icon: Optional[str] = None
    is_active: bool = True
    order: int = 0

class ServiceBase(BaseModel):
    category_id: int
    name: str
    slug: str
    description: Optional[str] = None
    detailed_description: Optional[str] = None
    benefits: List[str] = []
    price: Optional[float] = None
    price_type: str = "fixed"
    duration: Optional[str] = None
    is_active: bool = True
    is_featured: bool = False
    order: int = 0
    custom_fields: Optional[Dict[str, Any]] = None

class ServiceRequestBase(BaseModel):
    service_id: int
    project_id: Optional[int] = None
    message: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

# Create Models
class ServiceCategoryCreate(ServiceCategoryBase):
    pass

class ServiceCreate(ServiceBase):
    pass

class ServiceRequestCreate(ServiceRequestBase):
    pass

# Update Models
class ServiceCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None
    order: Optional[int] = None

class ServiceUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    detailed_description: Optional[str] = None
    benefits: Optional[List[str]] = None
    price: Optional[float] = None
    price_type: Optional[str] = None
    duration: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    order: Optional[int] = None
    custom_fields: Optional[Dict[str, Any]] = None

class ServiceRequestUpdate(BaseModel):
    status: Optional[str] = None
    message: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    admin_notes: Optional[str] = None

# Response Models
class ServiceCategoryInDB(ServiceCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ServiceInDB(ServiceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ServiceRequestInDB(ServiceRequestBase):
    id: int
    user_id: int
    status: str
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Response Models with Relationships
class ServiceWithCategory(ServiceInDB):
    category: ServiceCategoryInDB

class ServiceCategoryWithServices(ServiceCategoryInDB):
    services: List[ServiceInDB] = []

class ServiceRequestWithDetails(ServiceRequestInDB):
    service: ServiceInDB
    project_name: Optional[str] = None
    user_email: str

# Summary Models
class ServiceSummary(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    benefits: List[str] = []
    price: Optional[float] = None
    category_id: int
    category_name: str

    class Config:
        from_attributes = True

class ServiceCategorySummary(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    services_count: int = 0

    class Config:
        from_attributes = True