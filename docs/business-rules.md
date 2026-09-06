# ServiceFlow | Back-End | Reglas de Negocio

Reglas que definen el comportamiento funcional de ServiceFlow y las condiciones que deben cumplirse durante la gestión de solicitudes.

## Roles

ServiceFlow cuenta con tres roles:

* `ADMIN`: administra usuarios, equipos, categorías, prioridades y configuración del sistema.
* `AGENT`: gestiona y atiende solicitudes asignadas a su equipo.
* `USER`: crea y realiza el seguimiento de sus propias solicitudes.

El rol determina las acciones que puede realizar un usuario dentro del sistema.

## Usuarios

* Cada usuario debe tener un email único.
* Un usuario puede pertenecer a un equipo.
* Un usuario puede estar activo o inactivo.
* Los usuarios inactivos no pueden iniciar sesión.
* Un usuario no puede desactivarse a sí mismo si tiene rol `ADMIN`.
* No se puede desactivar al último administrador activo del sistema.
* Los usuarios se eliminan de forma lógica para conservar la trazabilidad de sus operaciones.

## Equipos

* Un equipo agrupa usuarios que participan en la atención de solicitudes.
* Un usuario puede pertenecer a un único equipo.
* El equipo del usuario que crea una solicitud no determina automáticamente el equipo encargado de atenderla.
* Un equipo no puede eliminarse si tiene usuarios o solicitudes asociadas.

## Solicitudes

Una solicitud representa un requerimiento interno realizado dentro de ServiceFlow.

Al crear una solicitud, el `USER` debe proporcionar:

* Descripción.
* Archivo adjunto opcional.

El `USER` no selecciona:

* Categoría.
* Prioridad.
* Equipo.
* Agente responsable.

Estas propiedades son determinadas durante la gestión de la solicitud por un `AGENT`.

## Estados

Las solicitudes pueden encontrarse en los siguientes estados:

* `NEW`: solicitud recién creada.
* `IN_PROGRESS`: solicitud en proceso de atención.
* `PENDING`: solicitud pendiente de una acción, información o aprobación.
* `RESOLVED`: solicitud resuelta.
* `CLOSED`: solicitud cerrada.

Los cambios de estado deben quedar registrados en el historial de la solicitud.

## Clasificación y asignación

El `AGENT` es responsable de clasificar y asignar las solicitudes.

Puede establecer:

* Categoría.
* Prioridad.
* Equipo responsable.
* Agente asignado.
* Estado.

Una solicitud puede ser reasignada cuando sea necesario.

La asignación debe mantener la trazabilidad de los cambios realizados.

## Aprobaciones

Una categoría puede requerir aprobación.

Cuando una solicitud requiere aprobación:

* Se genera una aprobación asociada a la solicitud.
* La aprobación comienza en estado `PENDING`.
* El responsable autorizado puede aprobar o rechazar la solicitud.
* La decisión puede incluir un comentario.
* La fecha de decisión debe quedar registrada.

Una solicitud que requiere aprobación no debe avanzar a la siguiente etapa que dependa de dicha aprobación hasta obtener una decisión válida.

## Comentarios

Los usuarios pueden agregar comentarios a las solicitudes según los permisos de su rol.

Los comentarios pueden ser:

* Públicos: visibles para los participantes autorizados de la solicitud.
* Internos: destinados exclusivamente a la gestión interna.

Los comentarios deben conservar el usuario que los creó y la fecha de creación.

## Archivos

Los archivos adjuntos pertenecen a una solicitud.

La base de datos almacena los metadatos y la referencia del archivo, mientras que el archivo físico se almacena en el sistema de almacenamiento configurado.

Cada archivo debe conservar:

* Nombre.
* Ruta o referencia.
* Usuario que lo cargó.
* Fecha de creación.

## SLA

Las solicitudes pueden tener un SLA asociado.

El SLA permite controlar:

* Tiempo máximo de respuesta.
* Tiempo máximo de resolución.
* Fecha de respuesta.
* Fecha de resolución.

El cumplimiento del SLA debe poder determinarse a partir de las fechas registradas.

## Historial

Las operaciones relevantes sobre una solicitud deben quedar registradas en su historial.

El historial debe permitir identificar:

* Usuario que realizó la acción.
* Acción realizada.
* Valor anterior, cuando corresponda.
* Valor nuevo, cuando corresponda.
* Fecha de la acción.

El historial es de solo lectura para los usuarios del sistema y no debe modificarse como parte del flujo normal.

## Catálogos

Las categorías y prioridades son datos configurables por `ADMIN`.

Una categoría o prioridad no debe eliminarse si existen solicitudes que la utilizan.

Las prioridades deben mantener un nivel que permita determinar su orden de importancia.

## Seguridad

* Las contraseñas deben almacenarse utilizando hashing seguro.
* Las credenciales no deben almacenarse en texto plano.
* Los secretos y configuraciones sensibles deben mantenerse fuera del código fuente.
* Los permisos deben validarse en el Back-End.
* Un usuario solo puede realizar las operaciones permitidas por su rol.
* Las operaciones sensibles deben mantener trazabilidad cuando corresponda.
