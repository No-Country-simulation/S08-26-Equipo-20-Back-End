"""
Script de seed de datos de prueba para ServiceFlow.

Siembra un conjunto determinista de datos que cubre todos los endpoints de la API,
incluidos los estados que la logica de negocio no produce de forma natural
(approbaciones PENDING en solicitudes cerradas, SLA incumplido, usuarios dados de baja).

Los datos quedan PERSISTENTES: a diferencia de scripts/test_e2e_flow.py, este script
no borra lo que crea al terminar, para poder probarlos desde Swagger o Postman.

Uso (desde la raiz del repo, con el entorno virtual activo):

    python -m scripts.seed_data             # siembra; aborta si ya hay datos del seed
    python -m scripts.seed_data --reset     # borra lo sembrado antes y vuelve a sembrar
    python -m scripts.seed_data --quiet      # sin salida formateada

NOTA 1: debe invocarse en modo modulo (-m). Ejecutarlo como "python scripts/seed_data.py"
falla con ModuleNotFoundError: No module named 'app', porque el directorio del script
(y no la raiz del repo) queda en sys.path.

NOTA 2: el Dockerfile no copia scripts/ a la imagen, asi que desde el contenedor hay que
copiarlo primero. Las dependencias solo estan instaladas ahi:

    docker cp scripts/seed_data.py sf-back-end:/app/seed_data.py
    docker compose exec sf-back-end python seed_data.py --reset

UPLOAD_ROOT se deriva del paquete app y no de __file__, por eso el script funciona igual
desde el host o desde dentro del contenedor.
"""

from __future__ import annotations

import argparse
import asyncio
import shutil
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

import app
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.categories.model import Categorie
from app.modules.priorities.model import Prioritie
from app.modules.requests.model import (
    Approval,
    ApprovalStatus,
    Attachment,
    Comment,
    Request,
    RequestHistory,
    RequestStatus,
    Sla,
)
from app.modules.teams.model import Team
from app.modules.users.model import Role, User

# Derivada del paquete app (no de __file__) para que el script funcione igual
# si se ejecuta desde el host o desde dentro del contenedor.
UPLOAD_ROOT = Path(app.__file__).resolve().parent / "uploads" / "requests"
SEED_FILE_PREFIX = "seed_"
SEED_PASSWORD = "ServiceFlow123"
# Los correos usan un dominio "real" a proposito: LoginRequest valida el correo con
# EmailStr, y email-validator rechaza .local, .test y .localhost como dominios
# reservados. Con @demo.local el seed crea usuarios que no pueden hacer login.

GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

# --- Catalogo sembrado (tus nombres son la marca que identifica lo que es del seed) ---

TEAM_SPECS = [
    {"name": "Soporte TI", "description": "Hardware, software y estaciones de trabajo"},
    {"name": "Helpdesk", "description": "Primer nivel de atencion al usuario interno"},
    {"name": "Infraestructura", "description": "Redes, servidores y accesos"},
]

CATEGORY_SPECS = [
    {"name": "Hardware", "description": "Equipos y periféricos", "requires_approval": True},
    {"name": "Licencias", "description": "Software y licencias", "requires_approval": True},
    {"name": "Accesos", "description": "Permisos y altas de usuarios", "requires_approval": False},
    {"name": "Redes", "description": "Conectividad y VPN", "requires_approval": False},
    {"name": "Otros", "description": "Sin clasificar", "requires_approval": False},
]

PRIORITY_SPECS = [
    {"name": "Alta", "level": 1},
    {"name": "Media", "level": 2},
    {"name": "Baja", "level": 3},
]

