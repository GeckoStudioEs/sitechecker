from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, validator

# Eliminamos la importación circular
# from app.schemas.keywords import KeywordSettings, KeywordAddRequest

# Importamos solo los modelos necesarios
from app.db.models import Keyword, KeywordPosition, Project, KeywordGroup

# Esquema base para palabras clave
class KeywordBase(BaseModel):
    keyword: str
    country: Optional[str] = None
    language: Optional[str] = None
    search_engine: str = "google"
    device: str = "desktop"
    target_url: Optional[str] = None
    group_id: Optional[int] = None

# Esquema para crear palabras clave
class KeywordCreate(KeywordBase):
    pass

# Esquema para actualizar palabras clave
class KeywordUpdate(BaseModel):
    country: Optional[str] = None
    language: Optional[str] = None
    search_engine: Optional[str] = None
    device: Optional[str] = None
    target_url: Optional[str] = None
    group_id: Optional[int] = None

# Esquema para crear posiciones de palabras clave
class KeywordPositionCreate(BaseModel):
    keyword_id: int
    check_date: datetime
    position: Optional[int] = None
    previous_position: Optional[int] = None
    url: Optional[str] = None
    serp_features: Optional[Dict[str, Any]] = None

# Esquema para detalles de palabra clave
class KeywordDetail(KeywordBase):
    id: int
    project_id: int
    volume: Optional[int] = None
    cpc: Optional[float] = None
    competition: Optional[float] = None
    created_at: datetime
    created_by: Optional[int] = None

    class Config:
        orm_mode = True

# Esquema para posición de palabra clave
class KeywordPositionDetail(BaseModel):
    id: int
    keyword_id: int
    check_date: datetime
    position: Optional[int] = None
    previous_position: Optional[int] = None
    url: Optional[str] = None
    serp_features: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        orm_mode = True

# Esquema para detalles de palabra clave con historial de posiciones
class KeywordWithPositions(KeywordDetail):
    positions: List[KeywordPositionDetail] = []

    class Config:
        orm_mode = True

# Esquema para configuración de seguimiento de palabras clave
class KeywordSettings(BaseModel):
    country: str = "us"
    language: str = "en"
    search_engine: str = "google"
    device: str = "desktop"
    location: Optional[str] = None

# Esquema para solicitud de añadir palabras clave
class KeywordAddRequest(BaseModel):
    keywords: List[str]
    settings: KeywordSettings
    target_url: Optional[str] = None
    check_positions: bool = False

# Esquema para respuesta de añadir palabras clave
class KeywordResponse(BaseModel):
    added: int
    skipped: int

# Esquema para grupo de palabras clave
class KeywordGroupBase(BaseModel):
    name: str
    description: Optional[str] = None

# Esquema para crear grupo de palabras clave
class KeywordGroupCreate(KeywordGroupBase):
    keyword_ids: List[int]

# Esquema para detalles de grupo de palabras clave
class KeywordGroupDetail(KeywordGroupBase):
    id: int
    project_id: int
    created_at: datetime
    created_by: Optional[int] = None
    keyword_count: int

    class Config:
        orm_mode = True

# Esquema para respuesta de grupo de palabras clave
class KeywordGroupResponse(BaseModel):
    id: int
    name: str
    keyword_count: int

# Esquema para sugerencia de palabra clave
class KeywordSuggestion(BaseModel):
    keyword: str
    volume: Optional[int] = None
    cpc: Optional[float] = None
    competition: Optional[float] = None
    difficulty: Optional[int] = None