# ServiceFlow | Back-End | Autenticación

Sistema de Autenticación y Autorización utilizado para proteger el acceso a ServiceFlow y controlar las acciones disponibles para cada usuario.

## Login

El usuario inicia sesión utilizando:

* Email.
* Contraseña.

Si las credenciales son válidas, el sistema genera un token JWT.

El token contiene la identificación del usuario y una fecha de expiración.

Las credenciales inválidas deben devolver un mensaje genérico y no revelar si el usuario existe, está inactivo o ingresó una contraseña incorrecta.

## JWT

ServiceFlow utiliza JSON Web Tokens para mantener la autenticación de las solicitudes.

Características:

* Algoritmo: `HS256`.
* Identificación del usuario mediante `sub`.
* Expiración del token: 30 minutos.
* El secreto utilizado para firmar los tokens se almacena fuera del código fuente.

El token debe enviarse en las solicitudes que requieran autenticación.

## Autorización

La autenticación determina quién es el usuario.

La autorización determina qué acciones puede realizar.

Los permisos se controlan en el Back-End según el rol del usuario:

* `ADMIN`: acceso a las funciones administrativas.
* `AGENT`: acceso a las funciones relacionadas con la atención de solicitudes.
* `USER`: acceso a sus propias solicitudes y funciones disponibles para usuarios.

La protección implementada en el Front-End no reemplaza la validación de permisos en el Back-End.

## Cambio de Contraseña

Los usuarios pueden cambiar su contraseña utilizando su contraseña actual y una nueva contraseña.

La nueva contraseña debe tener al menos 8 caracteres.

Después de cambiar correctamente la contraseña:

* Se actualiza el password hash.
* Se elimina el indicador de cambio obligatorio.
* Se genera un nuevo token de autenticación.

## Contraseña Temporal

Cuando un administrador crea un usuario sin establecer una contraseña, el sistema genera una contraseña temporal.

La contraseña temporal:

* Tiene una longitud de 12 caracteres.
* Se entrega una única vez.
* No debe almacenarse en texto plano.
* No debe registrarse en logs.
* Obliga al usuario a cambiarla durante su primer acceso.

El sistema utiliza `must_change_password` para determinar si el usuario debe realizar el cambio.

## Usuarios Inactivos

Los usuarios marcados como inactivos no pueden iniciar sesión.

El sistema debe responder con el mismo mensaje genérico utilizado para credenciales inválidas, evitando revelar información sobre el estado de la cuenta.

## Seguridad

* Las contraseñas se almacenan utilizando hashing con Argon2.
* Nunca se almacenan contraseñas en texto plano.
* Los secretos utilizados por la aplicación se mantienen en variables de entorno.
* Los tokens JWT no deben registrarse en logs.
* Las contraseñas y credenciales nunca deben aparecer en logs.
* Los endpoints protegidos deben validar el token antes de procesar la solicitud.
* Los permisos deben validarse siempre en el Back-End.
