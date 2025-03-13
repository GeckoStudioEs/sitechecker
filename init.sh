#!/bin/bash

set -e

# Colores para mensajes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Inicializando el proyecto SEO Analyzer ===${NC}"

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker no está instalado. Por favor, instálalo primero.${NC}"
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose no está instalado. Por favor, instálalo primero.${NC}"
    exit 1
fi

# Crear el archivo .env si no existe
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creando archivo .env con valores por defecto...${NC}"
    cp .env.example .env 2>/dev/null || echo -e "${YELLOW}No existe .env.example, creando .env desde cero...${NC}"
    cat > .env << EOF
# Entorno
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/seo_analyzer

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours

# Crawler Settings
USER_AGENT=SEOAnalyzer Bot (+https://example.com/bot)
RESPECT_ROBOTS_TXT=true
MAX_RETRIES=3
TIMEOUT=30
DELAY=0.5
MAX_PARALLEL_REQUESTS=5

# Email
EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USER=user@example.com
EMAIL_PASSWORD=password
FROM_EMAIL=noreply@example.com
USE_TLS=true

# API Keys (dejar vacías en desarrollo)
GOOGLE_API_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
EOF
    echo -e "${GREEN}Archivo .env creado correctamente.${NC}"
fi

# Construir los contenedores
echo -e "${BLUE}Construyendo los contenedores Docker...${NC}"
docker-compose build

# Iniciar los contenedores en segundo plano
echo -e "${BLUE}Iniciando los contenedores...${NC}"
docker-compose up -d

# Esperar a que la base de datos esté lista
echo -e "${YELLOW}Esperando a que la base de datos esté lista...${NC}"
sleep 5

# Ejecutar las migraciones de Alembic
echo -e "${BLUE}Ejecutando las migraciones de base de datos...${NC}"
docker-compose exec app alembic upgrade head

# Crear un usuario administrador si no existe
echo -e "${BLUE}Verificando si existe un usuario administrador...${NC}"
# Este comando ejecuta un script Python dentro del contenedor para crear un usuario admin
docker-compose exec app python -c "
from app.db.database import SessionLocal
from app.db.models import User
from app.core.security import get_password_hash
import datetime

db = SessionLocal()
admin = db.query(User).filter(User.email == 'admin@example.com').first()

if not admin:
    print('Creando usuario administrador...')
    admin_user = User(
        email='admin@example.com',
        password_hash=get_password_hash('admin123'),
        first_name='Admin',
        last_name='User',
        role='admin',
        is_active=True,
        created_at=datetime.datetime.utcnow()
    )
    db.add(admin_user)
    db.commit()
    print('Usuario administrador creado correctamente.')
else:
    print('El usuario administrador ya existe.')

db.close()
"

echo -e "${GREEN}Proyecto inicializado correctamente.${NC}"
echo -e "${GREEN}La API está disponible en: http://localhost:8000${NC}"
echo -e "${GREEN}La documentación está disponible en: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}Usuario administrador:${NC}"
echo -e "${YELLOW}  Email: admin@example.com${NC}"
echo -e "${YELLOW}  Contraseña: admin123${NC}"
echo -e "${RED}Por motivos de seguridad, cambie la contraseña del administrador después del primer inicio de sesión.${NC}"

# Mostrar los logs
echo -e "${BLUE}Mostrando logs (Ctrl+C para salir)...${NC}"
docker-compose logs -f app