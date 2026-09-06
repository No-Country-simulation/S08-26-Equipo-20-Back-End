# ServiceFlow | Back-End | Base de Datos

Modelo de Datos para la gestión y almacenamiento de la información de ServiceFlow.

La base de datos centraliza las solicitudes, usuarios, equipos, categorías, prioridades, historial, comentarios, archivos, aprobaciones y SLA relacionados con la atención de cada solicitud.

## Tablas

### Roles

Define los roles disponibles dentro del sistema.

* `id`
* `name`

### Users

Almacena los usuarios del sistema.

* `id`
* `name`
* `email`
* `password_hash`
* `role_id`
* `team_id`
* `is_active`
* `must_change_password`
* `created_at`
* `updated_at`

### Teams

Representa los equipos responsables de atender solicitudes.

* `id`
* `name`
* `description`
* `created_at`
* `updated_at`

### Categories

Define las categorías de las solicitudes.

* `id`
* `name`
* `description`
* `requires_approval`

### Priorities

Define las prioridades disponibles.

* `id`
* `name`
* `level`

### Requests

Almacena las solicitudes realizadas dentro del sistema.

* `id`
* `description`
* `status`
* `category_id`
* `priority_id`
* `team_id`
* `created_by`
* `assigned_to`
* `created_at`
* `updated_at`
* `resolved_at`
* `closed_at`

### Request History

Registra los cambios realizados sobre una solicitud.

* `id`
* `request_id`
* `user_id`
* `action`
* `old_value`
* `new_value`
* `created_at`

### Comments

Almacena los comentarios asociados a una solicitud.

* `id`
* `request_id`
* `user_id`
* `content`
* `is_internal`
* `created_at`

### Attachments

Almacena los archivos asociados a una solicitud.

* `id`
* `request_id`
* `uploaded_by`
* `file_name`
* `file_path`
* `created_at`

### Approvals

Gestiona las aprobaciones requeridas por las solicitudes.

* `id`
* `request_id`
* `approver_id`
* `status`
* `comment`
* `created_at`
* `decided_at`

### SLAs

Almacena los tiempos asociados al SLA de cada solicitud.

* `id`
* `request_id`
* `response_deadline`
* `resolution_deadline`
* `responded_at`
* `resolved_at`
* `created_at`

## Relaciones

```text
roles
  └── users

teams
  ├── users
  └── requests

categories
  └── requests

priorities
  └── requests

users
  ├── requests
  ├── request_history
  ├── comments
  ├── attachments
  └── approvals

requests
  ├── request_history
  ├── comments
  ├── attachments
  ├── approvals
  └── slas
```

---

* Creación: 06/09/2026
* Última Actualización: 06/09/2026
