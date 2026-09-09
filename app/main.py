from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.categories.model import Categorie  # noqa: F401
from app.modules.priorities.model import Prioritie  # noqa: F401
from app.modules.requests.model import (  # noqa: F401
    Approval,
    Attachment,
    Comment,
    Request,
    RequestHistory,
    Sla,
)
from app.modules.teams.model import Team  # noqa: F401
from app.modules.users.model import Role, User  # noqa: F401
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.teams.router import router as teams_router
from app.modules.categories.router import router as categories_router
from app.modules.priorities.router import router as priorities_router
from app.modules.requests.router import router as requests_router

app = FastAPI(title="ServiceFlow", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(teams_router)
app.include_router(categories_router)
app.include_router(priorities_router)
app.include_router(requests_router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}