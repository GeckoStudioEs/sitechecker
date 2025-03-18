import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db
from app.db.service_models import ServiceCategory, Service, ServiceRequest
from app.db.models import User
from app.core.security import get_password_hash
from app.api.deps import get_current_user, get_current_active_superuser

# Crear una base de datos en memoria para testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sobrescribir la dependencia para usar la base de datos de testing
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Crear usuario de prueba administrador
def get_test_admin_user():
    return User(
        id=1,
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        first_name="Admin",
        last_name="User",
        role="admin",
        is_active=True
    )

# Crear usuario de prueba normal
def get_test_normal_user():
    return User(
        id=2,
        email="user@example.com",
        password_hash=get_password_hash("user123"),
        first_name="Normal",
        last_name="User",
        role="user",
        is_active=True
    )

# Sobrescribir la dependencia para devolver el usuario de prueba
def override_get_current_user():
    return get_test_normal_user()

def override_get_current_admin_user():
    return get_test_admin_user()

# Configurar el cliente de prueba
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_current_active_superuser] = override_get_current_admin_user

client = TestClient(app)

@pytest.fixture(scope="function")
def init_test_db():
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear datos de prueba
    db = TestingSessionLocal()
    
    # Crear categorías de prueba
    categories = [
        ServiceCategory(
            id=1,
            name="Link Building",
            slug="link-building",
            description="Link building services",
            is_active=True
        ),
        ServiceCategory(
            id=2,
            name="Content Writing",
            slug="content-writing",
            description="Content writing services",
            is_active=True
        ),
        ServiceCategory(
            id=3,
            name="Inactive Category",
            slug="inactive-category",
            description="This category is inactive",
            is_active=False
        )
    ]
    
    db.add_all(categories)
    db.commit()
    
    # Crear servicios de prueba
    services = [
        Service(
            id=1,
            category_id=1,
            name="Guest Posts",
            slug="guest-posts",
            description="High quality guest posts",
            benefits=["Traffic boost", "Dofollow links"],
            price=199.99,
            is_active=True,
            is_featured=True
        ),
        Service(
            id=2,
            category_id=1,
            name="Niche Edits",
            slug="niche-edits",
            description="Niche edit links",
            benefits=["Contextual links", "High DA sites"],
            price=99.99,
            is_active=True,
            is_featured=False
        ),
        Service(
            id=3,
            category_id=2,
            name="Blog Content",
            slug="blog-content",
            description="SEO optimized blog content",
            benefits=["1000+ words", "SEO research"],
            price=0.10,
            price_type="per_word",
            is_active=True,
            is_featured=True
        ),
        Service(
            id=4,
            category_id=2,
            name="Inactive Service",
            slug="inactive-service",
            description="This service is inactive",
            benefits=["Test"],
            price=9.99,
            is_active=False
        )
    ]
    
    db.add_all(services)
    db.commit()
    
    # Crear usuarios de prueba
    admin_user = get_test_admin_user()
    normal_user = get_test_normal_user()
    
    db.add_all([admin_user, normal_user])
    db.commit()
    
    yield
    
    # Limpiar después de las pruebas
    db.close()
    Base.metadata.drop_all(bind=engine)

