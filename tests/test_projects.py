import pytest
from fastapi.testclient import TestClient
from app.db.models import Project

def test_create_project(client, user_token_headers, db, test_user):
    """
    Prueba la creación de un nuevo proyecto.
    """
    project_data = {
        "name": "Test Project",
        "domain": "example.com",
        "protocol": "https",
        "domain_scope": "domain",
        "tags": ["test", "example"]
    }
    
    response = client.post("/api/v1/projects", json=project_data, headers=user_token_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == project_data["name"]
    assert data["domain"] == project_data["domain"]
    assert data["protocol"] == project_data["protocol"]
    assert data["domain_scope"] == project_data["domain_scope"]
    assert data["tags"] == project_data["tags"]
    assert data["owner_id"] == test_user.id
    assert data["is_active"] == True
    assert data["credits_balance"] == 100
    assert data["full_domain"] == "https://example.com"

def test_read_projects(client, user_token_headers, db, test_user):
    """
    Prueba obtener la lista de proyectos de un usuario.
    """
    # Crear algunos proyectos para el usuario
    for i in range(3):
        project = Project(
            name=f"Project {i+1}",
            domain=f"example{i+1}.com",
            protocol="https",
            domain_scope="domain",
            owner_id=test_user.id,
            is_active=True,
            tags=["test"]
        )
        db.add(project)
    
    db.commit()
    
    response = client.get("/api/v1/projects", headers=user_token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Verificar los nombres de los proyectos
    project_names = [p["name"] for p in data]
    assert "Project 1" in project_names
    assert "Project 2" in project_names
    assert "Project 3" in project_names

def test_read_project(client, user_token_headers, db, test_user):
    """
    Prueba obtener un proyecto específico por su ID.
    """
    # Crear un proyecto para el usuario
    project = Project(
        name="Test Project",
        domain="example.com",
        protocol="https",
        domain_scope="domain",
        owner_id=test_user.id,
        is_active=True,
        tags=["test"]
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    response = client.get(f"/api/v1/projects/{project.id}", headers=user_token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == project.name
    assert data["domain"] == project.domain
    assert data["protocol"] == project.protocol
    assert data["domain_scope"] == project.domain_scope
    assert data["owner_id"] == test_user.id
    assert data["is_active"] == True
    assert data["full_domain"] == "https://example.com"

def test_read_project_not_found(client, user_token_headers):
    """
    Prueba obtener un proyecto que no existe.
    """
    response = client.get("/api/v1/projects/999", headers=user_token_headers)
    
    assert response.status_code == 404
    assert "Proyecto no encontrado" in response.json()["detail"]

def test_update_project(client, user_token_headers, db, test_user):
    """
    Prueba actualizar un proyecto.
    """
    # Crear un proyecto para el usuario
    project = Project(
        name="Test Project",
        domain="example.com",
        protocol="https",
        domain_scope="domain",
        owner_id=test_user.id,
        is_active=True,
        tags=["test"]
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    update_data = {
        "name": "Updated Project",
        "tags": ["test", "updated"]
    }
    
    response = client.put(f"/api/v1/projects/{project.id}", json=update_data, headers=user_token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["tags"] == update_data["tags"]
    # Los otros campos no deberían cambiar
    assert data["domain"] == project.domain
    assert data["protocol"] == project.protocol
    assert data["domain_scope"] == project.domain_scope

def test_update_project_not_found(client, user_token_headers):
    """
    Prueba actualizar un proyecto que no existe.
    """
    update_data = {
        "name": "Updated Project"
    }
    
    response = client.put("/api/v1/projects/999", json=update_data, headers=user_token_headers)
    
    assert response.status_code == 404
    assert "Proyecto no encontrado" in response.json()["detail"]

def test_delete_project(client, user_token_headers, db, test_user):
    """
    Prueba eliminar un proyecto.
    """
    # Crear un proyecto para el usuario
    project = Project(
        name="Test Project",
        domain="example.com",
        protocol="https",
        domain_scope="domain",
        owner_id=test_user.id,
        is_active=True,
        tags=["test"]
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    response = client.delete(f"/api/v1/projects/{project.id}", headers=user_token_headers)
    
    assert response.status_code == 204
    
    # Verificar que el proyecto ha sido eliminado
    project_db = db.query(Project).filter(Project.id == project.id).first()
    assert project_db is None

def test_delete_project_not_found(client, user_token_headers):
    """
    Prueba eliminar un proyecto que no existe.
    """
    response = client.delete("/api/v1/projects/999", headers=user_token_headers)
    
    assert response.status_code == 404
    assert "Proyecto no encontrado" in response.json()["detail"]

def test_admin_can_see_all_projects(client, admin_token_headers, db, test_user):
    """
    Prueba que un administrador puede ver todos los proyectos.
    """
    # Crear algunos proyectos para un usuario normal
    for i in range(3):
        project = Project(
            name=f"User Project {i+1}",
            domain=f"example{i+1}.com",
            protocol="https",
            domain_scope="domain",
            owner_id=test_user.id,
            is_active=True,
            tags=["test"]
        )
        db.add(project)
    
    db.commit()
    
    response = client.get("/api/v1/projects", headers=admin_token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Verificar los nombres de los proyectos
    project_names = [p["name"] for p in data]
    assert "User Project 1" in project_names
    assert "User Project 2" in project_names
    assert "User Project 3" in project_names