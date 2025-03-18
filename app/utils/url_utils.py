# app/utils/url_utils.py
import re
from urllib.parse import urlparse, urljoin, quote, unquote

def is_valid_url(url: str) -> bool:
    """
    Valida si una URL tiene formato correcto.
    
    Args:
        url: URL a validar
        
    Returns:
        True si la URL es válida, False en caso contrario
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def normalize_url(url: str) -> str:
    """
    Normaliza una URL para comparaciones consistentes.
    
    Args:
        url: URL a normalizar
        
    Returns:
        URL normalizada
    """
    if not url:
        return ""
        
    # Asegurar que la URL tenga protocolo
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Parsear la URL
    parsed = urlparse(url)
    
    # Normalizar componentes
    netloc = parsed.netloc.lower()
    
    # Eliminar www. si existe
    if netloc.startswith('www.'):
        netloc = netloc[4:]
    
    # Normalizar path
    path = parsed.path
    
    # Eliminar trailing slash si no es la única cosa en el path
    if path != '/' and path.endswith('/'):
        path = path[:-1]
    
    # Si no hay path, usar "/"
    if not path:
        path = '/'
    
    # Reconstruir URL sin parámetros, fragmentos o credenciales
    normalized = f"{parsed.scheme}://{netloc}{path}"
    
    return normalized

def get_domain(url: str) -> str:
    """
    Extrae el dominio de una URL.
    
    Args:
        url: URL de la que extraer el dominio
        
    Returns:
        Dominio de la URL
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Quitar el www. si existe
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return domain
    except:
        return ""

def is_internal_url(url: str, base_domain: str) -> bool:
    """
    Determina si una URL es interna al dominio base.
    
    Args:
        url: URL a comprobar
        base_domain: Dominio base
        
    Returns:
        True si la URL es interna, False en caso contrario
    """
    if not url or not base_domain:
        return False
        
    # Si es una URL relativa, es interna
    if not url.startswith(('http://', 'https://')):
        return True
    
    url_domain = get_domain(url)
    
    # Comprobar si el dominio de la URL es igual o subdominio del dominio base
    return url_domain == base_domain or url_domain.endswith('.' + base_domain)

def get_url_path(url: str) -> str:
    """
    Obtiene solo la parte del path de una URL.
    
    Args:
        url: URL de la que extraer el path
        
    Returns:
        Path de la URL
    """
    try:
        parsed = urlparse(url)
        return parsed.path
    except:
        return ""

def join_url(base: str, path: str) -> str:
    """
    Une una URL base con un path de forma segura.
    
    Args:
        base: URL base
        path: Path a añadir
        
    Returns:
        URL completa
    """
    return urljoin(base, path)

def encode_url(url: str) -> str:
    """
    Codifica correctamente una URL para su uso en parámetros.
    
    Args:
        url: URL a codificar
        
    Returns:
        URL codificada
    """
    return quote(url, safe='')

def decode_url(encoded_url: str) -> str:
    """
    Decodifica una URL codificada.
    
    Args:
        encoded_url: URL codificada
        
    Returns:
        URL decodificada
    """
    return unquote(encoded_url)

def extract_domain_from_url(url: str) -> str:
    """
    Extrae el dominio de una URL (alias de get_domain para compatibilidad).
    
    Args:
        url: URL de la que extraer el dominio
        
    Returns:
        Dominio de la URL
    """
    return get_domain(url)

def get_tld(url: str) -> str:
    """
    Obtiene el dominio de nivel superior (TLD) de una URL.
    
    Args:
        url: URL de la que extraer el TLD
        
    Returns:
        TLD de la URL
    """
    domain = get_domain(url)
    
    # Dividir el dominio por puntos y tomar el último elemento
    parts = domain.split('.')
    
    if len(parts) > 1:
        return parts[-1]
    
    return ""

def get_subdomain(url: str) -> str:
    """
    Obtiene el subdominio de una URL.
    
    Args:
        url: URL de la que extraer el subdominio
        
    Returns:
        Subdominio de la URL, o cadena vacía si no tiene
    """
    domain = get_domain(url)
    
    # Dividir el dominio por puntos
    parts = domain.split('.')
    
    # Si hay más de 2 partes, las primeras son el subdominio
    if len(parts) > 2:
        return '.'.join(parts[:-2])
    
    return ""

def is_relative_url(url: str) -> bool:
    """
    Determina si una URL es relativa.
    
    Args:
        url: URL a comprobar
        
    Returns:
        True si la URL es relativa, False en caso contrario
    """
    return not bool(urlparse(url).netloc)

def is_valid_domain(domain: str) -> bool:
    """
    Valida si un string es un nombre de dominio válido.
    
    Args:
        domain: Dominio a validar
        
    Returns:
        True si el dominio es válido, False en caso contrario
    """
    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return bool(re.match(pattern, domain))

def clean_query_params(url: str) -> str:
    """
    Limpia los parámetros de consulta de una URL.
    
    Args:
        url: URL a limpiar
        
    Returns:
        URL sin parámetros de consulta
    """
    try:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    except:
        return url

def get_url_fragments(url: str) -> dict:
    """
    Descompone una URL en sus componentes.
    
    Args:
        url: URL a descomponer
        
    Returns:
        Diccionario con los componentes de la URL
    """
    parsed = urlparse(url)
    return {
        "scheme": parsed.scheme,
        "netloc": parsed.netloc,
        "path": parsed.path,
        "params": parsed.params,
        "query": parsed.query,
        "fragment": parsed.fragment
    }

def clean_url_parameters(url: str) -> str:
    """
    Elimina parámetros de consulta y fragmentos de una URL (alias de clean_query_params).
    
    Args:
        url: URL a limpiar
        
    Returns:
        URL sin parámetros ni fragmentos
    """
    return clean_query_params(url)