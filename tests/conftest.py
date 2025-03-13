import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.models import User

# Crear un motor de base de datos para pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """
    Crea una base de datos de prueba para cada prueba.
    """
    # Crear las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear una sesión
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Eliminar las tablas después de cada prueba
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    """
    Crea un cliente de prueba con una base de datos de prueba.
    """
    # Sobrescribir la dependencia get_db para usar la base de datos de prueba
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Limpiar el override
    app.dependency_overrides = {}

@pytest.fixture
def test_user(db):
    """
    Crea un usuario de prueba.
    """
    user_data = {
        "email": "test@example.com",
        "password_hash": get_password_hash("password123"),
        "first_name": "Test",
        "last_name": "User",
        "role": "user",
        "is_active": True
    }
    
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@pytest.fixture
def test_admin(db):
    """
    Crea un usuario administrador de prueba.
    """
    admin_data = {
        "email": "admin@example.com",
        "password_hash": get_password_hash("admin123"),
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
        "is_active": True
    }
    
    admin = User(**admin_data)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    return admin

@pytest.fixture
def user_token_headers(client, test_user):
    """
    Crea un token para el usuario de prueba y devuelve las cabeceras con el token.
    """
    login_data = {
        "username": test_user.email,
        "password": "password123"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_token_headers(client, test_admin):
    """
    Crea un token para el administrador de prueba y devuelve las cabeceras con el token.
    """
    login_data = {
        "username": test_admin.email,
        "password": "admin123"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}