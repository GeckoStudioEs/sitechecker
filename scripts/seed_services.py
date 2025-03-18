"""
Script para poblar la base de datos con datos iniciales de servicios
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.service_models import ServiceCategory, Service

def seed_services():
    """Crea categorías y servicios iniciales en la base de datos"""
    db = SessionLocal()
    try:
        # Verificar si ya existen categorías para evitar duplicación
        if db.query(ServiceCategory).count() > 0:
            print("Ya existen categorías en la base de datos. No se realizará la carga inicial.")
            return
        
        # Crear categorías
        categories = [
            {
                "name": "Link Building",
                "slug": "link-building",
                "description": "Servicios para mejorar el perfil de enlaces de tu sitio web",
                "icon": "link",
                "order": 1
            },
            {
                "name": "Keyword Research",
                "slug": "keyword-research",
                "description": "Investigación y análisis de palabras clave para tu estrategia SEO",
                "icon": "search",
                "order": 2
            },
            {
                "name": "Content Writing",
                "slug": "content-writing",
                "description": "Creación de contenido optimizado para SEO",
                "icon": "file-text",
                "order": 3
            },
            {
                "name": "Web Development",
                "slug": "web-development",
                "description": "Servicios de desarrollo web enfocados en SEO",
                "icon": "code",
                "order": 4
            },
            {
                "name": "Video Production",
                "slug": "video-production",
                "description": "Producción de videos explicativos y marketing",
                "icon": "video",
                "order": 5
            },
            {
                "name": "Website Analytics",
                "slug": "website-analytics",
                "description": "Configuración y análisis de datos de tu sitio web",
                "icon": "bar-chart",
                "order": 6
            },
            {
                "name": "SEO",
                "slug": "seo",
                "description": "Servicios generales de optimización para motores de búsqueda",
                "icon": "trending-up",
                "order": 7
            },
            {
                "name": "UX Research",
                "slug": "ux-research",
                "description": "Análisis y mejora de la experiencia de usuario",
                "icon": "users",
                "order": 8
            }
        ]
        
        # Insertar categorías y guardar referencias
        categories_db = {}
        for cat_data in categories:
            category = ServiceCategory(**cat_data)
            db.add(category)
            db.commit()
            db.refresh(category)
            categories_db[cat_data["slug"]] = category.id
            print(f"Creada categoría: {category.name} (ID: {category.id})")
        
        # Definir servicios
        services = [
            # Link Building
            {
                "category_slug": "link-building",
                "name": "Guest Posts",
                "slug": "guest-posts",
                "description": "Obtención de enlaces desde sitios guest posts",
                "benefits": ["Tráfico orgánico (500/mes garantizado)", "Enlaces dofollow (10+)"],
                "price": 499.00,
                "order": 1,
                "is_featured": True
            },
            {
                "category_slug": "link-building",
                "name": "Niche Edits",
                "slug": "niche-edits",
                "description": "Añadir enlaces desde sitios web nicho específicos",
                "benefits": ["Tráfico orgánico (200/mes garantizado)", "Enlaces dofollow (5+)"],
                "price": 299.00,
                "order": 2
            },
            {
                "category_slug": "link-building",
                "name": "Authority Links",
                "slug": "authority-links",
                "description": "Enlaces desde sitios con alta autoridad",
                "benefits": ["Tráfico orgánico específico (500/mes)", "Enlaces dofollow (5+)"],
                "price": 599.00,
                "order": 3,
                "is_featured": True
            },
            {
                "category_slug": "link-building",
                "name": "Homepage Links",
                "slug": "homepage-links",
                "description": "Enlaces desde páginas home con alta autoridad",
                "benefits": ["Tráfico orgánico (50+)", "Enlaces dofollow (5+)"],
                "price": 799.00,
                "order": 4
            },
            
            # Keyword Research
            {
                "category_slug": "keyword-research",
                "name": "Keyword Research",
                "slug": "keyword-research-service",
                "description": "Investigación de palabras clave completa",
                "benefits": ["Top 50 de oportunidades de búsqueda", "Análisis de intención, CPC y volumen"],
                "price": 399.00,
                "order": 1,
                "is_featured": True
            },
            {
                "category_slug": "keyword-research",
                "name": "Topical Map",
                "slug": "topical-map",
                "description": "Plan de contenido estructurado para sitio web",
                "benefits": ["Agrupación de palabras clave por temas", "Análisis de intención, CPC y volumen", "Recomendaciones basadas en pilares"],
                "price": 599.00,
                "order": 2
            },
            
            # Content Writing
            {
                "category_slug": "content-writing",
                "name": "Website Content",
                "slug": "website-content",
                "description": "Contenido escrito para sitio web o blog",
                "benefits": ["Artículos de 1000+ palabras", "Diferentes idiomas disponibles", "SEO optimizado"],
                "price": 0.15,  # precio por palabra
                "price_type": "per_word",
                "order": 1,
                "is_featured": True
            },
            
            # Web Development
            {
                "category_slug": "web-development",
                "name": "UI/UX Design",
                "slug": "ui-ux-design",
                "description": "Diseño de interfaces de usuario",
                "benefits": ["Wireframes, mockups y diseños finales", "Optimización para tráfico y conversiones", "Responsive"],
                "price": 1499.00,
                "order": 1
            },
            {
                "category_slug": "web-development",
                "name": "Web Development",
                "slug": "web-development-service",
                "description": "Desarrollo completo de sitios web",
                "benefits": ["Desarrollo de sitios desde cero", "SEO optimizado", "Integraciones y migraciones"],
                "price": 2999.00,
                "order": 2,
                "is_featured": True
            },
            {
                "category_slug": "web-development",
                "name": "Support and Refinements",
                "slug": "support-refinements",
                "description": "Soporte técnico para sitios existentes",
                "benefits": ["Fixing bugs y problemas SEO", "Parches de seguridad", "Implementaciones de protecciones"],
                "price": 79.00,
                "price_type": "hourly",
                "order": 3
            },
            
            # Video Production
            {
                "category_slug": "video-production",
                "name": "Product Explainer Video",
                "slug": "product-explainer-video",
                "description": "Videos explicativos de productos",
                "benefits": ["Videos de alta calidad", "Guión profesional", "Claro y conciso"],
                "price": 999.00,
                "order": 1
            },
            {
                "category_slug": "video-production",
                "name": "Blog to Video",
                "slug": "blog-to-video",
                "description": "Conversión de artículos a videos",
                "benefits": ["Creados por profesionales", "Diseño de imagen", "Múltiples formatos"],
                "price": 299.00,
                "order": 2
            },
            
            # Website Analytics
            {
                "category_slug": "website-analytics",
                "name": "Google Analytics + Starter Setup",
                "slug": "google-analytics-setup",
                "description": "Configuración inicial de analytics",
                "benefits": ["Google Tag Manager", "Google Analytics 4", "Eventos personalizados"],
                "price": 299.00,
                "order": 1
            },
            
            # SEO
            {
                "category_slug": "seo",
                "name": "SEO Consultation",
                "slug": "seo-consultation",
                "description": "Consultoría SEO personalizada",
                "benefits": ["Incremento de tráfico por búsqueda", "Mejora de conversiones", "Keywords mejor posicionadas"],
                "price": 199.00,
                "price_type": "hourly",
                "order": 1,
                "is_featured": True
            },
            
            # UX Research
            {
                "category_slug": "ux-research",
                "name": "UX Website Audit",
                "slug": "ux-website-audit",
                "description": "Auditoría de experiencia de usuario",
                "benefits": ["Identificación de problemas", "Oportunidades de mejora", "Recomendaciones"],
                "price": 599.00,
                "order": 1
            },
            {
                "category_slug": "ux-research",
                "name": "UX Content Audit",
                "slug": "ux-content-audit",
                "description": "Análisis de contenido para experiencia de usuario",
                "benefits": ["Revisión de contenido existente", "Recomendaciones estructurales", "Mejoras de contenido"],
                "price": 499.00,
                "order": 2
            },
            {
                "category_slug": "ux-research",
                "name": "UX Keyword & CRO Audit",
                "slug": "ux-keyword-cro-audit",
                "description": "Análisis para mejora de conversiones",
                "benefits": ["Análisis de intención de búsqueda", "Estrategias específicas de SEO/CRO", "Integración con Google Analytics"],
                "price": 799.00,
                "order": 3
            }
        ]
        
        # Insertar servicios
        for service_data in services:
            category_slug = service_data.pop("category_slug")
            category_id = categories_db.get(category_slug)
            
            if not category_id:
                print(f"Error: Categoría no encontrada para {service_data['name']}")
                continue
            
            service = Service(category_id=category_id, **service_data)
            db.add(service)
            db.commit()
            db.refresh(service)
            print(f"Creado servicio: {service.name} (ID: {service.id}, Categoría: {category_slug})")
        
        print("\nDatos iniciales creados exitosamente!")
    
    except Exception as e:
        print(f"Error al crear datos iniciales: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_services()