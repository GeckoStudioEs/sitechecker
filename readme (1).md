# SEO Analyzer

SEO Analyzer es una herramienta de análisis SEO similar a Sitechecker, desarrollada con Python y FastAPI. Permite auditar sitios web, monitorear cambios, rastrear posiciones de palabras clave, y mucho más.

## Características

- Auditoría completa de sitios web
- Monitoreo de cambios en el sitio
- Seguimiento de posiciones de palabras clave
- Integración con Google Search Console y Google Analytics
- Detección de problemas de SEO
- Informes personalizados
- API RESTful

## Requisitos

- Docker y Docker Compose
- Python 3.10+

## Instalación

### Usando Docker (recomendado)

1. Clona este repositorio:
   ```bash
   git clone https://github.com/yourusername/seo-analyzer.git
   cd seo-analyzer
   ```

2. Ejecuta el script de inicialización:
   ```bash
   chmod +x init.sh
   ./init.sh
   ```

3. Accede a la aplicación en http://localhost:8000

### Instalación manual

1. Clona este repositorio:
   ```bash
   git clone https://github.com/yourusername/seo-analyzer.git
   cd seo-analyzer
   ```

2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configura las variables de entorno:
   ```bash
   cp .env.example .env
   # Edita el archivo .env con tus configuraciones
   ```

4. Inicializa la base de datos:
   ```bash
   # Asegúrate de tener PostgreSQL instalado y funcionando
   alembic upgrade head
   ```

5. Ejecuta la aplicación:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Accede a la aplicación en http://localhost:8000

## Estructura del Proyecto

```
seo_analyzer/
├── app/                    # Código principal
│   ├── api/                # Endpoints de la API
│   ├── core/               # Configuración y utilidades core
│   ├── db/                 # Modelos y configuración de BD
│   ├── models/             # Modelos Pydantic
│   ├── schemas/            # Esquemas de datos
│   ├── services/           # Servicios de negocio
│   └── utils/              # Utilidades generales
├── alembic/                # Migraciones de base de datos
├── tests/                  # Pruebas
├── docker-compose.yml      # Configuración de Docker
└── Dockerfile              # Configuración de imagen Docker
```

## Uso

### Acceso a la API

La documentación de la API está disponible en:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Autenticación

1. Registra un nuevo usuario:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password123", "first_name": "John", "last_name": "Doe"}'
   ```

2. Obtén un token de acceso:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/form-data" \
     -d "username=user@example.com&password=password123"
   ```

### Gestión de Proyectos

1. Crear un nuevo proyecto:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/projects" \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json" \
     -d '{"name": "Mi Sitio Web", "domain": "example.com", "protocol": "https", "domain_scope": "domain"}'
   ```

2. Listar proyectos:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/projects" \
     -H "Authorization: Bearer {token}"
   ```

## Desarrollo

### Ejecutar pruebas

```bash
pytest
```

### Generar migraciones

```bash
alembic revision --autogenerate -m "descripción de los cambios"
```

### Aplicar migraciones

```bash
alembic upgrade head
```

## Contribución

1. Haz un fork del repositorio
2. Crea una rama para tu función: `git checkout -b feature/nueva-funcionalidad`
3. Realiza tus cambios y haz commit: `git commit -m 'Añadir nueva funcionalidad'`
4. Envía tus cambios: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

## Licencia

[MIT](LICENSE)
