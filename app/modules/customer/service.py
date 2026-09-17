from pathlib import Path
import uuid

from fastapi import HTTPException, UploadFile, status

from .repository import SQLCustomerRepository
from .schemas import CommentCreate, CustomerRequestCreate

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads" / "requests"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".pdf", ".txt", ".log", ".csv"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class CustomerService:
    def __init__(self, repository: SQLCustomerRepository):
        self.repo = repository
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    async def verify_ownership(self, request_id: int, user_id: int) -> dict:
        req = await self.repo.get_request_by_id(request_id)
        if not req:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la solicitud con ID {request_id}.",
            )
        if req.get("created_by") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: esta solicitud pertenece a otro usuario.",
            )
        return req

    async def create_request(self, user_id: int, request_in: CustomerRequestCreate) -> dict:
        return await self.repo.create_request(user_id=user_id, request_in=request_in)

    async def list_requests(self, user_id: int, offset: int, limit: int) -> list[dict]:
        return await self.repo.list_requests_by_user(user_id=user_id, offset=offset, limit=limit)

    async def get_request_detail(self, request_id: int, user_id: int) -> dict:
        await self.verify_ownership(request_id, user_id)
        detail = await self.repo.get_request_detail(request_id)
        if not detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el detalle de la solicitud con ID {request_id}.",
            )
        return detail

    async def get_request_status(self, request_id: int, user_id: int) -> dict[str, str]:
        await self.verify_ownership(request_id, user_id)
        status_val = await self.repo.get_request_status(request_id)
        if not status_val:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el estado de la solicitud con ID {request_id}.",
            )
        return {"status": status_val}

    async def get_request_priority(self, request_id: int, user_id: int) -> dict:
        await self.verify_ownership(request_id, user_id)
        priority = await self.repo.get_request_priority(request_id)
        if not priority:
            return {
                "id": None,
                "name": "PENDING",
                "level": None,
            }
        return priority

    async def get_request_assignment(self, request_id: int, user_id: int) -> dict:
        await self.verify_ownership(request_id, user_id)
        assignment = await self.repo.get_request_assignment(request_id)
        if not assignment:
            return {
                "team": None,
                "assignee": None,
            }
        return assignment

    async def add_comment(self, request_id: int, user_id: int, comment_in: CommentCreate) -> dict:
        await self.verify_ownership(request_id, user_id)
        return await self.repo.add_comment(
            request_id=request_id,
            user_id=user_id,
            comment_in=comment_in,
        )

    async def add_attachment(self, request_id: int, user_id: int, file: UploadFile) -> dict:
        await self.verify_ownership(request_id, user_id)

        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre del archivo no es válido.",
            )

        original_filename = Path(file.filename).name
        file_ext = Path(original_filename).suffix.lower()

        if file_ext not in ALLOWED_EXTENSIONS:
            permitidas = ", ".join(sorted(ALLOWED_EXTENSIONS))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La extensión '{file_ext or 'sin extensión'}' no está permitida. Válidas: {permitidas}",
            )

        unique_disk_filename = f"{uuid.uuid4().hex}_{original_filename}"
        request_upload_dir = UPLOAD_DIR / str(request_id)
        request_upload_dir.mkdir(parents=True, exist_ok=True)
        file_path_on_disk = request_upload_dir / unique_disk_filename

        total_bytes = 0
        try:
            with open(file_path_on_disk, "wb") as buffer:
                while chunk := await file.read(1024 * 1024):  # 1MB chunks
                    total_bytes += len(chunk)
                    if total_bytes > MAX_FILE_SIZE_BYTES:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"El archivo excede el tamaño máximo permitido de {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB.",
                        )
                    buffer.write(chunk)
        except HTTPException:
            if file_path_on_disk.exists():
                file_path_on_disk.unlink()
            raise
        except Exception as e:
            if file_path_on_disk.exists():
                file_path_on_disk.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"No se pudo guardar el archivo físico: {str(e)}",
            )
        finally:
            await file.close()

        if total_bytes == 0:
            if file_path_on_disk.exists():
                file_path_on_disk.unlink()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo está vacío (0 bytes).",
            )

        relative_file_path = f"/uploads/requests/{request_id}/{unique_disk_filename}"

        try:
            return await self.repo.add_attachment(
                request_id=request_id,
                uploaded_by=user_id,
                file_name=original_filename,
                file_path=relative_file_path,
            )
        except Exception as e:
            if file_path_on_disk.exists():
                file_path_on_disk.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al registrar metadatos en repositorio: {str(e)}",
            )
