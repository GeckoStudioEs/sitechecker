# app/schemas/audit.py
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class SEOIssue(BaseModel):
    """Esquema para un problema de SEO encontrado"""
    type: str
    severity: str
    category: Optional[str] = "general"
    description: str
    recommendation: Optional[str] = None

class CrawlSettings(BaseModel):
    """Configuración para el crawler"""
    start_url: str
    max_pages: int = 500
    respect_robots_txt: bool = True
    follow_nofollow: bool = False
    max_concurrent_requests: int = 5
    timeout: int = 30  # segundos
    user_agent: str = "SEOAnalyzer Bot (+https://example.com/bot)"
    follow_external_links: bool = False

class LinkData(BaseModel):
    """Datos de un enlace"""
    url: str
    text: Optional[str] = None
    nofollow: bool = False

class PageData(BaseModel):
    """Datos de una página analizada"""
    url: str
    status_code: Optional[int] = None
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1: Optional[List[str]] = None
    canonical_url: Optional[str] = None
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    word_count: Optional[int] = None
    indexable: bool = True
    page_score: Optional[int] = None
    internal_links: List[Dict[str, Any]] = Field(default_factory=list)
    external_links: List[Dict[str, Any]] = Field(default_factory=list)
    inbound_links: List[Dict[str, Any]] = Field(default_factory=list)
    meta_robots: Optional[str] = None
    http_headers: Dict[str, Any] = Field(default_factory=dict)
    structured_data: Dict[str, Any] = Field(default_factory=dict)
    issues: List[Dict[str, Any]] = Field(default_factory=list)

class AuditSettings(BaseModel):
    """Configuración para una auditoría"""
    max_pages: int = 500
    respect_robots_txt: bool = True
    follow_nofollow: bool = False
    crawl_noindex: bool = False
    crawl_parameters: bool = True
    parallel_requests: int = 3
    user_agent: str = "desktop"
    crawl_images: bool = False
    crawl_js: bool = False
    crawl_css: bool = False
    crawl_external: bool = False
    country: Optional[str] = None

class AuditSummary(BaseModel):
    """Resumen de una auditoría"""
    site_score: int
    crawled_pages: int
    indexable_pages: int
    issues_count: Dict[str, int]
    categories: Dict[str, Dict[str, int]]
    top_issues: List[Dict[str, Any]]

class AuditResponse(BaseModel):
    """Respuesta para una auditoría iniciada"""
    audit_id: int
    status: str

class AuditStatusResponse(BaseModel):
    """Estado de una auditoría"""
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    crawled_pages: int = 0
    total_pages: int = 0
    progress_percentage: Optional[float] = None