USER_SPECS = [
    {"email": "admin@demo.serviceflow.dev", "name": "Ana Administradora", "role": "ADMIN", "team": None},
    {"email": "agente@demo.serviceflow.dev", "name": "Luis Agente TI", "role": "AGENT", "team": "Soporte TI"},
    {"email": "helpdesk@demo.serviceflow.dev", "name": "Marta Helpdesk", "role": "AGENT", "team": "Helpdesk"},
    {"email": "usuario@demo.serviceflow.dev", "name": "Carlos Colaborador", "role": "USER", "team": None},
    {"email": "usuario2@demo.serviceflow.dev", "name": "Lucia Colaboradora", "role": "USER", "team": None},
    {
        "email": "inactivo@demo.serviceflow.dev",
        "name": "Pedro De Baja",
        "role": "USER",
        "team": None,
        "is_active": False,
    },
]

TEAM_NAMES = [t["name"] for t in TEAM_SPECS]
CATEGORY_NAMES = [c["name"] for c in CATEGORY_SPECS]
PRIORITY_NAMES = [p["name"] for p in PRIORITY_SPECS]
USER_EMAILS = [u["email"] for u in USER_SPECS]


def _ago(hours: float) -> datetime:
    return datetime.now(timezone.utc) - timedelta(hours=hours)


def _ahead(hours: float) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=hours)


def _log(message: str, color: str = "") -> None:
    print(f"{color}{message}{RESET}" if color else message)


# --- Limpieza ---


async def wipe(session: AsyncSession) -> None:
    """Borra lo sembrado en orden inverso de dependencias para no violar las FK."""
    seeded_user_ids = select(User.id).where(User.email.in_(USER_EMAILS))
    seeded_request_ids = select(Request.id).where(
        Request.created_by.in_(seeded_user_ids)
        | Request.assigned_to.in_(seeded_user_ids)
    )

    for child in (Attachment, Comment, Approval, Sla, RequestHistory):
        await session.execute(delete(child).where(child.request_id.in_(seeded_request_ids)))
    await session.execute(delete(Request).where(Request.id.in_(seeded_request_ids)))
    await session.execute(delete(User).where(User.email.in_(USER_EMAILS)))
    await session.execute(delete(Categorie).where(Categorie.name.in_(CATEGORY_NAMES)))
    await session.execute(delete(Prioritie).where(Prioritie.name.in_(PRIORITY_NAMES)))
    await session.execute(delete(Team).where(Team.name.in_(TEAM_NAMES)))
    await session.commit()

    # Los adjuntos siembran archivos reales en disco; se limpian junto con la fila.
    if UPLOAD_ROOT.exists():
        for request_dir in UPLOAD_ROOT.iterdir():
            if request_dir.is_dir() and any(
                f.name.startswith(SEED_FILE_PREFIX) for f in request_dir.iterdir()
            ):
                shutil.rmtree(request_dir, ignore_errors=True)


async def seed_exists(session: AsyncSession) -> bool:
    return bool(await session.scalar(select(User.id).where(User.email.in_(USER_EMAILS)).limit(1)))


# --- Siembra ---


async def seed_catalogs(session: AsyncSession) -> tuple[dict, dict, dict]:
    teams = {}
    for spec in TEAM_SPECS:
        team = await session.scalar(select(Team).where(Team.name == spec["name"]))
        if team is None:
            team = Team(name=spec["name"], description=spec["description"])
            session.add(team)
        teams[spec["name"]] = team

    categories = {}
    for spec in CATEGORY_SPECS:
        category = await session.scalar(
            select(Categorie).where(Categorie.name == spec["name"])
        )
        if category is None:
            category = Categorie(**spec)
            session.add(category)
        categories[spec["name"]] = category

    priorities = {}
    # `priorities.level` es UNIQUE. En una base que ya tiene datos, el nivel canonico
    # puede estar ocupado por otra prioridad; en ese caso se busca el siguiente nivel
    # libre conservando el orden relativo de las sembradas.
    taken_levels = set(await session.scalars(select(Prioritie.level)))
    for spec in PRIORITY_SPECS:
        priority = await session.scalar(
            select(Prioritie).where(Prioritie.name == spec["name"])
        )
        if priority is None:
            level = spec["level"]
            while level in taken_levels:
                level += 1
            taken_levels.add(level)
            priority = Prioritie(name=spec["name"], level=level)
            session.add(priority)
        priorities[spec["name"]] = priority

    await session.commit()
    return teams, categories, priorities


