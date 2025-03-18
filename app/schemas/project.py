from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, validator

# Esquemas base
class ProjectBase(BaseModel):
    name: str
    domain: str
    protocol: str = "https"
    domain_scope: str = "domain"  # domain, subdomain, path
    tags: Optional[List[str]] = None

class ProjectPermissionBase(BaseModel):
    user_id: int
    permission_level: str

# Esquemas para crear y actualizar
class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    protocol: Optional[str] = None
    domain_scope: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None

class ProjectPermissionCreate(ProjectPermissionBase):
    pass

class ProjectPermissionUpdate(BaseModel):
    permission_level: str

# Esquemas para respuestas
class ProjectPermissionResponse(ProjectPermissionBase):
    id: int
    project_id: int
    created_at: datetime
    created_by: Optional[int] = None

    class Config:
        orm_mode = True

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    owner_id: Optional[int] = None
    is_active: bool
    credits_balance: int

    class Config:
        orm_mode = True

class ProjectWithPermissionsResponse(ProjectResponse):
    permissions: List[ProjectPermissionResponse] = []

class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    page: int
    pages: int

class ProjectUserInfo(BaseModel):
    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    permission_level: str

class ProjectUsersResponse(BaseModel):
    owner: Optional[ProjectUserInfo] = None
    users: List[ProjectUserInfo] = []