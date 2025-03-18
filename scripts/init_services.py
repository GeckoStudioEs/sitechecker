#!/usr/bin/env python
"""
Script de inicialización para el módulo de servicios del SEO Analyzer.
Este script realiza:
1. Creación de tablas en la base de datos
2. Carga de datos iniciales de categorías y servicios
3. Creación de enlaces necesarios para la integración del módulo
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path para importación relativa
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config

from app.db.database import Base, engine
from app.db.service_models import ServiceCategory, Service, ServiceRequest
from app.core.config import settings
from scripts.seed_services import seed_services

async def init_services():
    """Inicializa el módulo de servicios"""
    
    print("=" * 60)
    print("Inicializando módulo de servicios para SEO Analyzer")
    print("=" * 60)
    
    try:
        # 1. Crear tablas en la base de datos
        print("\n[1/3] Creando tablas en la base de datos...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas correctamente")
        
        # 2. Cargar datos iniciales
        print("\n[2/3] Cargando datos iniciales de servicios...")
        seed_services()
        print("✅ Datos iniciales cargados correctamente")
        
        # 3. Integrar el módulo en la aplicación
        print("\n[3/3] Verificando integración del módulo...")
        
        # Comprobar que los archivos principales existen
        required_files = [
            "app/db/service_models.py",
            "app/schemas/services.py",
            "app/services/services/service_service.py",
            "app/api/endpoints/services.py"
        ]
        
        for file_path in required_files:
            if not os.path.exists(os.path.join(root_dir, file_path)):
                print(f"❌ No se encontró el archivo: {file_path}")
                return False
        
        # Comprobar que el router está incluido en api.py
        api_file = os.path.join(root_dir, "app/api/api.py")
        with open(api_file, "r") as f:
            content = f.read()
            if "import services" not in content or "api_router.include_router(services.router" not in content:
                print("⚠️ El router de servicios no está incluido en api.py")
                print("Por favor, añade las siguientes líneas en app/api/api.py:")
                print("   from app.api.endpoints import services")
                print("   api_router.include_router(services.router, prefix=\"/services\", tags=[\"services\"])")
            else:
                print("✅ Router de servicios correctamente integrado")
        
        print("\n" + "=" * 60)
        print("🚀 Módulo de servicios inicializado correctamente!")
        print("=" * 60)
        print("\nPara verificar la instalación, accede a: http://localhost:8000/api/v1/services/categories")
        
    except Exception as e:
        print(f"\n❌ Error durante la inicialización: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(init_services())