async def seed_users(session: AsyncSession, teams: dict) -> dict:
    roles = {}
    for role_name in ("ADMIN", "AGENT", "USER"):
        role = await session.scalar(select(Role).where(Role.name == role_name))
        if role is None:
            raise RuntimeError(
                f"El rol {role_name} no existe. Ejecuta 'alembic upgrade head' primero."
            )
        roles[role_name] = role

    users = {}
    for spec in USER_SPECS:
        user = await session.scalar(select(User).where(User.email == spec["email"]))
        if user is None:
            user = User(
                name=spec["name"],
                email=spec["email"],
                password_hash=hash_password(SEED_PASSWORD),
                role_id=roles[spec["role"]].id,
                team_id=teams[spec["team"]].id if spec["team"] else None,
                must_change_password=False,
                is_active=spec.get("is_active", True),
            )
            session.add(user)
        users[spec["email"]] = user

    await session.commit()
    return users


def _write_placeholder(request_id: int, file_name: str) -> str:
    """Crea el archivo fisico para que GET /uploads/... no devuelva 404."""
    request_dir = UPLOAD_ROOT / str(request_id)
    request_dir.mkdir(parents=True, exist_ok=True)
    disk_name = f"{SEED_FILE_PREFIX}{uuid.uuid4().hex[:8]}_{file_name}"
    (request_dir / disk_name).write_text(
        f"Archivo de prueba generado por scripts/seed_data.py\nsolicitud={request_id}\n",
        encoding="utf-8",
    )
    return f"/uploads/requests/{request_id}/{disk_name}"


