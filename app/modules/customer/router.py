import time
from collections import defaultdict
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

from .repository import SQLCustomerRepository
from .schemas import (
    AttachmentRead,
    CommentCreate,
    CommentRead,
    CustomerRequestCreate,
    CustomerRequestDetail,
    CustomerRequestRead,
    PriorityRead,
)
from .service import CustomerService

router = APIRouter(prefix="/requests", tags=["Customer Requests"])

_create_request_rate_limit_tracker: dict[int, list[float]] = defaultdict(list)
_comment_rate_limit_tracker: dict[int, list[float]] = defaultdict(list)
_attachment_rate_limit_tracker: dict[int, list[float]] = defaultdict(list)

MAX_REQUESTS_PER_MINUTE = 5
MAX_COMMENTS_PER_MINUTE = 5
MAX_ATTACHMENTS_PER_MINUTE = 5


def get_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> SQLCustomerRepository:
    return SQLCustomerRepository(db=db)


def get_customer_service(
    repo: Annotated[SQLCustomerRepository, Depends(get_repository)],
) -> CustomerService:
    return CustomerService(repository=repo)


def get_current_user_id() -> int:
    return 1


def check_create_request_rate_limit(
    current_user_id: Annotated[int, Depends(get_current_user_id)],
) -> None:
    now = time.time()
    one_minute_ago = now - 60.0
    timestamps = [t for t in _create_request_rate_limit_tracker[current_user_id] if t > one_minute_ago]

    if len(timestamps) >= MAX_REQUESTS_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Límite de solicitudes excedido. Máximo {MAX_REQUESTS_PER_MINUTE} por minuto.",
        )
    timestamps.append(now)
    _create_request_rate_limit_tracker[current_user_id] = timestamps


def check_comment_rate_limit(
    current_user_id: Annotated[int, Depends(get_current_user_id)],
) -> None:
    now = time.time()
    one_minute_ago = now - 60.0
    timestamps = [t for t in _comment_rate_limit_tracker[current_user_id] if t > one_minute_ago]

    if len(timestamps) >= MAX_COMMENTS_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Límite de comentarios excedido. Máximo {MAX_COMMENTS_PER_MINUTE} por minuto.",
        )
    timestamps.append(now)
    _comment_rate_limit_tracker[current_user_id] = timestamps


def check_attachment_rate_limit(
    current_user_id: Annotated[int, Depends(get_current_user_id)],
) -> None:
    now = time.time()
    one_minute_ago = now - 60.0
    timestamps = [t for t in _attachment_rate_limit_tracker[current_user_id] if t > one_minute_ago]

    if len(timestamps) >= MAX_ATTACHMENTS_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Límite de subida de archivos excedido. Máximo {MAX_ATTACHMENTS_PER_MINUTE} por minuto.",
        )
    timestamps.append(now)
    _attachment_rate_limit_tracker[current_user_id] = timestamps


@router.post(
    "",
    response_model=CustomerRequestRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva solicitud de cliente",
    dependencies=[Depends(check_create_request_rate_limit)],
)
async def create_customer_request(
    request_in: CustomerRequestCreate,
    service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
) -> dict:
    return await service.create_request(user_id=current_user_id, request_in=request_in)


@router.get(
    "",
    response_model=list[CustomerRequestRead],
    status_code=status.HTTP_200_OK,
    summary="Listar solicitudes del usuario autenticado con paginación",
)
async def list_my_requests(
    service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    offset: Annotated[int, Query(ge=0, description="Desplazamiento de paginación")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Límite de elementos por página")] = 20,
) -> list[dict]:
    return await service.list_requests(user_id=current_user_id, offset=offset, limit=limit)


@router.get(
    "/{request_id}",
    response_model=CustomerRequestDetail,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalle completo de la solicitud con comentarios y adjuntos",
)
async def get_request_detail(
    request_id: int,
    service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
) -> dict:
    return await service.get_request_detail(request_id=request_id, user_id=current_user_id)


@router.get(
    "/{request_id}/status",
    response_model=dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Obtener el estado actual de la solicitud",
)
async def get_request_status(
    request_id: int,
    service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
) -> dict[str, str]:
    return await service.get_request_status(request_id=request_id, user_id=current_user_id)


@router.get(
    "/{request_id}/priority",
    response_model=PriorityRead,
    status_code=status.HTTP_200_OK,
    summary="Obtener información de prioridad de la solicitud",
)
async def get_request_priority(
    request_id: int,
    service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
) -> dict:
    return await service.get_request_priority(request_id=request_id, user_id=current_user_id)


@router.get(
    "/{request_id}/assignment",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Obtener el equipo y técnico asignados a la solicitud",
)
async def get_request_assignment(
    request_id: int,
    service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
) -> dict:
    return await service.get_request_assignment(request_id=request_id, user_id=current_user_id)


@router.post(
    "/{request_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Publicar un comentario en la solicitud (forzado a is_internal=False)",
    dependencies=[Depends(check_comment_rate_limit)],
)
async def add_comment_to_request(
    request_id: int,
    comment_in: CommentCreate,
    service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
) -> dict:
    return await service.add_comment(
        request_id=request_id,
        user_id=current_user_id,
        comment_in=comment_in,
    )


@router.post(
    "/{request_id}/attachments",
    response_model=AttachmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Subir un archivo adjunto a la solicitud",
    dependencies=[Depends(check_attachment_rate_limit)],
)
async def upload_attachment_to_request(
    request_id: int,
    file: Annotated[UploadFile, File(description="Archivo adjunto a subir")],
    service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
) -> dict:
    return await service.add_attachment(
        request_id=request_id,
        user_id=current_user_id,
        file=file,
    )
