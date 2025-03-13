import re
from typing import Any, Dict, List, Union, Optional

def is_valid_email(email: str) -> bool:
    """
    Valida si un string es un email bien formado.
    
    Args:
        email: Email a validar
        
    Returns:
        True si el email es válido, False en caso contrario
    """
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))

def validate_required_fields(data: Dict, required_fields: List[str]) -> List[str]:
    """
    Valida que un diccionario tenga todos los campos requeridos.
    
    Args:
        data: Diccionario a validar
        required_fields: Lista de campos requeridos
        
    Returns:
        Lista de campos faltantes
    """
    missing = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing.append(field)
    return missing

def sanitize_html(html: str) -> str:
    """
    Limpia HTML de tags peligrosos.
    Implementación básica - en producción usar una biblioteca completa.
    
    Args:
        html: HTML a limpiar
        
    Returns:
        HTML limpio
    """
    # Eliminar scripts
    html = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL)
    
    # Eliminar eventos on*
    html = re.sub(r' on\w+=".*?"', '', html)
    
    # Eliminar iframes
    html = re.sub(r'<iframe.*?>.*?</iframe>', '', html, flags=re.DOTALL)
    
    # Eliminar objetos
    html = re.sub(r'<object.*?>.*?</object>', '', html, flags=re.DOTALL)
    
    return html

def validate_int_range(value: Any, min_val: int = None, max_val: int = None) -> bool:
    """
    Valida que un valor sea un entero dentro de un rango.
    
    Args:
        value: Valor a validar
        min_val: Valor mínimo (opcional)
        max_val: Valor máximo (opcional)
        
    Returns:
        True si el valor es válido, False en caso contrario
    """
    try:
        val = int(value)
        if min_val is not None and val < min_val:
            return False
        if max_val is not None and val > max_val:
            return False
        return True
    except:
        return False

def validate_string_length(value: str, min_len: int = None, max_len: int = None) -> bool:
    """
    Valida que un string tenga una longitud dentro de un rango.
    
    Args:
        value: String a validar
        min_len: Longitud mínima (opcional)
        max_len: Longitud máxima (opcional)
        
    Returns:
        True si el string es válido, False en caso contrario
    """
    if not isinstance(value, str):
        return False
        
    if min_len is not None and len(value) < min_len:
        return False
        
    if max_len is not None and len(value) > max_len:
        return False
        
    return True

def safe_cast(val: Any, to_type: type, default: Any = None) -> Any:
    """
    Convierte de forma segura un valor a otro tipo.
    
    Args:
        val: Valor a convertir
        to_type: Tipo al que convertir
        default: Valor por defecto si la conversión falla
        
    Returns:
        Valor convertido o valor por defecto
    """
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

def validate_password_strength(password: str, min_length: int = 8) -> Dict[str, bool]:
    """
    Valida la fortaleza de una contraseña.
    
    Args:
        password: Contraseña a validar
        min_length: Longitud mínima requerida
        
    Returns:
        Diccionario con los resultados de las validaciones
    """
    results = {
        "length": len(password) >= min_length,
        "lowercase": bool(re.search(r'[a-z]', password)),
        "uppercase": bool(re.search(r'[A-Z]', password)),
        "digit": bool(re.search(r'\d', password)),
        "special": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    }
    
    results["valid"] = all(results.values())
    
    return results

def validate_date_format(date_string: str, format_string: str = "%Y-%m-%d") -> bool:
    """
    Valida que un string tenga un formato de fecha válido.
    
    Args:
        date_string: String a validar
        format_string: Formato esperado (%Y-%m-%d por defecto)
        
    Returns:
        True si el string tiene un formato de fecha válido, False en caso contrario
    """
    from datetime import datetime
    
    try:
        datetime.strptime(date_string, format_string)
        return True
    except ValueError:
        return False

def is_valid_ip(ip: str) -> bool:
    """
    Valida si un string es una dirección IP válida.
    
    Args:
        ip: IP a validar
        
    Returns:
        True si la IP es válida, False en caso contrario
    """
    # Patrón para validar IPv4
    ipv4_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})
    ipv4_match = re.match(ipv4_pattern, ip)
    
    if ipv4_match:
        # Verificar que cada octeto esté en el rango 0-255
        for i in range(1, 5):
            octet = int(ipv4_match.group(i))
            if octet < 0 or octet > 255:
                return False
        return True
    
    # Patrón para validar IPv6 (simplificado)
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}
    if re.match(ipv6_pattern, ip):
        return True
    
    return False

def validate_url_scheme(url: str, allowed_schemes: List[str] = ["http", "https"]) -> bool:
    """
    Valida que una URL use un esquema permitido.
    
    Args:
        url: URL a validar
        allowed_schemes: Lista de esquemas permitidos
        
    Returns:
        True si la URL usa un esquema permitido, False en caso contrario
    """
    from urllib.parse import urlparse
    
    try:
        parsed = urlparse(url)
        return parsed.scheme in allowed_schemes
    except:
        return False

def validate_domain_name(domain: str) -> bool:
    """
    Valida que un string sea un nombre de dominio válido.
    
    Args:
        domain: Dominio a validar
        
    Returns:
        True si el dominio es válido, False en caso contrario
    """
    # Patrón para validar nombres de dominio
    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}
    return bool(re.match(pattern, domain))

def is_valid_json(json_str: str) -> bool:
    """
    Valida que un string sea un JSON válido.
    
    Args:
        json_str: String a validar
        
    Returns:
        True si el string es un JSON válido, False en caso contrario
    """
    import json
    
    try:
        json.loads(json_str)
        return True
    except ValueError:
        return False

def is_valid_xml(xml_str: str) -> bool:
    """
    Valida que un string sea un XML válido.
    
    Args:
        xml_str: String a validar
        
    Returns:
        True si el string es un XML válido, False en caso contrario
    """
    import xml.etree.ElementTree as ET
    
    try:
        ET.fromstring(xml_str)
        return True
    except ET.ParseError:
        return False