async def seed_requests(
    session: AsyncSession, users: dict, teams: dict, categories: dict, priorities: dict
) -> None:
    admin = users["admin@demo.serviceflow.dev"]
    agent = users["agente@demo.serviceflow.dev"]
    helpdesk = users["helpdesk@demo.serviceflow.dev"]
    user1 = users["usuario@demo.serviceflow.dev"]
    user2 = users["usuario2@demo.serviceflow.dev"]

    # (descripcion, creador, estado, categoria, prioridad, equipo, asignado)
    specs = [
        ("No puedo ingresar al sistema, pantalla congelada.", user1, RequestStatus.NEW, None, None, None, None),
        ("El teclado no responde y el mouse óptico falla.", user2, RequestStatus.NEW, "Hardware", "Media", "Soporte TI", None),
        ("Solicito permisos para la carpeta compartida.", user1, RequestStatus.IN_PROGRESS, "Accesos", "Alta", "Infraestructura", agent),
        ("Renovación de suscripción para licencia de Figma.", user2, RequestStatus.PENDING, "Licencias", "Alta", "Soporte TI", helpdesk),
        ("Monitor secundario no da video tras reinicio.", user1, RequestStatus.RESOLVED, "Hardware", "Alta", "Soporte TI", agent),
        ("Cortes intermitentes de conexión con la VPN.", user2, RequestStatus.RESOLVED, "Redes", "Media", "Infraestructura", helpdesk),
        ("Reemplazo de batería de notebook corporativa.", user1, RequestStatus.CLOSED, "Hardware", "Alta", "Soporte TI", agent),
        ("Pedido de licencia para software no homologado.", user2, RequestStatus.CLOSED, "Licencias", "Baja", "Helpdesk", helpdesk),
    ]

    requests: list[Request] = []
    for description, creator, status, category, priority, team, assignee in specs:
        request = Request(
            description=description,
            status=status,
            created_by=creator.id,
            category_id=categories[category].id if category else None,
            priority_id=priorities[priority].id if priority else None,
            team_id=teams[team].id if team else None,
            assigned_to=assignee.id if assignee else None,
            created_at=_ago(72),
        )
        if status in (RequestStatus.RESOLVED, RequestStatus.CLOSED):
            request.resolved_at = _ago(20)
        if status == RequestStatus.CLOSED:
            request.closed_at = _ago(10)
        session.add(request)
        requests.append(request)

    await session.commit()

    # --- SLA: un caso dentro de plazo y otro incumplido ---
    slas = [
        # Solicitud 3 (IN_PROGRESS): plazos futuros, sin responder todavia.
        Sla(
            request_id=requests[2].id,
            response_deadline=_ahead(6),
            resolution_deadline=_ahead(48),
        ),
        # Solicitud 4 (PENDING): respondida a tiempo.
        Sla(
            request_id=requests[3].id,
            response_deadline=_ago(20),
            resolution_deadline=_ahead(30),
            responded_at=_ago(22),
        ),
        # Solicitud 5 (RESOLVED): cumplida en ambos plazos.
        Sla(
            request_id=requests[4].id,
            response_deadline=_ago(40),
            resolution_deadline=_ago(10),
            responded_at=_ago(42),
            resolved_at=_ago(22),
        ),
        # Solicitud 6 (RESOLVED):响应 tardia -> response_on_time=false.
        Sla(
            request_id=requests[5].id,
            response_deadline=_ago(48),
            resolution_deadline=_ago(12),
            responded_at=_ago(24),
            resolved_at=_ago(20),
        ),
        # Solicitud 7 (CLOSED): cumplida.
        Sla(
            request_id=requests[6].id,
            response_deadline=_ago(60),
            resolution_deadline=_ago(30),
            responded_at=_ago(62),
            resolved_at=_ago(32),
        ),
    ]
    session.add_all(slas)

    # --- Aprobaciones: PENDING, APPROVED y REJECTED ---
    session.add_all(
        [
            Approval(
                request_id=requests[3].id,
                approver_id=admin.id,
                status=ApprovalStatus.PENDING,
                comment=None,
            ),
            Approval(
                request_id=requests[6].id,
                approver_id=admin.id,
                status=ApprovalStatus.APPROVED,
                comment="Aprobado dentro del presupuesto del trimestre.",
                decided_at=_ago(28),
            ),
            Approval(
                request_id=requests[7].id,
                approver_id=admin.id,
                status=ApprovalStatus.REJECTED,
                comment="Rechazado: el software ya esta cubierto por la licencia corporativa.",
                decided_at=_ago(26),
            ),
        ]
    )

    # --- Comentarios: mezcla de publicos y notas internas ---
    session.add_all(
        [
            Comment(
                request_id=requests[4].id,
                user_id=agent.id,
                content="Nota interna: queda una sola unidad en depósito, reservada para este caso.",
                is_internal=True,
            ),
            Comment(
                request_id=requests[4].id,
                user_id=agent.id,
                content="Hola Carlos, tenemos un monitor de reemplazo listo para entregarte mañana a primera hora.",
                is_internal=False,
            ),
            Comment(
                request_id=requests[4].id,
                user_id=user1.id,
                content="Excelente, muchas gracias. Me viene perfecto para arrancar la semana.",
                is_internal=False,
            ),
            Comment(
                request_id=requests[5].id,
                user_id=helpdesk.id,
                content="Nota interna: se reinició el túnel en el concentrador VPN y se estabilizaron las sesiones.",
                is_internal=True,
            ),
        ]
    )

    # --- Historial de trazabilidad ---
    session.add_all(
        [
            RequestHistory(
                request_id=requests[3].id,
                user_id=agent.id,
                action="change_category",
                old_value=None,
                new_value="Licencias",
            ),
            RequestHistory(
                request_id=requests[3].id,
                user_id=helpdesk.id,
                action="change_priority",
                old_value="Media",
                new_value="Alta",
            ),
            RequestHistory(
                request_id=requests[3].id,
                user_id=helpdesk.id,
                action="change_status",
                old_value="IN_PROGRESS",
                new_value="PENDING",
            ),
            RequestHistory(
                request_id=requests[6].id,
                user_id=admin.id,
                action="change_status",
                old_value="RESOLVED",
                new_value="CLOSED",
            ),
        ]
    )

    await session.commit()

    # --- Adjuntos: se crean despues del commit para conocer el id de la solicitud ---
    session.add_all(
        [
            Attachment(
                request_id=requests[4].id,
                uploaded_by=user1.id,
                file_name="foto_falla_monitor.png",
                file_path=_write_placeholder(requests[4].id, "foto_falla_monitor.png"),
            ),
            Attachment(
                request_id=requests[5].id,
                uploaded_by=helpdesk.id,
                file_name="log_conexion_vpn.txt",
                file_path=_write_placeholder(requests[5].id, "log_conexion_vpn.txt"),
            ),
        ]
    )
    await session.commit()


