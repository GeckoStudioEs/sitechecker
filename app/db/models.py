import uuid
from datetime import datetime
from typing import List, Dict, Optional

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, JSON, Table, Float, Enum
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

# Tabla intermedia para la relación many-to-many entre usuarios y proyectos
project_user = Table(
    "project_permission",
    Base.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("project_id", Integer, ForeignKey("project.id", ondelete="CASCADE")),
    Column("user_id", Integer, ForeignKey("user.id", ondelete="CASCADE")),
    Column("permission_level", String(20), nullable=False),  # view, edit, admin
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("created_by", Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True),
)

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(20), default="user")  # user, admin, agency
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, nullable=True)

    # Relaciones
    projects = relationship(
        "Project",
        secondary=project_user,
        back_populates="users"
    )
    owned_projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    domain = Column(String(255), nullable=False)
    protocol = Column(String(10), default="https")
    domain_scope = Column(String(20), default="domain")  # domain, subdomain, path
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    tags = Column(ARRAY(String), default=[])
    credits_balance = Column(Integer, default=100)

    # Relaciones
    owner = relationship("User", back_populates="owned_projects")
    users = relationship(
        "User",
        secondary=project_user,
        back_populates="projects"
    )
    google_integrations = relationship("GoogleIntegration", back_populates="project", cascade="all, delete-orphan")
    site_audits = relationship("SiteAudit", back_populates="project", cascade="all, delete-orphan")
    pages = relationship("Page", back_populates="project", cascade="all, delete-orphan")
    site_monitorings = relationship("SiteMonitoring", back_populates="project", cascade="all, delete-orphan")
    keywords = relationship("Keyword", back_populates="project", cascade="all, delete-orphan")
    competitors = relationship("Competitor", back_populates="project", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="project", cascade="all, delete-orphan")
    segments = relationship("Segment", back_populates="project", cascade="all, delete-orphan")

class GoogleIntegration(Base):
    __tablename__ = "google_integration"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)
    integration_type = Column(String(20), nullable=False)  # analytics, search_console
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expiry = Column(DateTime)
    account_id = Column(String(255))
    property_id = Column(String(255))
    view_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, nullable=True)

    # Relaciones
    project = relationship("Project", back_populates="google_integrations")

class SiteAudit(Base):
    __tablename__ = "site_audit"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), default="in_progress")  # in_progress, completed, failed
    total_pages = Column(Integer, default=0)
    crawled_pages = Column(Integer, default=0)
    indexable_pages = Column(Integer, default=0)
    site_score = Column(Integer, nullable=True)  # 0-100
    issues_count = Column(JSON, nullable=True)  # {critical: 10, warning: 20, opportunity: 15, notice: 5}
    settings = Column(JSON, nullable=True)  # crawl settings used
    created_by = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)

    # Relaciones
    project = relationship("Project", back_populates="site_audits")
    issues = relationship("Issue", back_populates="audit", cascade="all, delete-orphan")
    pages = relationship("Page", back_populates="audit", cascade="all, delete-orphan")

class Issue(Base):
    __tablename__ = "issue"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("site_audit.id", ondelete="CASCADE"), nullable=False)
    issue_type = Column(String(50), nullable=False)  # title_missing, broken_link, etc.
    severity = Column(String(20), nullable=False)  # critical, warning, opportunity, notice
    category = Column(String(30), nullable=False)  # links, content, performance, security, etc.
    affected_pages_count = Column(Integer, default=0)
    description = Column(Text)
    impact = Column(Text)
    recommendation = Column(Text)
    is_fixed = Column(Boolean, default=False)
    ignored = Column(Boolean, default=False)

    # Relaciones
    audit = relationship("SiteAudit", back_populates="issues")

