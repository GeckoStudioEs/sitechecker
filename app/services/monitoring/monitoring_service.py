# app/services/monitoring/monitoring_service.py
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime, timedelta
import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.db.models import SiteMonitoring, Project, Page, SiteAudit
from app.schemas.monitoring import MonitoringSettings, MonitoringResult
from app.utils.url_utils import normalize_url, is_valid_url

class MonitoringService:
    """Servicio para monitorear cambios en sitios web"""
    
    def __init__(self, db: Session):
        """
        Inicializa el servicio con la sesión de base de datos
        
        Args:
            db: Sesión de SQLAlchemy
        """
        self.db = db
        
    async def check_site(self, project_id: int) -> int:
        """
        Realiza una verificación de monitoreo para un sitio y devuelve el ID de monitoreo
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            ID del registro de monitoreo creado
        """
        # Obtener proyecto
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Proyecto no encontrado")
            
        # Crear registro de monitoreo
        monitoring = SiteMonitoring(
            project_id=project_id,
            check_time=datetime.now(),
            status="in_progress"
        )
        self.db.add(monitoring)
        self.db.commit()
        self.db.refresh(monitoring)
        
        # Iniciar la verificación en segundo plano
        asyncio.create_task(self._run_check(monitoring.id))
        
        return monitoring.id
        
    async def _run_check(self, monitoring_id: int) -> None:
        """
        Ejecuta el proceso de verificación de monitoreo
        
        Args:
            monitoring_id: ID del registro de monitoreo
        """
        # Obtener el registro de monitoreo
        monitoring = self.db.query(SiteMonitoring).filter(SiteMonitoring.id == monitoring_id).first()
        if not monitoring:
            return
            
        try:
            # Obtener el proyecto
            project = self.db.query(Project).filter(Project.id == monitoring.project_id).first()
            if not project:
                raise ValueError("Proyecto no encontrado")
                
            # Obtener la última auditoría completada
            latest_audit = self.db.query(SiteAudit).filter(
                SiteAudit.project_id == project.id,
                SiteAudit.status == "completed"
            ).order_by(SiteAudit.end_time.desc()).first()
            
            if not latest_audit:
                raise ValueError("No se encontró ninguna auditoría completada para este proyecto")
            
            # Obtener páginas importantes de la última auditoría
            important_pages = self.db.query(Page).filter(
                Page.audit_id == latest_audit.id,
                Page.indexable == True
            ).order_by(Page.page_score.desc()).limit(10).all()
            
            if not important_pages:
                raise ValueError("No se encontraron páginas para monitorear")
            
            # Verificar cada página
            changes_detected = {
                "content_changes": [],
                "status_changes": [],
                "meta_changes": []
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
                for page in important_pages:
                    # Verificar si la página es accesible
                    try:
                        headers = {
                            "User-Agent": "SEOAnalyzer Monitoring Bot (+https://example.com/bot)",
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
                        }
                        response = await session.get(page.url, headers=headers)
                        new_status = response.status
                        
                        # Verificar cambios de estado
                        if new_status != page.status_code:
                            changes_detected["status_changes"].append({
                                "url": page.url,
                                "old_status": page.status_code,
                                "new_status": new_status
                            })
                            
                        # Para respuestas exitosas, verificar cambios de contenido
                        if 200 <= new_status < 300:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extraer información básica
                            title = self._extract_title(soup)
                            meta_description = self._extract_meta_description(soup)
                            h1_tags = self._extract_h1(soup)
                            
                            # Verificar cambios en el título
                            if title and title != page.page_title:
                                changes_detected["meta_changes"].append({
                                    "url": page.url,
                                    "type": "title",
                                    "old_value": page.page_title,
                                    "new_value": title
                                })
                                
                            # Verificar cambios en la meta descripción
                            if meta_description and meta_description != page.meta_description:
                                changes_detected["meta_changes"].append({
                                    "url": page.url,
                                    "type": "meta_description",
                                    "old_value": page.meta_description,
                                    "new_value": meta_description
                                })
                                
                            # Verificar cambios en H1
                            if h1_tags and (not page.h1 or (h1_tags[0] != page.h1)):
                                changes_detected["meta_changes"].append({
                                    "url": page.url,
                                    "type": "h1",
                                    "old_value": page.h1,
                                    "new_value": h1_tags[0] if h1_tags else None
                                })
                                
                            # Verificar cambios de contenido (comparación simple de recuento de palabras)
                            word_count = self._count_words(soup)
                            if page.word_count and abs(word_count - page.word_count) > page.word_count * 0.1:
                                changes_detected["content_changes"].append({
                                    "url": page.url,
                                    "type": "content",
                                    "old_value": str(page.word_count),
                                    "new_value": str(word_count),
                                    "change_percentage": round((word_count - page.word_count) / page.word_count * 100, 2)
                                })
                                
                    except asyncio.TimeoutError:
                        # Registrar timeout como un cambio de estado
                        changes_detected["status_changes"].append({
                            "url": page.url,
                            "old_status": page.status_code,
                            "new_status": 0,
                            "error": "Tiempo de espera agotado"
                        })
                    except Exception as e:
                        # Registrar error y marcar como caído
                        print(f"Error al verificar {page.url}: {str(e)}")
                        changes_detected["status_changes"].append({
                            "url": page.url,
                            "old_status": page.status_code,
                            "new_status": 0,
                            "error": str(e)
                        })
            
            # Determinar estado del sitio
            site_status = "up"
            if any(change.get("new_status", 0) >= 500 for change in changes_detected["status_changes"]):
                site_status = "down"
            elif changes_detected["status_changes"] or changes_detected["meta_changes"] or changes_detected["content_changes"]:
                site_status = "issues"
                
            # Contar cambios
            total_pages = len(important_pages)
            changed_pages = len(set([c.get("url") for category in changes_detected.values() for c in category]))
            
            # Actualizar registro de monitoreo
            monitoring.status = site_status
            monitoring.changes_detected = changes_detected
            monitoring.total_pages = total_pages
            monitoring.changed_pages = changed_pages
            
            self.db.commit()
            
        except Exception as e:
            # Actualizar registro de monitoreo con fallo
            monitoring.status = "failed"
            monitoring.issues_found = {"error": str(e)}
            self.db.commit()
            # Registrar el error
            print(f"Error en la verificación de monitoreo: {str(e)}")
    
    def update_monitoring_settings(self, project_id: int, settings: MonitoringSettings) -> bool:
        """
        Actualiza la configuración de monitoreo de un proyecto
        
        Args:
            project_id: ID del proyecto
            settings: Nueva configuración de monitoreo
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Proyecto no encontrado")
            
        # Actualizar configuración
        project.settings = project.settings or {}
        project.settings["monitoring"] = settings.dict()
        project.updated_at = datetime.now()
        
        try:
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error al actualizar configuración de monitoreo: {str(e)}")
            return False
    
    def get_monitoring_history(self, project_id: int, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None, limit: int = 30) -> List[Dict[str, Any]]:
        """
        Obtiene historial de verificaciones de monitoreo
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio para filtrar (opcional)
            end_date: Fecha de fin para filtrar (opcional)
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de verificaciones de monitoreo
        """
        query = self.db.query(SiteMonitoring).filter(SiteMonitoring.project_id == project_id)
        
        if start_date:
            query = query.filter(SiteMonitoring.check_time >= start_date)
        if end_date:
            query = query.filter(SiteMonitoring.check_time <= end_date)
            
        # Ordenar por fecha descendente y limitar resultados
        results = query.order_by(SiteMonitoring.check_time.desc()).limit(limit).all()
        
        history = []
        for item in results:
            history.append({
                "id": item.id,
                "check_time": item.check_time,
                "status": item.status,
                "total_pages": item.total_pages or 0,
                "changed_pages": item.changed_pages or 0,
                "has_issues": bool(item.issues_found)
            })
            
        return history
    
    def get_monitoring_changes(self, monitoring_id: int) -> Dict[str, Any]:
        """
        Obtiene cambios detectados en una verificación específica
        
        Args:
            monitoring_id: ID del registro de monitoreo
            
        Returns:
            Diccionario con los cambios detectados
        """
        monitoring = self.db.query(SiteMonitoring).filter(SiteMonitoring.id == monitoring_id).first()
        if not monitoring:
            raise ValueError("Registro de monitoreo no encontrado")
            
        return {
            "id": monitoring.id,
            "check_time": monitoring.check_time,
            "status": monitoring.status,
            "total_pages": monitoring.total_pages or 0,
            "changed_pages": monitoring.changed_pages or 0,
            "changes": monitoring.changes_detected or {},
            "issues": monitoring.issues_found or {}
        }
    
    def get_monitoring_status(self, project_id: int) -> Dict[str, Any]:
        """
        Obtiene estado actual de monitoreo
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Estado actual de monitoreo
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Proyecto no encontrado")
            
        # Obtener configuración actual
        settings = project.settings.get("monitoring", {}) if project.settings else {}
        
        # Obtener última verificación
        last_check = self.db.query(SiteMonitoring).filter(
            SiteMonitoring.project_id == project_id
        ).order_by(SiteMonitoring.check_time.desc()).first()
        
        result = {
            "is_active": settings.get("is_active", False),
            "frequency": settings.get("frequency", "3d"),
            "last_check": None,
            "next_check": None,
            "current_status": "unknown"
        }
        
        if last_check:
            result["last_check"] = last_check.check_time
            result["current_status"] = last_check.status
            
            # Calcular próxima verificación basada en la frecuencia
            if settings.get("is_active", False):
                frequency = settings.get("frequency", "3d")
                
                next_check = last_check.check_time
                if frequency == "12h":
                    next_check += timedelta(hours=12)
                elif frequency == "daily":
                    next_check += timedelta(days=1)
                elif frequency == "3d":
                    next_check += timedelta(days=3)
                elif frequency == "weekly":
                    next_check += timedelta(weeks=1)
                elif frequency == "monthly":
                    next_check += timedelta(days=30)
                    
                result["next_check"] = next_check
                
        return result
    
    def get_monitoring_summary(self, project_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Obtiene resumen de monitoreo para un período
        
        Args:
            project_id: ID del proyecto
            days: Número de días a incluir en el resumen
            
        Returns:
            Resumen de monitoreo
        """
        start_date = datetime.now() - timedelta(days=days)
        
        # Obtener verificaciones en el período
        checks = self.db.query(SiteMonitoring).filter(
            SiteMonitoring.project_id == project_id,
            SiteMonitoring.check_time >= start_date
        ).order_by(SiteMonitoring.check_time.asc()).all()
        
        if not checks:
            return {
                "total_checks": 0,
                "days_monitored": days,
                "avg_uptime_percentage": 0,
                "total_changes": 0,
                "changes_by_type": {},
                "most_changed_pages": []
            }
        
        # Calcular estadísticas
        uptime_checks = sum(1 for check in checks if check.status == "up")
        total_checks = len(checks)
        
        # Contar cambios por tipo
        changes_by_type = {
            "content": 0,
            "meta": 0,
            "status": 0
        }
        
        # Contar cambios por página
        changes_by_page = {}
        
        total_changes = 0
        for check in checks:
            if check.changes_detected:
                # Contar cambios de contenido
                content_changes = check.changes_detected.get("content_changes", [])
                changes_by_type["content"] += len(content_changes)
                
                # Contar cambios de meta
                meta_changes = check.changes_detected.get("meta_changes", [])
                changes_by_type["meta"] += len(meta_changes)
                
                # Contar cambios de estado
                status_changes = check.changes_detected.get("status_changes", [])
                changes_by_type["status"] += len(status_changes)
                
                # Acumular por página
                for category in ["content_changes", "meta_changes", "status_changes"]:
                    for change in check.changes_detected.get(category, []):
                        url = change.get("url", "")
                        if url:
                            if url not in changes_by_page:
                                changes_by_page[url] = 0
                            changes_by_page[url] += 1
                            total_changes += 1
        
        # Encontrar páginas con más cambios
        most_changed_pages = []
        for url, count in sorted(changes_by_page.items(), key=lambda x: x[1], reverse=True)[:5]:
            most_changed_pages.append({
                "url": url,
                "changes_count": count
            })
        
        return {
            "total_checks": total_checks,
            "days_monitored": days,
            "avg_uptime_percentage": round((uptime_checks / total_checks) * 100, 2) if total_checks > 0 else 0,
            "total_changes": total_changes,
            "changes_by_type": changes_by_type,
            "most_changed_pages": most_changed_pages
        }
    
    # Métodos auxiliares
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae el título de la página"""
        title_tag = soup.find('title')
        return title_tag.text.strip() if title_tag else None
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae la meta descripción"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else None
    
    def _extract_h1(self, soup: BeautifulSoup) -> List[str]:
        """Extrae los encabezados H1"""
        return [h1.text.strip() for h1 in soup.find_all('h1')]
    
    def _count_words(self, soup: BeautifulSoup) -> int:
        """Cuenta palabras en el contenido principal"""
        # Eliminar scripts y estilos
        for script in soup(["script", "style"]):
            script.extract()
        
        text = soup.get_text()
        words = text.lower().split()
        return len(words)