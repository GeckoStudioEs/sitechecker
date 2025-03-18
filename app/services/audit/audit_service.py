# app/services/audit/audit_service.py
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import SiteAudit, Page, Issue, Project
from app.schemas.audit import AuditSettings, AuditSummary, PageData, CrawlSettings
from app.services.crawler.crawler import Crawler

class AuditService:
    """Servicio para gestionar auditorías SEO"""
    
    def __init__(self, db: Session):
        """
        Inicializa el servicio con la sesión de base de datos
        
        Args:
            db: Sesión de SQLAlchemy
        """
        self.db = db
        
    async def start_audit(self, project_id: int, settings: AuditSettings, user_id: int) -> int:
        """
        Inicia una nueva auditoría de sitio y devuelve su ID
        
        Args:
            project_id: ID del proyecto
            settings: Configuración de la auditoría
            user_id: ID del usuario que inicia la auditoría
            
        Returns:
            ID de la auditoría creada
        """
        # Verificar que el proyecto existe
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("El proyecto no existe")
            
        # Crear registro de auditoría
        audit = SiteAudit(
            project_id=project_id,
            start_time=datetime.now(),
            status="in_progress",
            settings=settings.dict(),
            created_by=user_id
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        
        # Iniciar el proceso de auditoría en segundo plano
        asyncio.create_task(self._run_audit(audit.id, settings))
        
        return audit.id
        
    async def _run_audit(self, audit_id: int, settings: AuditSettings) -> None:
        """
        Ejecuta el proceso de auditoría
        
        Args:
            audit_id: ID de la auditoría
            settings: Configuración de la auditoría
        """
        # Obtener la auditoría de la base de datos
        audit = self.db.query(SiteAudit).filter(SiteAudit.id == audit_id).first()
        if not audit:
            return
            
        try:
            # Obtener el proyecto
            project = self.db.query(Project).filter(Project.id == audit.project_id).first()
            if not project:
                raise ValueError("Proyecto no encontrado")
                
            # Configurar crawler
            start_url = f"{project.protocol}://{project.domain}"
            crawler_settings = CrawlSettings(
                start_url=start_url,
                max_pages=settings.max_pages,
                respect_robots_txt=settings.respect_robots_txt,
                follow_nofollow=settings.follow_nofollow,
                max_concurrent_requests=settings.parallel_requests,
                user_agent=settings.user_agent,
                follow_external_links=settings.crawl_external
            )
            
            # Iniciar crawling
            crawler = Crawler(crawler_settings)
            crawl_results = await crawler.start()
            
            # Procesar resultados
            indexable_pages = 0
            issues_by_type = {}
            issues_by_category = {}
            
            for url, page_data in crawl_results.items():
                # Guardar página en la base de datos
                page = Page(
                    project_id=project.id,
                    audit_id=audit.id,
                    url=url,
                    canonical_url=page_data.canonical_url,
                    status_code=page_data.status_code,
                    page_title=page_data.title,
                    meta_description=page_data.meta_description,
                    h1=page_data.h1[0] if page_data.h1 and len(page_data.h1) > 0 else None,
                    content_type=page_data.content_type,
                    size_bytes=page_data.size_bytes,
                    word_count=page_data.word_count,
                    indexable=page_data.indexable,
                    page_score=page_data.page_score,
                    internal_links_count=len(page_data.internal_links),
                    external_links_count=len(page_data.external_links)
                )
                self.db.add(page)
                
                if page_data.indexable:
                    indexable_pages += 1
                
                # Guardar problemas en la base de datos
                for issue_data in page_data.issues:
                    category = issue_data.get("category", "general")
                    severity = issue_data.get("severity", "notice")
                    issue_type = issue_data.get("type", "unknown")
                    
                    issue = Issue(
                        audit_id=audit.id,
                        issue_type=issue_type,
                        severity=severity,
                        category=category,
                        description=issue_data.get("description", ""),
                        affected_pages_count=1  # Se actualizará después
                    )
                    self.db.add(issue)
                    
                    # Actualizar contadores de problemas
                    key = f"{category}:{issue_type}"
                    issues_by_type[key] = issues_by_type.get(key, 0) + 1
                    
                    # Actualizar contadores por categoría
                    if category not in issues_by_category:
                        issues_by_category[category] = {}
                    issues_by_category[category][severity] = issues_by_category[category].get(severity, 0) + 1
            
            # Actualizar conteo de páginas afectadas por cada tipo de problema
            for key, count in issues_by_type.items():
                category, issue_type = key.split(":", 1)
                issues = self.db.query(Issue).filter(
                    Issue.audit_id == audit.id,
                    Issue.issue_type == issue_type,
                    Issue.category == category
                ).all()
                for issue in issues:
                    issue.affected_pages_count = count
            
            # Calcular puntuación general del sitio (implementación básica)
            site_score = self._calculate_site_score(crawl_results.values())
            
            # Actualizar registro de auditoría
            audit.end_time = datetime.now()
            audit.status = "completed"
            audit.total_pages = len(crawl_results)
            audit.crawled_pages = len(crawl_results)
            audit.indexable_pages = indexable_pages
            audit.site_score = site_score
            audit.issues_count = {
                "critical": sum(issue.get("severity") == "critical" for page in crawl_results.values() for issue in page.issues),
                "warning": sum(issue.get("severity") == "warning" for page in crawl_results.values() for issue in page.issues),
                "opportunity": sum(issue.get("severity") == "opportunity" for page in crawl_results.values() for issue in page.issues),
                "notice": sum(issue.get("severity") == "notice" for page in crawl_results.values() for issue in page.issues)
            }
            
            self.db.commit()
            
        except Exception as e:
            # Actualizar registro de auditoría con fallo
            audit.end_time = datetime.now()
            audit.status = "failed"
            self.db.commit()
            # Registrar el error
            print(f"Error en la auditoría: {str(e)}")
    
    def get_audit_status(self, audit_id: int) -> Dict[str, Any]:
        """
        Obtiene el estado de una auditoría en progreso
        
        Args:
            audit_id: ID de la auditoría
            
        Returns:
            Diccionario con el estado de la auditoría
        """
        audit = self.db.query(SiteAudit).filter(SiteAudit.id == audit_id).first()
        if not audit:
            raise ValueError("Auditoría no encontrada")
            
        result = {
            "status": audit.status,
            "start_time": audit.start_time,
            "end_time": audit.end_time,
            "crawled_pages": audit.crawled_pages,
            "total_pages": audit.total_pages
        }
        
        # Calcular porcentaje de progreso para auditorías en curso
        if audit.status == "in_progress" and audit.total_pages > 0:
            result["progress_percentage"] = round((audit.crawled_pages / audit.total_pages) * 100, 2)
            
        return result
    
    def get_audit_summary(self, audit_id: int) -> AuditSummary:
        """
        Obtiene el resumen de una auditoría completada
        
        Args:
            audit_id: ID de la auditoría
            
        Returns:
            Resumen de la auditoría
        """
        audit = self.db.query(SiteAudit).filter(SiteAudit.id == audit_id).first()
        if not audit:
            raise ValueError("Auditoría no encontrada")
            
        if audit.status != "completed":
            raise ValueError(f"La auditoría no está completada (estado actual: {audit.status})")
            
        # Obtener categorías de problemas
        categories = {}
        issues_by_category = self.db.query(
            Issue.category,
            Issue.severity,
            Issue.affected_pages_count
        ).filter(
            Issue.audit_id == audit_id
        ).all()
        
        for category, severity, count in issues_by_category:
            if category not in categories:
                categories[category] = {}
            if severity not in categories[category]:
                categories[category][severity] = 0
            categories[category][severity] += count
            
        # Obtener principales problemas
        top_issues = []
        top_db_issues = self.db.query(Issue).filter(
            Issue.audit_id == audit_id
        ).order_by(
            Issue.severity.in_(["critical", "warning"]).desc(),
            Issue.affected_pages_count.desc()
        ).limit(10).all()
        
        for issue in top_db_issues:
            top_issues.append({
                "type": issue.issue_type,
                "severity": issue.severity,
                "category": issue.category,
                "description": issue.description,
                "affected_pages_count": issue.affected_pages_count
            })
            
        return AuditSummary(
            site_score=audit.site_score,
            crawled_pages=audit.crawled_pages,
            indexable_pages=audit.indexable_pages,
            issues_count=audit.issues_count,
            categories=categories,
            top_issues=top_issues
        )
    
    def get_audit_issues(self, audit_id: int, severity: Optional[str] = None, 
                         category: Optional[str] = None, page: int = 1, 
                         page_size: int = 50) -> Dict[str, Any]:
        """
        Obtiene problemas detectados en una auditoría
        
        Args:
            audit_id: ID de la auditoría
            severity: Filtrar por severidad
            category: Filtrar por categoría
            page: Número de página para paginación
            page_size: Tamaño de página para paginación
            
        Returns:
            Diccionario con problemas paginados
        """
        query = self.db.query(Issue).filter(Issue.audit_id == audit_id)
        
        # Aplicar filtros
        if severity:
            query = query.filter(Issue.severity == severity)
        if category:
            query = query.filter(Issue.category == category)
            
        # Contar total de resultados
        total_items = query.count()
        total_pages = (total_items + page_size - 1) // page_size
        
        # Aplicar paginación
        query = query.order_by(
            Issue.severity.in_(["critical", "warning"]).desc(),
            Issue.affected_pages_count.desc()
        ).offset((page - 1) * page_size).limit(page_size)
        
        issues = []
        for issue in query.all():
            issues.append({
                "id": issue.id,
                "type": issue.issue_type,
                "severity": issue.severity,
                "category": issue.category,
                "description": issue.description,
                "affected_pages_count": issue.affected_pages_count,
                "is_fixed": issue.is_fixed,
                "ignored": issue.ignored
            })
            
        return {
            "items": issues,
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages
        }
    
    def get_page_details(self, audit_id: int, url: str) -> Dict[str, Any]:
        """
        Obtiene detalles completos de una página específica
        
        Args:
            audit_id: ID de la auditoría
            url: URL de la página
            
        Returns:
            Diccionario con detalles de la página
        """
        page = self.db.query(Page).filter(
            Page.audit_id == audit_id,
            Page.url == url
        ).first()
        
        if not page:
            raise ValueError("Página no encontrada")
            
        # Obtener enlaces entrantes
        inbound_links = self.db.query(
            Page.url, 
            Page.page_title
        ).join(
            Link, 
            Link.source_page_id == Page.id
        ).filter(
            Link.target_page_id == page.id,
            Link.audit_id == audit_id
        ).all()
        
        # Obtener problemas específicos de esta página
        page_issues = self.db.query(PageIssue).filter(
            PageIssue.page_id == page.id
        ).all()
        
        issues = []
        for issue in page_issues:
            issues.append({
                "type": issue.issue_type,
                "severity": issue.severity,
                "category": issue.category,
                "description": issue.description
            })
            
        result = {
            "url": page.url,
            "canonical_url": page.canonical_url,
            "status_code": page.status_code,
            "page_title": page.page_title,
            "meta_description": page.meta_description,
            "h1": page.h1,
            "content_type": page.content_type,
            "size_bytes": page.size_bytes,
            "word_count": page.word_count,
            "indexable": page.indexable,
            "page_score": page.page_score,
            "internal_links_count": page.internal_links_count,
            "external_links_count": page.external_links_count,
            "inbound_links_count": page.inbound_links_count,
            "level": page.level,
            "inbound_links": [{"url": url, "title": title} for url, title in inbound_links],
            "issues": issues
        }
        
        return result
    
    def _calculate_site_score(self, pages) -> int:
        """
        Calcula la puntuación general del sitio
        
        Args:
            pages: Lista de datos de páginas
            
        Returns:
            Puntuación del sitio (0-100)
        """
        if not pages:
            return 0
            
        # Contar páginas indexables
        indexable_pages = [p for p in pages if p.indexable]
        if not indexable_pages:
            return 0
            
        # Calcular puntuación media de páginas indexables
        avg_score = sum(p.page_score or 0 for p in indexable_pages) / len(indexable_pages)
        
        # Penalizar por porcentaje de páginas con problemas críticos
        critical_issues_pages = sum(1 for p in pages 
                                  for issue in p.issues 
                                  if issue.get("severity") == "critical")
        critical_penalty = (critical_issues_pages / len(pages)) * 30  # Hasta 30 puntos de penalización
        
        # Penalizar por porcentaje de páginas con problemas de advertencia
        warning_issues_pages = sum(1 for p in pages 
                                 for issue in p.issues 
                                 if issue.get("severity") == "warning")
        warning_penalty = (warning_issues_pages / len(pages)) * 15  # Hasta 15 puntos de penalización
        
        # Calcular puntuación final
        score = avg_score - critical_penalty - warning_penalty
        
        return max(0, min(100, round(score)))