class Page(Base):
    __tablename__ = "page"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)
    audit_id = Column(Integer, ForeignKey("site_audit.id", ondelete="CASCADE"), nullable=False)
    url = Column(Text, nullable=False)
    canonical_url = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=True)
    page_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    h1 = Column(Text, nullable=True)
    content_type = Column(String(100), nullable=True)
    size_bytes = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    indexable = Column(Boolean, nullable=True)
    level = Column(Integer, nullable=True)  # depth from homepage
    page_score = Column(Integer, nullable=True)  # 0-100
    page_weight = Column(Float, nullable=True)  # importance score
    last_modified = Column(DateTime, nullable=True)
    found_at = Column(JSON, nullable=True)  # {sitemap: true, internal_links: true, etc}
    internal_links_count = Column(Integer, default=0)
    external_links_count = Column(Integer, default=0)
    inbound_links_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    project = relationship("Project", back_populates="pages")
    audit = relationship("SiteAudit", back_populates="pages")
    outbound_links = relationship("Link", foreign_keys="Link.source_page_id", back_populates="source_page", cascade="all, delete-orphan")
    inbound_links = relationship("Link", foreign_keys="Link.target_page_id", back_populates="target_page", cascade="all, delete-orphan")

class Link(Base):
    __tablename__ = "link"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("site_audit.id", ondelete="CASCADE"), nullable=False)
    source_page_id = Column(Integer, ForeignKey("page.id", ondelete="CASCADE"), nullable=False)
    target_url = Column(Text, nullable=False)
    target_page_id = Column(Integer, ForeignKey("page.id", ondelete="SET NULL"), nullable=True)
    link_text = Column(Text, nullable=True)
    is_internal = Column(Boolean, nullable=True)
    is_followed = Column(Boolean, default=True)
    is_broken = Column(Boolean, default=False)
    status_code = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    source_page = relationship("Page", foreign_keys=[source_page_id], back_populates="outbound_links")
    target_page = relationship("Page", foreign_keys=[target_page_id], back_populates="inbound_links")

class SiteMonitoring(Base):
    __tablename__ = "site_monitoring"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)
    check_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), nullable=True)  # up, down, issues
    response_time = Column(Integer, nullable=True)  # ms
    changes_detected = Column(JSON, nullable=True)
    total_pages = Column(Integer, nullable=True)
    new_pages = Column(Integer, default=0)
    changed_pages = Column(Integer, default=0)
    deleted_pages = Column(Integer, default=0)
    issues_found = Column(JSON, nullable=True)

    # Relaciones
    project = relationship("Project", back_populates="site_monitorings")

class Keyword(Base):
    __tablename__ = "keyword"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)
    keyword = Column(Text, nullable=False)
    country = Column(String(5), nullable=True)  # ISO code: es, us, etc.
    language = Column(String(5), nullable=True)  # ISO code: es, en, etc.
    search_engine = Column(String(20), default="google")  # google, bing, etc.
    device = Column(String(20), default="desktop")  # desktop, mobile
    volume = Column(Integer, nullable=True)
    cpc = Column(Float, nullable=True)
    competition = Column(Float, nullable=True)  # 0-1
    target_url = Column(Text, nullable=True)
    group_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)

    # Relaciones
    project = relationship("Project", back_populates="keywords")
    positions = relationship("KeywordPosition", back_populates="keyword", cascade="all, delete-orphan")

class KeywordPosition(Base):
    __tablename__ = "keyword_position"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("keyword.id", ondelete="CASCADE"), nullable=False)
    check_date = Column(DateTime, nullable=False)
    position = Column(Integer, nullable=True)
    previous_position = Column(Integer, nullable=True)
    url = Column(Text, nullable=True)  # URL posicionada
    serp_features = Column(JSON, nullable=True)  # featured snippets, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    keyword = relationship("Keyword", back_populates="positions")

class Competitor(Base):
    __tablename__ = "competitor"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)
    domain = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)
    visibility = Column(Float, nullable=True)  # domain visibility percentage
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    project = relationship("Project", back_populates="competitors")

class Alert(Base):
    __tablename__ = "alert"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # site_down, position_change, etc.
    delivery_method = Column(String(20), nullable=False)  # email, slack
    recipients = Column(ARRAY(String), nullable=True)
    slack_channel = Column(String(100), nullable=True)
    frequency = Column(String(20), nullable=True)  # realtime, daily, weekly
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)

    # Relaciones
    project = relationship("Project", back_populates="alerts")

class Segment(Base):
    __tablename__ = "segment"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    filter_rule = Column(JSON, nullable=True)  # {field: "url", operator: "contains", value: "/blog/"}
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)

    # Relaciones
    project = relationship("Project", back_populates="segments")