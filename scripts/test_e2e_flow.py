"""
Script de prueba End-to-End (E2E) para ServiceFlow - Service Agent MVP.
Ejecuta todo el ciclo de vida de una solicitud de principio a fin y muestra los resultados formateados en consola.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any

from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.main import app
from app.modules.categories.model import Categorie
from app.modules.priorities.model import Prioritie
from app.modules.requests.model import Request
from app.modules.teams.model import Team
from app.modules.users.model import Role, User

# Colores para la consola
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_step(step_num: int, title: str):
    print(f"\n{BOLD}{BLUE}======================================================================{RESET}")
    print(f"{BOLD}{CYAN}▶ PASO {step_num}: {title}{RESET}")
    print(f"{BOLD}{BLUE}======================================================================{RESET}")


def print_success(message: str, data: Any = None):
    print(f"{GREEN}✔ {message}{RESET}")
    if data is not None:
        formatted = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        print(f"{YELLOW}{formatted}{RESET}")


def print_info(message: str):
    print(f"ℹ {message}")


async def create_test_user(email: str, name: str, role_name: str, password: str = "Secret123!") -> User:
    async with SessionLocal() as session:
        role = await session.scalar(select(Role).where(Role.name == role_name))
        if not role:
            raise RuntimeError(f"El rol {role_name} no existe en la base de datos.")
        
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role_id=role.id,
            is_active=True,
            must_change_password=False,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def run_e2e():
    print(f"\n{BOLD}{GREEN}>>> INICIANDO PRUEBA END-TO-END (E2E) - SERVICEFLOW{RESET}\n")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Generar emails únicos para la prueba
        run_id = uuid.uuid4().hex[:6]
        admin_email = f"admin-{run_id}@test.com"
        agent_email = f"agent-{run_id}@test.com"
        user_email = f"colaborador-{run_id}@test.com"
        password = "Secret123!"

        created_user_ids = []
        created_category_ids = []
        created_priority_ids = []
        created_team_ids = []
        created_request_ids = []

        try:
            # -------------------------------------------------------------
            # PASO 1: Creación de Usuarios de Prueba
            # -------------------------------------------------------------
            print_step(1, "Crear usuarios de prueba (Admin, Agente, Colaborador)")
            admin = await create_test_user(admin_email, "Admin General", "ADMIN", password)
            agent = await create_test_user(agent_email, "Agente Soporte", "AGENT", password)
            colab = await create_test_user(user_email, "Juan Colaborador", "USER", password)
            created_user_ids.extend([admin.id, agent.id, colab.id])

            print_success("Usuarios creados con éxito:", {
                "admin": {"id": admin.id, "email": admin.email, "role": "ADMIN"},
                "agent": {"id": agent.id, "email": agent.email, "role": "AGENT"},
                "user": {"id": colab.id, "email": colab.email, "role": "USER"},
            })

            # -------------------------------------------------------------
            # PASO 2: Autenticación / Login
            # -------------------------------------------------------------
            print_step(2, "Autenticación de los 3 usuarios vía /auth/login")
            
            resp_admin = await client.post("/auth/login", json={"email": admin_email, "password": password})
            assert resp_admin.status_code == 200, f"Login falló: {resp_admin.text}"
            admin_token = resp_admin.json()["access_token"]
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            print_success("Token JWT obtenido para ADMIN")

            resp_agent = await client.post("/auth/login", json={"email": agent_email, "password": password})
            assert resp_agent.status_code == 200, f"Login falló: {resp_agent.text}"
            agent_token = resp_agent.json()["access_token"]
            agent_headers = {"Authorization": f"Bearer {agent_token}"}
            print_success("Token JWT obtenido para AGENT")

            resp_user = await client.post("/auth/login", json={"email": user_email, "password": password})
            assert resp_user.status_code == 200, f"Login falló: {resp_user.text}"
            user_token = resp_user.json()["access_token"]
            user_headers = {"Authorization": f"Bearer {user_token}"}
            print_success("Token JWT obtenido para USER")

            # -------------------------------------------------------------
            # PASO 3: Creación de Catálogos (Categorías, Prioridades, Equipos)
            # -------------------------------------------------------------
            print_step(3, "ADMIN crea Catálogos iniciales")

            # Categoría que requiere aprobación
            resp_cat = await client.post(
                "/categories",
                headers=admin_headers,
                json={"name": f"Equipos y Hardware {run_id}", "description": "Laptops y accesorios", "requires_approval": True},
            )
            assert resp_cat.status_code == 201, resp_cat.text
            cat_data = resp_cat.json()
            created_category_ids.append(cat_data["id"])
            print_success("Categoría creada (con requires_approval=True):", cat_data)

            # Prioridad
            resp_pri = await client.post(
                "/priorities",
                headers=admin_headers,
                json={"name": f"Alta {run_id}", "level": 1},
            )
            assert resp_pri.status_code == 201, resp_pri.text
            pri_data = resp_pri.json()
            created_priority_ids.append(pri_data["id"])
            print_success("Prioridad creada:", pri_data)

            # Equipo
            resp_team = await client.post(
                "/teams",
                headers=admin_headers,
                json={"name": f"Infraestructura TI {run_id}", "description": "Gestión de hardware y redes"},
            )
            assert resp_team.status_code == 201, resp_team.text
            team_data = resp_team.json()
            created_team_ids.append(team_data["id"])
            print_success("Equipo creado:", team_data)

            # -------------------------------------------------------------
            # PASO 4: Colaborador crea una Solicitud
            # -------------------------------------------------------------
            print_step(4, "USER crea una nueva Solicitud")
            resp_req = await client.post(
                "/requests/",
                headers=user_headers,
                json={"description": "Requiero una laptop MacBook Pro M3 para tareas de desarrollo backend."},
            )
            assert resp_req.status_code == 201, resp_req.text
            req_data = resp_req.json()
            request_id = req_data["id"]
            created_request_ids.append(request_id)
            print_success(f"Solicitud #{request_id} creada por el colaborador (Estado: {req_data['status']}):", req_data)

            # -------------------------------------------------------------
            # PASO 5: Agente de Servicio consulta solicitudes
            # -------------------------------------------------------------
            print_step(5, "AGENT consulta la lista general de solicitudes")
            resp_list = await client.get("/requests/", headers=agent_headers)
            assert resp_list.status_code == 200
            print_success(f"Agente ve {len(resp_list.json())} solicitud(es) en total en el sistema.")

            # -------------------------------------------------------------
            # PASO 6: Clasificación y Asignación (Triage) por parte del Agente
            # -------------------------------------------------------------
            print_step(6, "AGENT clasifica la Solicitud y se asigna como responsable")
            resp_classify = await client.patch(
                f"/requests/{request_id}",
                headers=agent_headers,
                json={
                    "category_id": cat_data["id"],
                    "priority_id": pri_data["id"],
                    "team_id": team_data["id"],
                    "assigned_to": agent.id,
                },
            )
            assert resp_classify.status_code == 200, resp_classify.text
            print_success("Solicitud clasificada correctamente:", resp_classify.json())

            # -------------------------------------------------------------
            # PASO 7: Verificación automática de SLA y Aprobación
            # -------------------------------------------------------------
            print_step(7, "Verificar SLA y Aprobación autogenerados")
            
            # Consultar SLA
            resp_sla = await client.get(f"/requests/{request_id}/sla", headers=agent_headers)
            assert resp_sla.status_code == 200, resp_sla.text
            sla_data = resp_sla.json()
            print_success("SLA autogenerado con deadline y responded_at registrado:", sla_data)

            # Consultar Aprobaciones
            resp_appr = await client.get(f"/requests/{request_id}/approvals", headers=agent_headers)
            assert resp_appr.status_code == 200, resp_appr.text
            approvals_data = resp_appr.json()
            assert len(approvals_data) > 0, "No se generó la aprobación automática"
            approval_id = approvals_data[0]["id"]
            print_success("Aprobación autogenerada (requerida por la categoría):", approvals_data[0])

            # -------------------------------------------------------------
            # PASO 8: Comunicación (Comentarios Públicos vs Notas Internas)
            # -------------------------------------------------------------
            print_step(8, "Comunicación: Agente añade nota interna y Colaborador comenta")

            # Nota interna del agente (solo visible para AGENT/ADMIN)
            resp_note = await client.post(
                f"/requests/{request_id}/comments",
                headers=agent_headers,
                json={"content": "Nota Interna: Revisé stock en depósito central y queda 1 unidad disponible.", "is_internal": True},
            )
            assert resp_note.status_code == 201
            print_success("Nota interna agregada por el Agente.")

            # Comentario público del colaborador
            resp_pub = await client.post(
                f"/requests/{request_id}/comments",
                headers=user_headers,
                json={"content": "¿Aproximadamente cuánto tiempo demora la entrega del equipo?", "is_internal": False},
            )
            assert resp_pub.status_code == 201
            print_success("Comentario público agregado por el Colaborador.")

            # Verificar aislamiento: Colaborador solo debe ver 1 comentario (el público)
            resp_user_comments = await client.get(f"/requests/{request_id}/comments", headers=user_headers)
            assert len(resp_user_comments.json()) == 1, "El usuario vio notas internas indebidamente"
            print_success(f"Filtro de seguridad validado: Colaborador solo ve {len(resp_user_comments.json())} comentario(s) públicos.")

            # Agente debe ver ambos (2)
            resp_agent_comments = await client.get(f"/requests/{request_id}/comments", headers=agent_headers)
            assert len(resp_agent_comments.json()) == 2
            print_success(f"Agente ve {len(resp_agent_comments.json())} comentarios (incluyendo notas internas).")

            # -------------------------------------------------------------
            # PASO 9: ADMIN Aprueba la Solicitud
            # -------------------------------------------------------------
            print_step(9, "ADMIN decide y aprueba la Solicitud")
            resp_decide = await client.patch(
                f"/requests/{request_id}/approvals/{approval_id}",
                headers=admin_headers,
                json={"status": "APPROVED", "comment": "Aprobado según presupuesto de equipamiento Q3."},
            )
            assert resp_decide.status_code == 200, resp_decide.text
            print_success("Aprobación registrada:", resp_decide.json())

            # -------------------------------------------------------------
            # PASO 10: Transición de Estados (IN_PROGRESS -> RESOLVED -> CLOSED)
            # -------------------------------------------------------------
            print_step(10, "Transición de Estados de la Solicitud")

            # 1. Pasar a IN_PROGRESS
            resp_in_prog = await client.patch(
                f"/requests/{request_id}/status",
                headers=agent_headers,
                json={"status": "IN_PROGRESS"},
            )
            assert resp_in_prog.status_code == 200
            print_success("Estado actualizado a IN_PROGRESS")

            # 2. Pasar a RESOLVED
            resp_res = await client.patch(
                f"/requests/{request_id}/status",
                headers=agent_headers,
                json={"status": "RESOLVED"},
            )
            assert resp_res.status_code == 200
            res_data = resp_res.json()
            assert res_data["resolved_at"] is not None
            print_success("Estado actualizado a RESOLVED (con resolved_at registrado):", {
                "id": res_data["id"],
                "status": res_data["status"],
                "resolved_at": res_data["resolved_at"]
            })

            # 3. Pasar a CLOSED
            resp_closed = await client.patch(
                f"/requests/{request_id}/status",
                headers=agent_headers,
                json={"status": "CLOSED"},
            )
            assert resp_closed.status_code == 200
            closed_data = resp_closed.json()
            assert closed_data["closed_at"] is not None
            print_success("Estado actualizado a CLOSED (con closed_at registrado):", {
                "id": closed_data["id"],
                "status": closed_data["status"],
                "closed_at": closed_data["closed_at"]
            })

            # -------------------------------------------------------------
            # PASO 11: Auditoría y Trazabilidad (Historial Completo)
            # -------------------------------------------------------------
            print_step(11, "Consultar el Historial de Auditoría de la Solicitud")
            resp_hist = await client.get(f"/requests/{request_id}/history", headers=agent_headers)
            assert resp_hist.status_code == 200
            history_entries = resp_hist.json()
            print_success(f"Historial con {len(history_entries)} evento(s) de trazabilidad:", history_entries)

            # -------------------------------------------------------------
            # RESUMEN FINAL
            # -------------------------------------------------------------
            print(f"\n{BOLD}{GREEN}======================================================================{RESET}")
            print(f"{BOLD}{GREEN}*** ¡TODAS LAS PRUEBAS END-TO-END PASARON SATISFACTORIAMENTE!{RESET}")
            print(f"{BOLD}{GREEN}======================================================================{RESET}\n")

        finally:
            # Limpieza de datos creados durante la prueba
            print_info("Limpiando datos de prueba...")
            async with SessionLocal() as session:
                # Borrar en orden inverso (hijos primero) para evitar errores de llave foránea
                from app.modules.requests.model import Approval, Comment, RequestHistory, Sla
                for req_id in created_request_ids:
                    await session.execute(delete(Approval).where(Approval.request_id == req_id))
                    await session.execute(delete(Comment).where(Comment.request_id == req_id))
                    await session.execute(delete(RequestHistory).where(RequestHistory.request_id == req_id))
                    await session.execute(delete(Sla).where(Sla.request_id == req_id))
                    await session.execute(delete(Request).where(Request.id == req_id))
                for cat_id in created_category_ids:
                    await session.execute(delete(Categorie).where(Categorie.id == cat_id))
                for pri_id in created_priority_ids:
                    await session.execute(delete(Prioritie).where(Prioritie.id == pri_id))
                for t_id in created_team_ids:
                    await session.execute(delete(Team).where(Team.id == t_id))
                for u_id in created_user_ids:
                    await session.execute(delete(User).where(User.id == u_id))
                await session.commit()
            print_success("Base de datos limpia.")


if __name__ == "__main__":
    asyncio.run(run_e2e())