# Tests de la API de categorías
def test_read_categories(init_test_db):
    response = client.get("/api/v1/services/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2  # Al menos deberían estar las dos categorías activas
    assert any(category["slug"] == "link-building" for category in data)
    assert any(category["slug"] == "content-writing" for category in data)
    assert not any(category["slug"] == "inactive-category" for category in data)  # No debería haber categorías inactivas

def test_read_category_by_id(init_test_db):
    response = client.get("/api/v1/services/categories/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Link Building"
    assert data["slug"] == "link-building"
    assert len(data["services"]) == 2  # Debería tener 2 servicios

def test_read_category_by_slug(init_test_db):
    response = client.get("/api/v1/services/categories/slug/content-writing")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Content Writing"
    assert data["id"] == 2
    assert len(data["services"]) == 1  # Solo debe mostrar el servicio activo

def test_create_category(init_test_db):
    app.dependency_overrides[get_current_user] = override_get_current_admin_user  # Usar admin para esta prueba
    
    new_category = {
        "name": "Test Category",
        "slug": "test-category",
        "description": "Category created for testing",
        "is_active": True
    }
    
    response = client.post("/api/v1/services/categories", json=new_category)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Category"
    assert data["slug"] == "test-category"
    
    # Verificar que se puede recuperar la categoría creada
    response_get = client.get(f"/api/v1/services/categories/slug/{data['slug']}")
    assert response_get.status_code == 200
    
    app.dependency_overrides[get_current_user] = override_get_current_user  # Restaurar usuario normal

def test_update_category(init_test_db):
    app.dependency_overrides[get_current_user] = override_get_current_admin_user  # Usar admin para esta prueba
    
    update_data = {
        "name": "Updated Link Building",
        "description": "This description has been updated"
    }
    
    response = client.put("/api/v1/services/categories/1", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Link Building"
    assert data["description"] == "This description has been updated"
    assert data["slug"] == "link-building"  # El slug no debe cambiar
    
    app.dependency_overrides[get_current_user] = override_get_current_user  # Restaurar usuario normal

# Tests de la API de servicios
def test_read_services(init_test_db):
    response = client.get("/api/v1/services/services")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3  # Solo servicios activos
    assert any(service["slug"] == "guest-posts" for service in data)
    assert any(service["slug"] == "niche-edits" for service in data)
    assert any(service["slug"] == "blog-content" for service in data)
    assert not any(service["slug"] == "inactive-service" for service in data)

def test_read_services_by_category(init_test_db):
    response = client.get("/api/v1/services/services?category_id=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Solo servicios de Link Building
    assert all(service["category_id"] == 1 for service in data)

def test_read_service_by_id(init_test_db):
    response = client.get("/api/v1/services/services/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Guest Posts"
    assert data["slug"] == "guest-posts"
    assert data["category"]["name"] == "Link Building"

def test_read_service_by_slug(init_test_db):
    response = client.get("/api/v1/services/services/slug/blog-content")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Blog Content"
    assert data["id"] == 3
    assert data["price_type"] == "per_word"
    assert data["category"]["id"] == 2

def test_create_service(init_test_db):
    app.dependency_overrides[get_current_user] = override_get_current_admin_user  # Usar admin para esta prueba
    
    new_service = {
        "category_id": 1,
        "name": "Test Service",
        "slug": "test-service",
        "description": "Service created for testing",
        "benefits": ["Benefit 1", "Benefit 2"],
        "price": 149.99,
        "is_active": True
    }
    
    response = client.post("/api/v1/services/services", json=new_service)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Service"
    assert data["slug"] == "test-service"
    assert data["category_id"] == 1
    
    app.dependency_overrides[get_current_user] = override_get_current_user  # Restaurar usuario normal

def test_featured_services(init_test_db):
    response = client.get("/api/v1/services/featured")
    assert response.status_code == 200
    data = response.json()
    
    # Solo deben aparecer servicios con is_featured=True y is_active=True
    assert len(data) == 2
    featured_slugs = [service["slug"] for service in data]
    assert "guest-posts" in featured_slugs
    assert "blog-content" in featured_slugs
    assert "niche-edits" not in featured_slugs  # No es featured
    assert "inactive-service" not in featured_slugs  # No está activo

def test_services_by_category_slug(init_test_db):
    response = client.get("/api/v1/services/categories/link-building/services")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 2
    assert all(service["category_name"] == "Link Building" for service in data)
    service_slugs = [service["slug"] for service in data]
    assert "guest-posts" in service_slugs
    assert "niche-edits" in service_slugs

# Tests de la API de solicitudes de servicio
def test_create_service_request(init_test_db):
    new_request = {
        "service_id": 1,
        "message": "I'm interested in your guest posting service",
        "custom_fields": {"target_website": "example.com", "desired_anchor_text": "best seo tools"}
    }
    
    response = client.post("/api/v1/services/requests", json=new_request)
    assert response.status_code == 201
    data = response.json()
    assert data["service_id"] == 1
    assert data["user_id"] == 2  # El ID del usuario normal
    assert data["status"] == "pending"

def test_read_service_requests(init_test_db):
    # Primero crear una solicitud
    new_request = {
        "service_id": 2,
        "message": "I need niche edits",
        "custom_fields": {"websites": ["site1.com", "site2.com"]}
    }
    client.post("/api/v1/services/requests", json=new_request)
    
    # Obtener las solicitudes
    response = client.get("/api/v1/services/requests")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["service"]["name"] is not None
    assert data[0]["user_email"] == "user@example.com"

def test_update_service_request(init_test_db):
    # Primero crear una solicitud
    new_request = {
        "service_id": 3,
        "message": "I need blog content",
        "custom_fields": {"topic": "SEO tips"}
    }
    create_response = client.post("/api/v1/services/requests", json=new_request)
    request_id = create_response.json()["id"]
    
    # Actualizar la solicitud
    update_data = {
        "message": "I need blog content ASAP",
        "custom_fields": {"topic": "SEO tips", "urgency": "high"}
    }
    
    response = client.put(f"/api/v1/services/requests/{request_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "I need blog content ASAP"
    assert data["custom_fields"]["urgency"] == "high"
    assert data["status"] == "pending"  # No debe cambiar sin permisos de admin

def test_admin_update_service_request(init_test_db):
    app.dependency_overrides[get_current_user] = override_get_current_admin_user  # Usar admin para esta prueba
    
    # Primero crear una solicitud
    new_request = {
        "service_id": 1,
        "message": "Test admin request",
    }
    create_response = client.post("/api/v1/services/requests", json=new_request)
    request_id = create_response.json()["id"]
    
    # Actualizar la solicitud como admin
    update_data = {
        "status": "approved",
        "admin_notes": "Approved by admin"
    }
    
    response = client.put(f"/api/v1/services/requests/{request_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["admin_notes"] == "Approved by admin"
    
    app.dependency_overrides[get_current_user] = override_get_current_user  # Restaurar usuario normal