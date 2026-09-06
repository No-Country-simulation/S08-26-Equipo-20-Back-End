# ServiceFlow | Back-End

Guía de DESARROLLO y REGLAS para mantener el código, la arquitectura y el flujo del trabajo del proyecto.

## Principios

ServiceFlow debe seguir los principios de Clean Code y SOLID, priorizando siempre un código simple, claro, legible y fácil de mantener. Se debe evitar la sobreingeniería y no introducir abstracciones, patrones o estructuras innecesarias cuando una solución más sencilla resuelva correctamente el problema.

## Back-End

ServiceFlow utiliza Python y FastAPI, manteniendo una arquitectura por cada donde los Routers manejan HTTP y las validaciones de entrada, los Services contienen la lógica de negocio, los Repositories gestionar el acceso a datos y los Models representan las entidades de la base de datos. Se utiliza PyDantic para los Schemas, SQLAlchemy para el acceso a PostgreSQL y Alembic para las migraciones. No se debe colocar lógica de negocio en los Routers ni reglas de negocio en los Repositories. Los datos de entrada y salida deben validarse correctamente y los errores deben manejarse de forma clara y consistente. No se debe exponer información sensible, almacenar constraseñas en texto plano ni hardcodear secretos, credenciales o configuraciones sensibles.

## Arquitectura

Cada capa debe mantener una responsabilidad clara.

Router → Service → Repository → Model

## Git

### Commits

Hacer uso de Conventional Commits:

```
feat: nueva funcionalidad
fix: corrección
refactor: refactorización
tests: pruebas
docs: documentación
chore: configuración
```

### Branches

```
feat/nombre
fix/nombre
refactor/nombre
test/nombre
docs/nombre
chore/nombre
```

## Workflow

El trabajo debe seguir un flujo ordenado, analizar el estado actual antes de modificarlo, explicar los cambios antes de implementarlos y consultar antes de tomar decisiones que afecten al proyecto. Solo se debe implementar lo solicitado, verificar los cambios realizados e informar las acciones ejecutadas. Una vez finalizado el trabajo, se debe eseperar la siguiente instrucción y no realizar cambios que estén fuera del alcance establecido.