# --- Reporte ---


async def report(session: AsyncSession) -> None:
    print(f"\n{BOLD}{GREEN}{'=' * 70}{RESET}")
    print(f"{BOLD}{GREEN}DATOS DE PRUEBA LISTOS{RESET}")
    print(f"{BOLD}{GREEN}{'=' * 70}{RESET}\n")

    print(f"{BOLD}Usuarios (password: {SEED_PASSWORD}){RESET}")
    users = (
        await session.scalars(select(User).where(User.email.in_(USER_EMAILS)).order_by(User.id))
    ).all()
    for user in users:
        role = await session.scalar(select(Role).where(Role.id == user.role_id))
        team = await session.scalar(select(Team).where(Team.id == user.team_id)) if user.team_id else None
        estado = "activo" if user.is_active else f"{RED}inactivo (login dara 401){RESET}"
        print(
            f"  id={user.id:<3} {user.email:<24} {role.name:<6} "
            f"team={team.name if team else '-':<16} {estado}"
        )

    print(f"\n{BOLD}Catalogos{RESET}")
    for model, names in (
        (Team, TEAM_NAMES),
        (Categorie, CATEGORY_NAMES),
        (Prioritie, PRIORITY_NAMES),
    ):
        rows = await session.scalars(
            select(model).where(model.name.in_(names)).order_by(model.id)
        )
        for row in rows.all():
            level = f" level={row.level}" if model is Prioritie else ""
            print(f"  {model.__tablename__:<12} id={row.id:<3} {row.name}{level}")

    print(f"\n{BOLD}Solicitudes{RESET}")
    seeded_requests = await session.scalars(
        select(Request)
        .where(Request.created_by.in_(select(User.id).where(User.email.in_(USER_EMAILS))))
        .order_by(Request.id)
    )
    for request in seeded_requests.all():
        print(
            f"  id={request.id:<3} {request.status.value:<12} "
            f"team={request.team_id or '-':<4} assignee={request.assigned_to or '-':<4} "
            f"{request.description[:52]}"
        )

    print(f"\n{BOLD}Primer paso para obtener un token{RESET}")
    print(f"{YELLOW}  curl -X POST http://localhost:8000/auth/login \\{RESET}")
    print(f'{YELLOW}    -H "Content-Type: application/json" \\{RESET}')
    print(f'{YELLOW}    -d \'{{"email":"admin@demo.serviceflow.dev","password":"{SEED_PASSWORD}"}}\'{RESET}\n')


async def main(reset: bool, quiet: bool) -> int:
    async with SessionLocal() as session:
        if await seed_exists(session):
            if not reset:
                print(
                    f"{RED}Ya existen datos del seed.{RESET} "
                    f"Usa --reset para borrarlos y volver a sembrar."
                )
                return 1
            if not quiet:
                _log("Borrando datos previos del seed...", YELLOW)
            await wipe(session)
            if not quiet:
                _log("Datos previos eliminados.", GREEN)

        teams, categories, priorities = await seed_catalogs(session)
        users = await seed_users(session, teams)
        await seed_requests(session, users, teams, categories, priorities)

    if not quiet:
        async with SessionLocal() as session:
            await report(session)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Siembra datos de prueba en ServiceFlow.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Borra los datos sembrados previamente antes de insertar.",
    )
    parser.add_argument("--quiet", action="store_true", help="Omite el reporte formateado.")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(main(args.reset, args.quiet)))
