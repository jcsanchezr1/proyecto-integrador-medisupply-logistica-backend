# MediSupply Logistics Backend

Sistema de gestión de logística para MediSupply.

## Descripción

Este servicio se encarga de la gestión de logística en el sistema MediSupply.

## Estructura del Proyecto

```
proyecto-integrador-medisupply-logistica-backend/
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── database.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── base_controller.py
│   │   └── health_controller.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   └── db_models.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── base_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── base_service.py
│   ├── utils/
│   │   └── __init__.py
│   └── exceptions/
│       ├── __init__.py
│       └── custom_exceptions.py
├── tests/
├── .github/workflows/
├── app.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## Instalación

1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar variables de entorno (ver sección Variables de Entorno)
4. Ejecutar: `python app.py`

## Endpoints

### Health Check
- `GET /logistics/ping` - Verifica el estado del servicio
  - **Respuesta**: `"pong"`

## Base de Datos

El servicio utiliza PostgreSQL como base de datos. Las tablas se crean automáticamente al iniciar la aplicación.

## Desarrollo

El servicio corre en el puerto 8086 por defecto (mapeado desde el puerto interno 8080).

### Ejecutar Localmente
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export DATABASE_URL="postgresql://medisupply_local_user:medisupply_local_password@localhost:5432/medisupply_local_db"

# Ejecutar aplicación
python app.py
```

## Docker

### Construir Imagen
```bash
docker build -t medisupply-logistics-backend .
```

### Ejecutar Contenedor
```bash
docker run -p 8086:8080 \
  -e DATABASE_URL="postgresql://medisupply_local_user:medisupply_local_password@host.docker.internal:5432/medisupply_local_db" \
  medisupply-logistics-backend
```

## Testing

### Health Check
```bash
curl http://localhost:8086/logistics/ping
# Respuesta: "pong"
```
