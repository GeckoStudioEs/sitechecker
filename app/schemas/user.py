from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        """Valida que la contraseña tenga al menos 8 caracteres y contenga al menos una letra y un número."""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isalpha() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('password')
    def password_strength(cls, v):
        """Valida que la contraseña tenga al menos 8 caracteres y contenga al menos una letra y un número."""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isalpha() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

class UserInDBBase(UserBase):
    id: int
    role: str
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class User(UserInDBBase):
    """Esquema para devolver un usuario."""
    pass

class UserInDB(UserInDBBase):
    """Esquema para el usuario en base de datos."""
    password_hash: str

class Token(BaseModel):
    """Esquema para el token de acceso."""
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    """Esquema para el payload del token."""
    sub: Optional[int] = None