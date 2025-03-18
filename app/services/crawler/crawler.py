# app/services/crawler/crawler.py
from typing import Dict, List, Optional, Set
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from app.schemas.audit import PageData, CrawlSettings
from app.utils.url_utils import normalize_url, is_internal_url

class Crawler:
    """Clase principal para rastrear sitios web"""
    
    def __init__(self, settings: CrawlSettings):
        """
        Inicializa el crawler con configuraciones específicas
        
        Args:
            settings: Configuración del crawler incluyendo URL inicial, límites, etc.
        """
        self.settings = settings
        self.visited_urls: Set[str] = set()
        self.queue: Set[str] = {settings.start_url}
        self.results: Dict[str, PageData] = {}
        self.session = None
        
    async def start(self) -> Dict[str, PageData]:
        """
        Inicia el proceso de crawling
        
        Returns:
            Diccionario con los datos de las páginas rastreadas
        """
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": self.settings.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            }
        )
        
        try:
            # Crear tareas para procesamiento paralelo
            tasks = []
            for _ in range(min(len(self.queue), self.settings.max_concurrent_requests)):
                tasks.append(asyncio.create_task(self._crawl_next()))
                
            await asyncio.gather(*tasks)
            return self.results
        finally:
            await self.session.close()
            
    async def _crawl_next(self):
        """Procesa la siguiente URL en la cola"""
        while self.queue and len(self.visited_urls) < self.settings.max_pages:
            # Obtener la siguiente URL de la cola
            url = self.queue.pop()
            self.visited_urls.add(url)
            
            try:
                # Obtener y procesar la página
                page_data = await self._fetch_and_process(url)
                self.results[url] = page_data
                
                # Añadir nuevas URLs a la cola
                for link in page_data.internal_links:
                    normalized_link = normalize_url(link.get("url", ""))
                    if (normalized_link and 
                        normalized_link not in self.visited_urls and 
                        normalized_link not in self.queue and 
                        len(self.visited_urls) + len(self.queue) < self.settings.max_pages):
                        self.queue.add(normalized_link)
            except Exception as e:
                print(f"Error al rastrear {url}: {str(e)}")
                # Registrar página con error
                self.results[url] = PageData(
                    url=url,
                    status_code=0,
                    issues=[{"type": "crawl_error", "severity": "critical", "description": str(e)}]
                )
    
    async def _fetch_and_process(self, url: str) -> PageData:
        """
        Obtiene y procesa una página
        
        Args:
            url: URL de la página a procesar
            
        Returns:
            Datos procesados de la página
        """
        try:
            async with self.session.get(url, timeout=self.settings.timeout) as response:
                content_type = response.headers.get("Content-Type", "")
                
                # Verificar si es HTML
                if "text/html" not in content_type.lower():
                    return PageData(
                        url=url,
                        status_code=response.status,
                        content_type=content_type,
                        indexable=False,
                        issues=[{
                            "type": "not_html", 
                            "severity": "notice", 
                            "description": f"No es una página HTML: {content_type}"
                        }]
                    )
                
                # Obtener contenido HTML
                html = await response.text()
                
                # Procesar HTML con BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extraer información básica
                title = self._extract_title(soup)
                meta_description = self._extract_meta_description(soup)
                h1_tags = self._extract_h1(soup)
                canonical = self._extract_canonical(soup)
                robots = self._extract_robots(soup)
                
                # Extraer enlaces
                internal_links, external_links = self._extract_links(soup, url)
                
                # Verificar si la página es indexable
                indexable = self._is_indexable(robots, canonical, url)
                
                # Realizar análisis básico SEO
                issues = self._analyze_seo(title, meta_description, h1_tags, internal_links, external_links)
                
                # Calcular puntuación de la página (implementación básica)
                page_score = 100 - (len(issues) * 5)  # Restar 5 puntos por cada problema
                
                return PageData(
                    url=url,
                    status_code=response.status,
                    title=title,
                    meta_description=meta_description,
                    h1=h1_tags,
                    canonical_url=canonical,
                    content_type=content_type,
                    size_bytes=len(html),
                    word_count=self._count_words(soup),
                    indexable=indexable,
                    page_score=max(0, page_score),
                    internal_links=internal_links,
                    external_links=external_links,
                    meta_robots=robots,
                    issues=issues
                )
                
        except asyncio.TimeoutError:
            return PageData(
                url=url,
                status_code=0,
                indexable=False,
                issues=[{
                    "type": "timeout", 
                    "severity": "critical", 
                    "description": f"Tiempo de espera agotado al intentar acceder a {url}"
                }]
            )
        except Exception as e:
            return PageData(
                url=url,
                status_code=0,
                indexable=False,
                issues=[{
                    "type": "fetch_error", 
                    "severity": "critical", 
                    "description": f"Error al obtener la página: {str(e)}"
                }]
            )
    
    # Métodos auxiliares para extracción y análisis
    
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
    
    def _extract_canonical(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae la URL canónica"""
        canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
        return canonical_tag.get('href', '').strip() if canonical_tag else None
    
    def _extract_robots(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae directivas de robots"""
        robots_tag = soup.find('meta', attrs={'name': 'robots'})
        return robots_tag.get('content', '').strip() if robots_tag else None
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> tuple:
        """Extrae enlaces internos y externos"""
        internal_links = []
        external_links = []
        
        for a in soup.find_all('a', href=True):
            href = a.get('href', '').strip()
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
                
            # Convertir enlaces relativos a absolutos
            full_url = urljoin(base_url, href)
            
            # Normalizar la URL
            full_url = normalize_url(full_url)
            
            link_data = {
                "url": full_url,
                "text": a.text.strip(),
                "nofollow": 'rel' in a.attrs and 'nofollow' in a.get('rel', '')
            }
            
            # Determinar si es interno o externo
            if is_internal_url(full_url, urlparse(base_url).netloc):
                internal_links.append(link_data)
            else:
                external_links.append(link_data)
                
        return internal_links, external_links
    
    def _count_words(self, soup: BeautifulSoup) -> int:
        """Cuenta palabras en el contenido principal"""
        # Eliminar scripts y estilos
        for script in soup(["script", "style"]):
            script.extract()
        
        text = soup.get_text()
        words = text.lower().split()
        return len(words)
    
    def _is_indexable(self, robots: Optional[str], canonical: Optional[str], url: str) -> bool:
        """Determina si una página es indexable"""
        # Comprobar directivas de robots
        if robots and ('noindex' in robots.lower()):
            return False
        
        # Comprobar si la URL canónica apunta a otra página
        if canonical and canonical != url and canonical != normalize_url(url):
            return False
            
        return True
    
    def _analyze_seo(self, title, meta_description, h1_tags, internal_links, external_links) -> List[Dict]:
        """Analiza problemas SEO básicos"""
        issues = []
        
        # Problemas de título
        if not title:
            issues.append({
                "type": "missing_title",
                "severity": "critical",
                "description": "La página no tiene una etiqueta de título"
            })
        elif len(title) < 10:
            issues.append({
                "type": "title_too_short",
                "severity": "warning",
                "description": "El título de la página es demasiado corto (menos de 10 caracteres)"
            })
        elif len(title) > 60:
            issues.append({
                "type": "title_too_long",
                "severity": "warning",
                "description": "El título de la página es demasiado largo (más de 60 caracteres)"
            })
            
        # Problemas de meta descripción
        if not meta_description:
            issues.append({
                "type": "missing_meta_description",
                "severity": "warning",
                "description": "La página no tiene meta descripción"
            })
        elif len(meta_description) < 50:
            issues.append({
                "type": "meta_description_too_short",
                "severity": "notice",
                "description": "La meta descripción es demasiado corta (menos de 50 caracteres)"
            })
        elif len(meta_description) > 160:
            issues.append({
                "type": "meta_description_too_long",
                "severity": "notice",
                "description": "La meta descripción es demasiado larga (más de 160 caracteres)"
            })
            
        # Problemas de encabezados
        if not h1_tags:
            issues.append({
                "type": "missing_h1",
                "severity": "warning",
                "description": "La página no tiene un encabezado H1"
            })
        elif len(h1_tags) > 1:
            issues.append({
                "type": "multiple_h1",
                "severity": "warning",
                "description": f"La página tiene múltiples encabezados H1 ({len(h1_tags)})"
            })
            
        return issues