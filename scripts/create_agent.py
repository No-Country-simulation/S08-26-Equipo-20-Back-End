import asyncio
from sqlalchemy import select
from app.core.database import SessionLocal
from app.core.security import hash_password

# Import all models to register them in SQLAlchemy
from app.modules.categories.model import Categorie
from app.modules.priorities.model import Prioritie
from app.modules.requests.model import Request
from app.modules.teams.model import Team
from app.modules.users.model import Role, User

async def create_agent():
    async with SessionLocal() as session:
        # Agent
        role_agent = await session.scalar(select(Role).where(Role.name == "AGENT"))
        agent = User(
            name="Linder Rodríguez",
            email="linder@serviceflow.com",
            password_hash=hash_password("agent123"),
            role_id=role_agent.id,
            is_active=True,
            must_change_password=False,
        )
        session.add(agent)
        
        # Admin (for approvals or testing)
        role_admin = await session.scalar(select(Role).where(Role.name == "ADMIN"))
        admin = User(
            name="Admin System",
            email="admin@serviceflow.com",
            password_hash=hash_password("admin123"),
            role_id=role_admin.id,
            is_active=True,
            must_change_password=False,
        )
        session.add(admin)

        # User (to create requests)
        role_user = await session.scalar(select(Role).where(Role.name == "USER"))
        user = User(
            name="Usuario Prueba",
            email="user@serviceflow.com",
            password_hash=hash_password("user123"),
            role_id=role_user.id,
            is_active=True,
            must_change_password=False,
        )
        session.add(user)

        await session.commit()
        print("Usuarios creados con éxito:")
        print("- Agente: linder@serviceflow.com / agent123")
        print("- Admin: admin@serviceflow.com / admin123")
        print("- User: user@serviceflow.com / user123")

if __name__ == "__main__":
    asyncio.run(create_agent())
