# ServiceFlow | Back-End | API

## Autenticación
POST /auth/login
GET /auth/me
POST /auth/change-password

## Usuarios
GET /users
POST /users
GET /users/{id}
PATCH /users/{id}
DELETE /users/{id}

## Equipos
GET /teams
POST /teams
GET /teams/{id}
PATCH /teams/{id}
DELETE /teams/{id}

## Categorías
GET /categories
POST /categories
PATCH /categories/{id}
DELETE /categories/{id}

## Prioridades
GET /priorities
POST /priorities
PATCH /priorities/{id}
DELETE /priorities/{id}

## Solicitudes
POST /requests
GET /requests
GET /requests/{id}
PATCH /requests/{id}
