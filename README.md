# API REST básica con FastAPI y MySQL

API REST base construida con FastAPI y MySQL. Proporciona la conexión con una base de datos MySQL. Expone un endpoint `health` para verificar el estado de la API y un endpoint raíz `/` que devuelve un mensaje de bienvenida con enlaces HATEOAS a los recursos disponibles. 

## Arquitectura

```mermaid
flowchart LR

fastapi["🐍 FastAPI (8000)<br/>Uvicorn"]
mysql["🗄️ MySQL 8"]

fastapi -->|SQL| mysql
```

Dos servicios Docker:
| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| `mysql`  | 3306   | Base de datos MySQL 8.0 con persistencia local |
| `python` | 8000   | API FastAPI + Uvicorn |

## Estructura del proyecto

```
api/
├── main.py              # Punto de entrada FastAPI
├── database.py          # Pool de conexiones MySQL
└── routes/
    └──  base.py          # GET / y GET /health
setup-environment/
├── docker-compose.yml
├── .env.example          # Ejemplo de variables de entorno
├── Dockerfile           # Imagen para la API
├── requirements.txt     # Dependencias de la API
data/
└── mysql-data/          # Volumen local MySQL (persistencia)
```

## Endpoints de la API

### Base
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Bienvenida con enlaces HATEOAS |
| GET | `/health` | Health check |
| GET | `/docs` | Documentación Swagger UI |
| GET | `/redoc` | Documentación ReDoc |

## Puesta en marcha

### Requisitos previos
- Docker y Docker Compose

### 1. Variables de entorno

Crea el archivo `setup-environment/.env` (toma como base `setup-environment/.env.example`):

```env
MYSQL_ROOT_PASSWORD=<your-root-password>
MYSQL_DATABASE=<your-database-name>
MYSQL_USER=<your-username>
MYSQL_PASSWORD=<your-password>
```

### 2. Arrancar los servicios

```bash
cd setup-environment
docker-compose up --build -d
```

### 3. Verificar estado

```bash
docker-compose ps
docker-compose logs -f python   # logs de la API
```

**NOTA**

> Puedes usar Docker Desktop para gestionar los contenedores y volúmenes de forma visual.
> 
> El contenedor `python` contiene un servidor Uvicorn en modo de desarrollo, por lo que se reiniciará automáticamente al detectar cambios en el código fuente. Esto facilita el desarrollo iterativo sin necesidad de reconstruir la imagen cada vez.

### 4. Acceder a los servicios

| Servicio | URL |
|----------|-----|
| API | http://localhost:8000 |
| Documentación Swagger | http://localhost:8000/docs |
| Documentación ReDoc | http://localhost:8000/redoc |

## Comandos útiles

```bash
# Parar servicios
docker-compose down

# Reiniciar solo la API
docker-compose restart python

# Entrar al contenedor de la API
docker exec -it $(docker-compose ps -q python) /bin/sh

# Acceder a MySQL
docker exec -it mysql mysql -u root -p
```

## Dependencias principales

**API** (`requirements.txt`):
- `fastapi` — framework web
- `uvicorn` — servidor ASGI
- `mysql-connector-python` — driver MySQL
- `dotenv` — carga de variables de entorno
- `pydantic` — validación de datos
- `pytz` — manejo de zonas horarias
- 
## 🛠️ Endpoints Implementados y Ejemplos de Uso
A continuación se detallan los endpoints implementados, junto con ejemplos de peticiones y respuestas para cada uno.

### 1. Obtener todos los libros
- **Endpoint:** `GET /books`
- **Descripción:** Devuelve una lista en formato JSON de todos los libros disponibles en la base de datos.
- **Ejemplo de Petición:**
  ```http
  GET /books/
  ```
- **Ejemplo de Respuesta (200 OK):**
  ```json
  [
    {
      "id": 1,
      "title": "El Quijote",
      "author": "Miguel de Cervantes",
      "publisher": "Editorial A",
      "year": 1605,
      "category": "Ficción"
    }
  ]
  ```

### 2. Crear un nuevo libro
- **Endpoint:** `POST /books`
- **Descripción:** Inserta un nuevo libro en la base de datos.
- **Ejemplo de Petición (Body JSON):**
  ```json
  {
    "title": "Dune",
    "author": "Frank Herbert",
    "publisher": "Acervo",
    "year": 1965,
    "category": "Ciencia"
  }
  ```
- **Ejemplo de Respuesta (201 Created):**
  ```json
  {
    "title": "Dune",
    "author": "Frank Herbert",
    "publisher": "Acervo",
    "year": 1965,
    "category": "Ciencia",
    "id": 11
  }
  ```

### 3. Obtener un libro por ID
- **Endpoint:** `GET /books/{id}`
- **Descripción:** Devuelve los detalles de un libro específico según su identificador único.
- **Ejemplo de Petición:**
  ```http
  GET /books/11
  ```
- **Ejemplo de Respuesta (200 OK):**
  ```json
  {
    "id": 11,
    "title": "Dune",
    "author": "Frank Herbert",
    "publisher": "Acervo",
    "year": 1965,
    "category": "Ciencia"
  }
  ```

### 4. Actualizar un libro
- **Endpoint:** `PUT /books/{id}`
- **Descripción:** Actualiza parcial o totalmente los campos de un libro existente.
- **Ejemplo de Petición (Body JSON con los campos a modificar):**
  ```json
  {
    "year": 2024
  }
  ```
- **Ejemplo de Respuesta (200 OK):**
  ```json
  {
    "message": "Libro actualizado correctamente"
  }
  ```

### 5. Eliminar un libro
- **Endpoint:** `DELETE /books/{id}`
- **Descripción:** Elimina físicamente el registro de un libro mediante su ID, siempre que no viole restricciones de integridad (ej. si tiene ejemplares asociados).
- **Ejemplo de Petición:**
  ```http
  DELETE /books/11
  ```
- **Ejemplo de Respuesta:** `204 No Content` *(Sin cuerpo en la respuesta)*

### 6. Realizar un préstamo
- **Endpoint:** `POST /loans`
- **Descripción:** Inicia el préstamo de un ejemplar a un usuario. Invoca al procedimiento almacenado `RealizarPrestamo` que verifica disponibilidad y posibles sanciones.
- **Ejemplo de Petición (Body JSON):**
  ```json
  {
    "userId": 1,
    "inventoryNumber": "INV005"
  }
  ```
- **Ejemplo de Respuesta (201 Created / 200 OK):**
  ```json
  {
    "message": "Préstamo realizado con éxito"
  }
  ```

### 7. Devolver un préstamo
- **Endpoint:** `POST /loans/return`
- **Descripción:** Registra la devolución de un ejemplar previamente prestado invocando al procedimiento almacenado `DevolverLibro`. Este procedimiento evalúa si el usuario ha excedido el tiempo y le aplica sanciones si corresponde.
- **Ejemplo de Petición (Body JSON):**
  ```json
  {
    "userId": 1,
    "inventoryNumber": "INV005"
  }
  ```
- **Ejemplo de Respuesta (200 OK):**
  ```json
  {
    "message": "Devolución realizada con éxito"
  }
  ```
  
## Licencia

Este proyecto está licenciado bajo la Licencia CC BY-NC-ND 4.0. Esto significa que puedes compartir el proyecto siempre que cites al autor, no lo uses para fines comerciales y no realices obras derivadas.
