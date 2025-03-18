from typing import Dict, List, Optional, Any, Tuple
from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date

from app.db.models import Keyword, KeywordPosition, Project, KeywordGroup, User
from app.schemas.keywords import KeywordSettings, KeywordAddRequest, KeywordCreate

class KeywordService:
    """Servicio para gestionar palabras clave y su seguimiento"""
    
    def __init__(self, db: Session, background_tasks: Optional[BackgroundTasks] = None):
        """
        Inicializa el servicio con la sesión de base de datos
        
        Args:
            db: Sesión de SQLAlchemy
            background_tasks: Gestor de tareas en segundo plano (opcional)
        """
        self.db = db
        self.background_tasks = background_tasks
    
    def add_keywords(self, project_id: int, request: KeywordAddRequest, user_id: int) -> Tuple[int, int]:
        """
        Añade palabras clave a un proyecto para seguimiento
        
        Args:
            project_id: ID del proyecto
            request: Solicitud con palabras clave y configuración
            user_id: ID del usuario que añade las palabras clave
            
        Returns:
            Tupla con (cantidad_añadidas, cantidad_omitidas)
        """
        # Verificar que el proyecto existe
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"El proyecto con ID {project_id} no existe")
        
        # Inicializar contadores
        added = 0
        skipped = 0
        
        # Procesar cada palabra clave
        for keyword_text in request.keywords:
            # Omitir palabras clave vacías
            if not keyword_text.strip():
                skipped += 1
                continue
                
            # Verificar si la palabra clave ya existe para este proyecto
            existing = self.db.query(Keyword).filter(
                Keyword.project_id == project_id,
                Keyword.keyword == keyword_text,
                Keyword.country == request.settings.country,
                Keyword.device == request.settings.device,
                Keyword.search_engine == request.settings.search_engine
            ).first()
            
            if existing:
                skipped += 1
                continue
            
            # Crear nueva palabra clave
            keyword = Keyword(
                project_id=project_id,
                keyword=keyword_text,
                country=request.settings.country,
                language=request.settings.language,
                search_engine=request.settings.search_engine,
                device=request.settings.device,
                target_url=request.target_url,
                created_by=user_id
            )
            
            self.db.add(keyword)
            added += 1
        
        # Guardar cambios en la base de datos
        self.db.commit()
        
        # Si se solicitó comprobar posiciones y se añadieron palabras clave
        if request.check_positions and added > 0 and self.background_tasks:
            # Ejecutar la comprobación de posiciones en segundo plano
            self.background_tasks.add_task(
                self.update_positions,
                project_id
            )
        
        return (added, skipped)
    
    def delete_keywords(self, project_id: int, keyword_ids: List[int]) -> int:
        """
        Elimina palabras clave del seguimiento
        
        Args:
            project_id: ID del proyecto
            keyword_ids: Lista de IDs de palabras clave a eliminar
            
        Returns:
            Número de palabras clave eliminadas
        """
        # Verificar que las palabras clave pertenecen al proyecto
        keywords = self.db.query(Keyword).filter(
            Keyword.project_id == project_id,
            Keyword.id.in_(keyword_ids)
        ).all()
        
        # Eliminar cada palabra clave
        for keyword in keywords:
            self.db.delete(keyword)
        
        # Guardar cambios y devolver cantidad eliminada
        self.db.commit()
        return len(keywords)
    
    def get_keywords(
        self, 
        project_id: int, 
        search: Optional[str] = None, 
        group_id: Optional[int] = None,
        page: int = 1, 
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Obtiene palabras clave de un proyecto con paginación y filtros
        
        Args:
            project_id: ID del proyecto
            search: Texto para filtrar palabras clave (opcional)
            group_id: ID del grupo para filtrar (opcional)
            page: Número de página
            page_size: Tamaño de página
            
        Returns:
            Diccionario con palabras clave paginadas y metadatos
        """
        # Consulta base
        query = self.db.query(Keyword).filter(Keyword.project_id == project_id)
        
        # Aplicar filtros
        if search:
            query = query.filter(Keyword.keyword.ilike(f"%{search}%"))
        
        if group_id:
            query = query.filter(Keyword.group_id == group_id)
        
        # Contar total
        total = query.count()
        
        # Aplicar paginación
        offset = (page - 1) * page_size
        keywords = query.order_by(Keyword.keyword).offset(offset).limit(page_size).all()
        
        # Construir resultado
        result = {
            "items": keywords,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
        
        return result
    
    def get_keyword_detail(self, keyword_id: int) -> Dict[str, Any]:
        """
        Obtiene detalles de una palabra clave específica, incluyendo historial de posiciones
        
        Args:
            keyword_id: ID de la palabra clave
            
        Returns:
            Diccionario con detalles de la palabra clave
        """
        # Obtener la palabra clave
        keyword = self.db.query(Keyword).filter(Keyword.id == keyword_id).first()
        if not keyword:
            raise ValueError(f"Palabra clave con ID {keyword_id} no encontrada")
        
        # Obtener historial de posiciones recientes
        positions = self.db.query(KeywordPosition).filter(
            KeywordPosition.keyword_id == keyword_id
        ).order_by(KeywordPosition.check_date.desc()).limit(10).all()
        
        # Convertir a diccionario
        result = {
            "id": keyword.id,
            "project_id": keyword.project_id,
            "keyword": keyword.keyword,
            "country": keyword.country,
            "language": keyword.language,
            "search_engine": keyword.search_engine,
            "device": keyword.device,
            "volume": keyword.volume,
            "cpc": keyword.cpc,
            "competition": keyword.competition,
            "target_url": keyword.target_url,
            "group_id": keyword.group_id,
            "created_at": keyword.created_at,
            "created_by": keyword.created_by,
            "group_name": keyword.group.name if keyword.group else None,
            "positions": [
                {
                    "id": pos.id,
                    "position": pos.position,
                    "previous_position": pos.previous_position,
                    "check_date": pos.check_date,
                    "url": pos.url,
                    "serp_features": pos.serp_features
                } 
                for pos in positions
            ]
        }
        
        return result
    
    async def update_positions(self, project_id: int, keyword_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Actualiza las posiciones de las palabras clave
        
        Args:
            project_id: ID del proyecto
            keyword_ids: Lista opcional de IDs de palabras clave a actualizar
            
        Returns:
            Diccionario con resultados de la actualización
        """
        # Consulta base para obtener palabras clave
        query = self.db.query(Keyword).filter(Keyword.project_id == project_id)
        
        # Filtrar por IDs específicos si se proporcionan
        if keyword_ids:
            query = query.filter(Keyword.id.in_(keyword_ids))
        
        # Obtener palabras clave
        keywords = query.all()
        
        if not keywords:
            return {"updated": 0, "errors": 0, "message": "No hay palabras clave para actualizar"}
        
        # Aquí se implementaría la llamada real a un servicio de SERP
        # Por ahora, simulamos resultados
        
        updated = 0
        errors = 0
        
        for keyword in keywords:
            try:
                # Obtener posición anterior más reciente
                prev_position = self.db.query(KeywordPosition).filter(
                    KeywordPosition.keyword_id == keyword.id
                ).order_by(KeywordPosition.check_date.desc()).first()
                
                # Simular nueva posición (en una implementación real, llamaríamos a un servicio de SERP)
                import random
                new_position = random.randint(1, 100)
                previous_value = prev_position.position if prev_position else None
                
                # Crear registro de posición
                position = KeywordPosition(
                    keyword_id=keyword.id,
                    check_date=datetime.now(),
                    position=new_position,
                    previous_position=previous_value,
                    url=f"https://example.com/result-{new_position}",
                    serp_features={"featured_snippet": random.choice([True, False])}
                )
                
                self.db.add(position)
                updated += 1
                
            except Exception as e:
                errors += 1
                print(f"Error actualizando posición para {keyword.keyword}: {str(e)}")
        
        # Guardar cambios
        self.db.commit()
        
        return {
            "updated": updated,
            "errors": errors,
            "message": f"Se actualizaron {updated} palabras clave con {errors} errores"
        }
    
    def create_keyword_group(self, project_id: int, name: str, keyword_ids: List[int]) -> int:
        """
        Crea un grupo de palabras clave
        
        Args:
            project_id: ID del proyecto
            name: Nombre del grupo
            keyword_ids: Lista de IDs de palabras clave a incluir
            
        Returns:
            ID del grupo creado
        """
        # Verificar que el proyecto existe
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"El proyecto con ID {project_id} no existe")
        
        # Verificar que las palabras clave pertenecen al proyecto
        keywords = self.db.query(Keyword).filter(
            Keyword.project_id == project_id,
            Keyword.id.in_(keyword_ids)
        ).all()
        
        if len(keywords) != len(keyword_ids):
            raise ValueError("Algunas palabras clave no existen o no pertenecen a este proyecto")
        
        # Crear grupo
        group = KeywordGroup(
            project_id=project_id,
            name=name,
            created_at=datetime.now()
        )
        
        self.db.add(group)
        self.db.flush()  # Para obtener el ID del grupo
        
        # Asignar palabras clave al grupo
        for keyword in keywords:
            keyword.group_id = group.id
        
        self.db.commit()
        return group.id
    
    def get_keyword_groups(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene grupos de palabras clave de un proyecto
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Lista de grupos con conteo de palabras clave
        """
        # Consulta para obtener grupos con conteo de palabras clave
        groups = self.db.query(
            KeywordGroup,
            func.count(Keyword.id).label('keyword_count')
        ).outerjoin(
            Keyword, KeywordGroup.id == Keyword.group_id
        ).filter(
            KeywordGroup.project_id == project_id
        ).group_by(
            KeywordGroup.id
        ).all()
        
        # Formatear resultado
        result = []
        for group, count in groups:
            result.append({
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "created_at": group.created_at,
                "keyword_count": count
            })
        
        return result
    
    def delete_keyword_group(self, group_id: int, remove_keywords: bool = False) -> bool:
        """
        Elimina un grupo de palabras clave
        
        Args:
            group_id: ID del grupo a eliminar
            remove_keywords: Si es True, también elimina las palabras clave
            
        Returns:
            True si se eliminó correctamente
        """
        # Obtener el grupo
        group = self.db.query(KeywordGroup).filter(KeywordGroup.id == group_id).first()
        if not group:
            raise ValueError(f"Grupo con ID {group_id} no encontrado")
        
        # Manejar las palabras clave del grupo
        if remove_keywords:
            # Eliminar las palabras clave
            keywords = self.db.query(Keyword).filter(Keyword.group_id == group_id).all()
            for keyword in keywords:
                self.db.delete(keyword)
        else:
            # Desasociar las palabras clave
            self.db.query(Keyword).filter(Keyword.group_id == group_id).update({"group_id": None})
        
        # Eliminar el grupo
        self.db.delete(group)
        self.db.commit()
        
        return True
    
    def get_suggested_keywords(self, seed_keyword: str, country: str = 'us', language: str = 'en') -> List[Dict[str, Any]]:
        """
        Obtiene sugerencias de palabras clave basadas en una semilla
        
        Args:
            seed_keyword: Palabra clave semilla
            country: Código del país
            language: Código del idioma
            
        Returns:
            Lista de sugerencias de palabras clave
        """
        # En una implementación real, llamaríamos a una API externa
        # Por ahora, generamos algunas sugerencias de ejemplo
        
        # Simplemente añadimos algunos prefijos y sufijos comunes
        prefixes = ["best", "top", "how to", "why", "where to", "when to"]
        suffixes = ["guide", "tutorial", "tips", "services", "near me", "online"]
        
        suggestions = []
        
        # Añadir la semilla original
        suggestions.append({
            "keyword": seed_keyword,
            "volume": 1000,
            "cpc": 1.5,
            "competition": 0.65,
            "difficulty": 45
        })
        
        # Añadir combinaciones con prefijos
        for prefix in prefixes:
            keyword = f"{prefix} {seed_keyword}"
            suggestions.append({
                "keyword": keyword,
                "volume": int(800 * (0.5 + 0.5 * len(keyword) / 20)),
                "cpc": round(0.5 + 2 * len(keyword) / 30, 2),
                "competition": round(0.3 + 0.6 * len(keyword) / 40, 2),
                "difficulty": min(100, 30 + len(keyword))
            })
        
        # Añadir combinaciones con sufijos
        for suffix in suffixes:
            keyword = f"{seed_keyword} {suffix}"
            suggestions.append({
                "keyword": keyword,
                "volume": int(600 * (0.5 + 0.5 * len(keyword) / 20)),
                "cpc": round(0.5 + 2 * len(keyword) / 30, 2),
                "competition": round(0.3 + 0.6 * len(keyword) / 40, 2),
                "difficulty": min(100, 25 + len(keyword))
            })
        
        return suggestions