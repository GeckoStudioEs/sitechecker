# app/schemas/monitoring.py
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class MonitoringSettings(BaseModel):
    """Configuración para el monitoreo de sitios"""
    is_active: bool = True
    frequency: str = "3d"  # 12h, daily, 3d, weekly, monthly
    via_webhook: bool = False
    webhook_url: Optional[str] = None

class MonitoringResponse(BaseModel):
    """Respuesta para un monitoreo iniciado"""
    monitoring_id: int
    status: str

class MonitoringChange(BaseModel):
    """Cambio detectado en el monitoreo"""
    url: str
    type: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    change_percentage: Optional[float] = None

class StatusChange(BaseModel):
    """Cambio de estado en una URL"""
    url: str
    old_status: int
    new_status: int
    error: Optional[str] = None

class MonitoringResult(BaseModel):
    """Resultado de un monitoreo"""
    id: int
    check_time: datetime
    status: str
    total_pages: int
    changed_pages: int
    new_pages: int = 0
    deleted_pages: int = 0
    content_changes: List[MonitoringChange] = Field(default_factory=list)
    status_changes: List[StatusChange] = Field(default_factory=list)
    meta_changes: List[MonitoringChange] = Field(default_factory=list)
    issues_found: Dict[str, Any] = Field(default_factory=dict)

class MonitoringSummary(BaseModel):
    """Resumen de monitoreo para un período"""
    total_checks: int
    days_monitored: int
    avg_uptime_percentage: float
    total_changes: int
    changes_by_type: Dict[str, int]
    most_changed_pages: List[Dict[str, Any]]