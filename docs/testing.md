# ServiceFlow | Back-End | Testing

Estrategia de pruebas utilizada para verificar el correcto funcionamiento del Back-End y mantener la estabilidad del sistema durante su desarrollo.

## Herramientas

El proyecto utiliza:

* `pytest` para ejecutar las pruebas.
* `httpx` para realizar pruebas sobre los endpoints de FastAPI.

## Objetivo

Las pruebas deben verificar principalmente:

* Reglas de negocio.
* Autenticación y autorización.
* Validación de datos.
* Comportamiento de los endpoints.
* Persistencia de datos.
* Manejo de errores.

## Tests

Las pruebas deben organizarse de acuerdo con la responsabilidad que se desea verificar.

### Services

Los Services deben probar las reglas de negocio y los diferentes escenarios de cada operación.

Se deben contemplar:

* Operaciones exitosas.
* Datos inválidos.
* Recursos inexistentes.
* Operaciones no permitidas.
* Reglas específicas del negocio.

### API

Los endpoints deben probarse mediante solicitudes HTTP para verificar:

* Código de respuesta.
* Datos enviados.
* Datos recibidos.
* Autenticación.
* Autorización.
* Errores de validación.

### Autenticación

Se deben probar como mínimo:

* Login exitoso.
* Credenciales inválidas.
* Usuario inactivo.
* Token válido.
* Token inválido o expirado.
* Cambio de contraseña.
* Cambio obligatorio de contraseña.

### Usuarios

Se deben verificar:

* Creación de usuarios.
* Consulta de usuarios.
* Actualización de usuarios.
* Desactivación de usuarios.
* Restricciones sobre administradores.
* Filtros de búsqueda.

### Solicitudes

Se deben verificar:

* Creación de solicitudes.
* Consulta de solicitudes.
* Actualización de solicitudes.
* Cambios de estado.
* Asignación de solicitudes.
* Registro del historial.
* Permisos según el rol.

## Ejecución

Las pruebas se ejecutan mediante:

```bash
pytest
```

El desarrollo debe continuar únicamente cuando las pruebas correspondientes a los cambios realizados sean satisfactorias.

## Buenas Prácticas

* Cada prueba debe verificar un comportamiento concreto.
* Las pruebas deben ser claras y fáciles de mantener.
* No se deben realizar pruebas innecesariamente complejas.
* Los tests no deben depender entre sí.
* Los datos utilizados durante las pruebas deben estar controlados.
* Los cambios en reglas de negocio deben acompañarse de las pruebas correspondientes.
