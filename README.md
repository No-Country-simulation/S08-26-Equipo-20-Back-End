# ServiceFlow | Back-End

API REST para la gestión centralizada de solicitudes internas de una organización.

ServiceFlow permite registrar, clasificar, priorizar, asignar y realizar el seguimiento de solicitudes internas, manteniendo la trazabilidad de cada operación y centralizando la información relacionada con su atención.

## Integrantes

* Matias Bertuccio — Software Engineer
* Alexis Albarenga — Software Engineer
* Linder Rodríguez — Software Engineer
* Andrés Uzeda — QA Engineer

## Tecnologías

Back-End:

![Python](https://img.shields.io/badge/Python-000000?style=flat-square&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-000000?style=flat-square&logo=fastapi&logoColor=white) ![Uvicorn](https://img.shields.io/badge/Uvicorn-000000?style=flat-square) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-000000?style=flat-square&logo=sqlalchemy&logoColor=white) ![Alembic](https://img.shields.io/badge/Alembic-000000?style=flat-square) ![Pydantic](https://img.shields.io/badge/Pydantic-000000?style=flat-square&logo=pydantic&logoColor=white)

Bases de Datos:

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-000000?style=flat-square&logo=postgresql&logoColor=white)

Tests:

![pytest](https://img.shields.io/badge/pytest-000000?style=flat-square&logo=pytest&logoColor=white) ![Playwright](https://img.shields.io/badge/Playwright-000000?style=flat-square)

Contenedores:

![Docker](https://img.shields.io/badge/Docker-000000?style=flat-square&logo=docker&logoColor=white) ![Docker Compose](https://img.shields.io/badge/Docker_Compose-000000?style=flat-square&logo=docker&logoColor=white)

Herramientas:

![Git](https://img.shields.io/badge/Git-000000?style=flat-square&logo=git&logoColor=white) ![GitHub](https://img.shields.io/badge/GitHub-000000?style=flat-square&logo=github&logoColor=white) ![Visual Studio Code](https://img.shields.io/badge/Visual_Studio_Code-000000?style=flat-square) ![OpenCode](https://img.shields.io/badge/OpenCode-000000?style=flat-square&logo=opencode&logoColor=white)

Las versiones exactas de cada dependencia se encuentran en `pyproject.toml`, `package.json` y los archivos de bloqueo de dependencias correspondientes.

## Arquitectura

El proyecto sigue una arquitectura por capas, con una responsabilidad clara en cada una.

```
Router → Service → Repository → Model
```

* `app/modules/*/router.py` — maneja HTTP y las validaciones de entrada
* `app/modules/*/service.py` — contiene la lógica de negocio
* `app/modules/*/repository.py` — gestiona el acceso a datos
* `app/modules/*/model.py` — representa las entidades de la base de datos
* `app/modules/*/schemas.py` — define los esquemas de entrada y salida con Pydantic
* `app/core/` — configuración, conexión a la base de datos, seguridad y dependencias

## Requisitos Previos

* Docker y Docker Compose, para el levantamiento mediante contenedores.
* Python 3.11 o superior y una instancia de PostgreSQL, para el levantamiento local.

## Instalación y Ejecución

La vía recomendada es mediante Docker Compose, que define tanto el servicio de API como el de base de datos en el archivo `docker-compose.yml`.

```bash
docker compose up --build
```

La API queda disponible en `http://localhost:8000`.

Los contenedores definen las siguientes credenciales por defecto para la base de datos:

* Host: `sf-back-db`
* Puerto: `5432` (expuesto en el host como `5434`)
* Base de datos: `serviceflow`
* Usuario: `serviceflow`
* Contraseña: `serviceflow`

Al iniciar, el script `entrypoint.sh` ejecuta automáticamente `alembic upgrade head` y luego levanta Uvicorn en modo `--reload`, con el directorio `app/` montado como volumen para el recargado automático del código.

Para detener los contenedores:

```bash
docker compose down
```

Para eliminar también el volumen de datos persistido:

```bash
docker compose down -v
```

### Ejecución Local

Instalar el proyecto y sus dependencias de desarrollo:

```bash
pip install -e ".[dev]"
```

Configurar las variables de entorno en un archivo `.env` en la raíz del repositorio (ver la sección siguiente).

Aplicar las migraciones:

```bash
alembic upgrade head
```

Levantar la API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Variables de Entorno

La configuración se lee desde un archivo `.env` en la raíz del repositorio. El archivo `.env.example` documenta todas las variables disponibles.

| Variable | Requerida | Default | Descripción |
| --- | --- | --- | --- |
| `DATABASE_URL` | Si | Ninguno | Cadena de conexión a PostgreSQL con driver asíncrono. Ejemplo: `postgresql+asyncpg://serviceflow:serviceflow@localhost:5434/serviceflow` |
| `JWT_SECRET` | Si | Ninguno | Clave usada para firmar los tokens JWT. Debe cambiarse en entornos productivos. |
| `JWT_ALGORITHM` | No | `HS256` | Algoritmo de firma de los tokens. |
| `JWT_EXPIRE_MINUTES` | No | `30` | Minutos de vigencia del token de acceso. |

El archivo `.env` no se versiona en el repositorio por contener información sensible.

## Base de Datos

* Motor: PostgreSQL 16
* ORM: SQLAlchemy 2.0 en modo asíncrono
* Driver: `asyncpg`
* Migraciones: Alembic

El motor y la sesión se configuran en `app/core/database.py`. El esquema de base de datos se administra exclusivamente mediante migraciones de Alembic.

## Migraciones

Aplicar todas las migraciones pendientes:

```bash
alembic upgrade head
```

Este comando se ejecuta automáticamente en el arranque del contenedor. Al ejecutar la API de forma local, debe aplicarse manualmente antes de iniciar el servidor.

## Seeds

El script `scripts/seed_data.py` siembra un conjunto determinista de datos de prueba que cubre todos los endpoints de la API, incluidos estados que la lógica de negocio no produce de forma natural, como aprobaciones pendientes en solicitudes cerradas, SLA incumplido y usuarios dados de baja.

```bash
python -m scripts.seed_data
```

Opciones disponibles:

* `--reset` — borra los datos sembrados previamente y vuelve a sembrar
* `--quiet` — omite el reporte formateado de salida

Los datos quedan persistentes en la base de datos, a diferencia de `scripts/test_e2e_flow.py`, que borra lo que crea al terminar.

Consideraciones:

* El script debe invocarse en modo módulo (`-m`). Ejecutarlo como `python scripts/seed_data.py` falla con `ModuleNotFoundError: No module named 'app'`.
* El `Dockerfile` no copia el directorio `scripts/` a la imagen. Para ejecutarlo dentro del contenedor hay que copiarlo primero:

```bash
docker cp scripts/seed_data.py sf-back-end:/app/seed_data.py
docker compose exec sf-back-end python seed_data.py --reset
```

Usuarios creados por el seed, todos con la contraseña `ServiceFlow123`:

| Email | Rol | Estado |
| --- | --- | --- |
| `admin@demo.serviceflow.dev` | ADMIN | Activo |
| `agente@demo.serviceflow.dev` | AGENT | Activo |
| `helpdesk@demo.serviceflow.dev` | AGENT | Activo |
| `usuario@demo.serviceflow.dev` | USER | Activo |
| `usuario2@demo.serviceflow.dev` | USER | Activo |
| `inactivo@demo.serviceflow.dev` | USER | Inactivo |

## API

La aplicación expone la documentación interactiva de FastAPI en las rutas `/docs` (Swagger UI) y `/redoc`.

### Módulos

| Prefijo | Descripción |
| --- | --- |
| `/auth` | Inicio de sesión, usuario autenticado y cambio de contraseña |
| `/users` | Gestión de usuarios |
| `/teams` | Gestión de equipos |
| `/categories` | Gestión de categorías |
| `/priorities` | Gestión de prioridades |
| `/requests` | Gestión de solicitudes, comentarios, historial, SLA y aprobaciones |
| `/customer/requests` | Portal de solicitudes para el usuario final |
| `/health` | Verificación del estado del servicio |
| `/uploads` | Archivos adjuntos almacenados |

El detalle completo de los endpoints, sus parámetros y sus respuestas se encuentra en `docs/api.md`.

## Autenticación

La API utiliza tokens JWT con esquema Bearer.

* Los tokens se firman con la clave `JWT_SECRET` y el algoritmo `JWT_ALGORITHM`.
* La vigencia por defecto es de `JWT_EXPIRE_MINUTES` minutos.
* Las contraseñas se almacenan hasheadas con Argon2, nunca en texto plano.
* El control de acceso se realiza por rol, con dependencias centralizadas en `app/core/dependencies.py`.
* Los roles definidos son `ADMIN`, `AGENT` y `USER`.

El flujo y los casos de error se detallan en `docs/auth.md`.

## Tests

El proyecto contiene dos frameworks de prueba independientes.

### Pruebas Unitarias y de Integración

Suite implementada con pytest y httpx, ubicada en el directorio `tests/`.

```bash
pytest
```

Detalle de la configuración:

* El modo asíncrono está habilitado mediante `asyncio_mode = "auto"` en `pyproject.toml`.
* Las pruebas utilizan la base de datos real configurada en `DATABASE_URL`. No hay una base de datos aislada ni sustitución de dependencias, por lo que es necesario que la base de datos esté accesible y migrada antes de ejecutarlas.
* Las pruebas crean y eliminan sus propios datos de prueba mediante los helpers definidos en `tests/conftest.py`.

### Pruebas E2E de API

Framework de automatización de pruebas de API implementado con Playwright y validación de esquemas AJV, ubicado en el directorio `PruebasAPI/`. Es un subproyecto Node con su propio `package.json` y su propio archivo de bloqueo de dependencias.

```bash
cd PruebasAPI
npm install
npm test
```

La suite se ejecuta de forma secuencial (`workers: 1`) para evitar condiciones de carrera en la base de datos, y requiere que el Back-End esté levantado y accesible.

Scripts disponibles:

| Script | Descripción |
| --- | --- |
| `npm test` | Ejecuta toda la suite |
| `npm run test:e2e` | Ejecuta únicamente las pruebas E2E de API |
| `npm run test:smoke` | Ejecuta las pruebas marcadas con `@smoke` |
| `npm run test:regression` | Ejecuta las pruebas marcadas con `@regression` |
| `npm run test:positive` | Ejecuta las pruebas marcadas con `@positive` |
| `npm run test:negative` | Ejecuta las pruebas marcadas con `@negative` |
| `npm run report` | Abre el reporte HTML de Playwright |
| `npm run allure:generate` | Genera el reporte de Allure |
| `npm run allure:serve` | Sirve el reporte de Allure |
| `npm run allure:open` | Abre el reporte de Allure ya generado |
| `npm run clean` | Elimina los artefactos de las pruebas |

La URL base de la API se define mediante la variable de entorno `BASE_URL`, con el valor por defecto `http://localhost:8000`:

```bash
BASE_URL=http://localhost:8000 npm test
```

Los casos de prueba están detallados en `PruebasAPI/CASOS_DE_PRUEBA_DETALLADOS.md`.

### Linter y Formatter

No se ha encontrado en el proyecto una configuración de linter o formatter para Python. El archivo `pyproject.toml` no declara herramientas como Ruff, Black, isort o mypy.

## Integración con Front-End

El Back-End se expone en el puerto `8000` y es el único componente que el Front-End necesita para funcionar.

* La aplicación se levanta en `http://localhost:8000`.
* El Front-End debe estar configurado con `NEXT_PUBLIC_API_URL=http://localhost:8000` para dirigir sus solicitudes a esta API.
* La configuración de CORS es permisiva, habilitando todos los orígenes, métodos y cabeceras. Esto permite que el Front-End, servido en un origen distinto como `http://localhost:3000`, acceda a la API sin configuración adicional. Al usar comodín en los orígenes junto con credenciales, el comportamiento puede variar según el cliente HTTP.
* La API expone `GET /health`, que responde `{"status":"ok"}`. Es el mecanismo de verificación de que el servicio está disponible y accesible desde el Front-End.
* La configuración CORS se define en `app/main.py`.

Los archivos adjuntos subidos por los usuarios se almacenan en el directorio `app/uploads/` y se sirven de forma estática desde la ruta `/uploads`.

## Documentación Adicional

* `docs/api.md` — documentación de los endpoints de la API
* `docs/auth.md` — flujo de autenticación, sesión y autorización
* `docs/business-rules.md` — reglas de negocio del dominio
* `docs/database.md` — modelo de datos y estructura de la base de datos
* `docs/structure.md` — arquitectura y estructura de carpetas
* `docs/testing.md` — estrategia de pruebas
* `PruebasAPI/README.md` — guía del framework de pruebas de API
* `PruebasAPI/CASOS_DE_PRUEBA_DETALLADOS.md` — detalle de los casos de prueba E2E

---

* Creación: 06/09/2026
* Última Actualización: 01/10/2026
