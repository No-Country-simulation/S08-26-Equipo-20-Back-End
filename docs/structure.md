# ServiceFlow | Back-End | Estructura

Estructura del Back-End y distribución de responsabilidades dentro del proyecto.

## Arquitectura

ServiceFlow utiliza una arquitectura por capas:

```text
Router
  ↓
Service
  ↓
Repository
  ↓
Model
```

Cada capa mantiene una responsabilidad clara y evita concentrar diferentes responsabilidades en un mismo lugar.

## Routers

Los Routers gestionan la comunicación HTTP con la API.

Responsabilidades:

* Definir endpoints.
* Recibir solicitudes.
* Validar autenticación y autorización.
* Utilizar Schemas para los datos de entrada y salida.
* Llamar a los Services.
* Devolver las respuestas HTTP correspondientes.

Los Routers no deben contener lógica de negocio compleja.

## Schemas

Los Schemas definen los datos utilizados por la API.

Responsabilidades:

* Validar datos de entrada.
* Definir estructuras de respuesta.
* Serializar información.
* Mantener claros los contratos de la API.

Se utiliza Pydantic para su implementación.

## Services

Los Services contienen la lógica de negocio y los casos de uso del sistema.

Responsabilidades:

* Aplicar reglas de negocio.
* Coordinar operaciones.
* Validar condiciones necesarias para realizar una operación.
* Utilizar los Repositories para acceder a los datos.

Los Services no deben encargarse directamente de la comunicación HTTP.

## Repositories

Los Repositories gestionan el acceso a la base de datos.

Responsabilidades:

* Consultar datos.
* Crear registros.
* Actualizar registros.
* Eliminar o desactivar registros cuando corresponda.
* Ejecutar consultas específicas.

Los Repositories no deben contener reglas de negocio.

## Models

Los Models representan las entidades almacenadas en la base de datos.

Se utiliza SQLAlchemy para su implementación.

Los Models definen:

* Campos.
* Tipos de datos.
* Claves primarias.
* Claves foráneas.
* Relaciones entre entidades.

No deben contener workflows completos ni lógica de negocio compleja.

## Core

La capa `core` contiene componentes compartidos de la aplicación.

Puede incluir:

* Configuración.
* Seguridad.
* Autenticación.
* Manejo de dependencias.
* Componentes de infraestructura.

Los datos sensibles y configuraciones dependientes del entorno deben mantenerse fuera del código fuente.

## Migraciones

Las modificaciones de la estructura de la base de datos se gestionan mediante Alembic.

Las migraciones permiten mantener sincronizados los Models y la base de datos y conservar un historial de cambios.

## Principios

La estructura debe mantenerse simple y clara.

Se deben aplicar Clean Code y SOLID sin introducir abstracciones o patrones innecesarios.

Cada componente debe tener una responsabilidad clara y el código debe permanecer fácil de entender, probar y mantener.
