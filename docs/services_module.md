# Módulo de Servicios - SEO Analyzer

Este documento describe el módulo de servicios implementado en la aplicación SEO Analyzer, el cual permite gestionar el catálogo de servicios de SEO y procesar solicitudes de usuarios.

## Índice

1. [Estructura del Módulo](#estructura-del-módulo)
2. [Modelos de Datos](#modelos-de-datos)
3. [Endpoints de la API](#endpoints-de-la-api)
4. [Casos de Uso Comunes](#casos-de-uso-comunes)
5. [Guía de Implementación Frontend](#guía-de-implementación-frontend)
6. [Permisos y Roles](#permisos-y-roles)
7. [Administración de Solicitudes](#administración-de-solicitudes)

## Estructura del Módulo

El módulo de servicios se compone de:

- **Modelos de Base de Datos**: Definen la estructura de categorías, servicios y solicitudes.
- **Esquemas Pydantic**: Para validación y serialización de datos.
- **Servicio**: Contiene la lógica de negocio para operaciones con servicios.
- **Endpoints API**: Exponen la funcionalidad a través de la API REST.
- **Scripts de Inicialización**: Para poblar inicialmente la base de datos con servicios.

## Modelos de Datos

### ServiceCategory

Representa una categoría de servicios:

```python
class ServiceCategory(Base):
    """Categoría de servicios disponibles"""
    __tablename__ = "service_category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    slug = Column(String(100), unique=True, nullable=False)
    icon = Column(String(100))
    is_active = Column(Boolean, default=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    services = relationship("Service", back_populates="category")
```

### Service

Representa un servicio individual:

```python
class Service(Base):
    """Servicio individual disponible para contratación"""
    __tablename__ = "service"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("service_category.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    detailed_description = Column(Text)
    benefits = Column(ARRAY(String), default=[])
    price = Column(Float)
    price_type = Column(String(20), default="fixed")  # fixed, hourly, monthly
    duration = Column(String(50))  # Estimación de duración
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    custom_fields = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    category = relationship("ServiceCategory", back_populates="services")
    requests = relationship("ServiceRequest", back_populates="service")
```

### ServiceRequest

Representa una solicitud de servicio por parte de un usuario:

```python
class ServiceRequest(Base):
    """Solicitud de servicio por parte de un usuario"""
    __tablename__ = "service_request"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("service.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=True)
    status = Column(String(20), default="pending")  # pending, approved, in_progress, completed, cancelled
    message = Column(Text)
    custom_fields = Column(JSON)  # Campos personalizados según el servicio
    admin_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    service = relationship("Service", back_populates="requests")
    user = relationship("User")
    project = relationship("Project")
```

## Endpoints de la API

El módulo expone los siguientes endpoints:

### Categorías

- `GET /services/categories`: Lista todas las categorías de servicios activas.
- `GET /services/categories/{category_id}`: Obtiene una categoría específica por ID.
- `GET /services/categories/slug/{slug}`: Obtiene una categoría por su slug.
- `POST /services/categories`: Crea una nueva categoría (admin).
- `PUT /services/categories/{category_id}`: Actualiza una categoría existente (admin).
- `DELETE /services/categories/{category_id}`: Elimina una categoría (admin).

### Servicios

- `GET /services/services`: Lista todos los servicios activos, opcionalmente filtrados por categoría.
- `GET /services/services/{service_id}`: Obtiene un servicio específico por ID.
- `GET /services/services/slug/{slug}`: Obtiene un servicio por su slug.
- `POST /services/services`: Crea un nuevo servicio (admin).
- `PUT /services/services/{service_id}`: Actualiza un servicio existente (admin).
- `DELETE /services/services/{service_id}`: Elimina un servicio (admin).

### Endpoints Públicos

- `GET /services/featured`: Lista servicios destacados (is_featured=True).
- `GET /services/categories/{category_slug}/services`: Lista servicios por slug de categoría.

### Solicitudes de Servicio

- `POST /services/requests`: Crea una nueva solicitud de servicio.
- `GET /services/requests`: Lista solicitudes del usuario actual (admin ve todas).
- `GET /services/requests/{request_id}`: Obtiene una solicitud específica.
- `PUT /services/requests/{request_id}`: Actualiza una solicitud (usuario: mensaje, admin: todo).

## Casos de Uso Comunes

### 1. Mostrar el catálogo de servicios

```javascript
// Frontend ejemplo (React)
async function fetchServiceCategories() {
  const response = await fetch('/api/v1/services/categories');
  const categories = await response.json();
  
  // Para cada categoría, cargar sus servicios
  categories.forEach(async category => {
    const servicesResponse = await fetch(`/api/v1/services/categories/${category.id}`);
    const categoryWithServices = await servicesResponse.json();
    // Renderizar categoría con sus servicios
  });
}
```

### 2. Solicitar un servicio

```javascript
// Frontend ejemplo (React)
async function requestService(serviceId, message, customFields, projectId = null) {
  const response = await fetch('/api/v1/services/requests', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      service_id: serviceId,
      message: message,
      custom_fields: customFields,
      project_id: projectId
    }),
  });
  
  if (response.ok) {
    // Mostrar mensaje de éxito
  } else {
    // Manejar error
  }
}
```

### 3. Ver solicitudes pendientes (Admin)

```javascript
// Frontend ejemplo (React)
async function fetchPendingRequests() {
  const response = await fetch('/api/v1/services/requests?status=pending');
  const pendingRequests = await response.json();
  
  // Renderizar listado de solicitudes pendientes
}
```

## Guía de Implementación Frontend

### Interfaz Principal de Servicios

La página principal de servicios debe mostrar:

1. Un panel lateral con las categorías de servicios.
2. Un listado de servicios de la categoría seleccionada.
3. Posiblemente servicios destacados en la parte superior.

Ejemplo de estructura:

```html
<div class="services-container">
  <aside class="services-sidebar">
    <h2>Categorías</h2>
    <ul class="category-list">
      <!-- Lista de categorías -->
      <li class="category-item"><a href="#link-building">Link Building</a></li>
      <li class="category-item"><a href="#keyword-research">Keyword Research</a></li>
      <!-- etc. -->
    </ul>
  </aside>
  
  <main class="services-content">
    <section class="featured-services">
      <h2>Servicios Destacados</h2>
      <!-- Carrusel o listado de servicios destacados -->
    </section>
    
    <section id="link-building" class="service-category">
      <h2>Link Building</h2>
      <div class="services-grid">
        <!-- Tarjetas de servicios -->
        <div class="service-card">
          <h3>Guest Posts</h3>
          <p>Obtención de enlaces desde sitios guest posts</p>
          <ul class="benefits-list">
            <li>Tráfico orgánico (500/mes garantizado)</li>
            <li>Enlaces dofollow (10+)</li>
          </ul>
          <div class="price">$499.00</div>
          <button class="request-button">Solicitar Servicio</button>
        </div>
        <!-- más servicios -->
      </div>
    </section>
    
    <!-- Repetir por cada categoría -->
  </main>
</div>
```

### Formulario de Solicitud

Cuando un usuario hace clic en "Solicitar Servicio", debe mostrarse un formulario que incluya:

1. Información del servicio seleccionado (nombre, descripción, precio).
2. Selector de proyecto (opcional).
3. Campo para mensaje.
4. Campos personalizados según el tipo de servicio.
5. Botón de envío.

## Permisos y Roles

El módulo de servicios implementa los siguientes permisos:

- **Usuarios no autenticados**: Pueden ver categorías y servicios públicos, pero no pueden solicitar servicios.
- **Usuarios autenticados**: Pueden ver todas las categorías y servicios activos, solicitar servicios y gestionar sus propias solicitudes.
- **Administradores**: Tienen acceso completo al módulo, pudiendo crear, actualizar y eliminar categorías y servicios, así como gestionar todas las solicitudes.

## Administración de Solicitudes

Las solicitudes de servicio pasan por los siguientes estados:

1. **pending**: Estado inicial cuando se crea la solicitud.
2. **approved**: La solicitud ha sido aprobada pero no ha comenzado.
3. **in_progress**: El servicio está en ejecución.
4. **completed**: El servicio ha sido completado.
5. **cancelled**: La solicitud ha sido cancelada.

Solo los administradores pueden cambiar el estado de una solicitud. Los usuarios normales pueden actualizar el mensaje y los campos personalizados mientras la solicitud esté en estado "pending".

### Flujo de Trabajo Recomendado

1. Usuario solicita un servicio (estado: pending).
2. Administrador revisa y aprueba la solicitud (estado: approved).
3. Administrador comienza a trabajar en el servicio (estado: in_progress).
4. Administrador completa el servicio (estado: completed).
5. Si es necesario, cualquier parte puede cancelar la solicitud (estado: cancelled).

Esta gestión puede integrarse con un sistema de notificaciones para informar a los usuarios sobre cambios de estado y permitir comunicación adicional.