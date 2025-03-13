import pytest
from fastapi.testclient import TestClient

def test_register_user(client):
    """
    Prueba el registro de un nuevo usuario.
    """
    user_data = {
        "email": "newuser@example.com",
        "password": "Password123",
        "first_name": "New",
        "last_name": "User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert "id" in data
    assert "password_hash" not in data

def test_register_user_duplicate_email(client, test_user):
    """
    Prueba el registro de un usuario con un email que ya existe.
    """
    user_data = {
        "email": test_user.email,  # Email que ya existe
        "password": "Password123",
        "first_name": "Another",
        "last_name": "User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 400
    assert "ya está registrado" in response.json()["detail"]

def test_login_user(client, test_user):
    """
    Prueba el inicio de sesión de un usuario.
    """
    login_data = {
        "username": test_user.email,
        "password": "password123"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user_invalid_password(client, test_user):
    """
    Prueba el inicio de sesión de un usuario con contraseña incorrecta.
    """
    login_data = {
        "username": test_user.email,
        "password": "wrong_password"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 401
    assert "Email o contraseña incorrectos" in response.json()["detail"]

def test_login_user_invalid_email(client):
    """
    Prueba el inicio de sesión con un email que no existe.
    """
    login_data = {
        "username": "nonexistent@example.com",
        "password": "password123"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 401
    assert "Email o contraseña incorrectos" in response.json()["detail"]

def test_get_current_user(client, user_token_headers):
    """
    Prueba obtener el usuario actual.
    """
    response = client.get("/api/v1/auth/me", headers=user_token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password_hash" not in data

def test_get_current_user_invalid_token(client):
    """
    Prueba obtener el usuario actual con un token inválido.
    """
    invalid_token_headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/auth/me", headers=invalid_token_headers)
    
    assert response.status_code == 401
    assert "No se pudieron validar las credenciales" in response.json()["detail"]

def test_test_token(client, user_token_headers):
    """
    Prueba el endpoint de prueba de token.
    """
    response = client.post("/api/v1/auth/test-token", headers=user_token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"