from fastapi import APIRouter
from sqlalchemy import select
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from app.core.dependencies import CurrentUser, DbDep
from app.modules.users.model import User, Role

router = APIRouter(prefix="/users", tags=["users"])

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role_id: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class UserListOut(BaseModel):
    items: List[UserOut]
    total: int

@router.get("/", response_model=UserListOut)
async def list_users(
    db: DbDep,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    offset: int = 0,
    limit: int = 100
):
    query = select(User)
    
    if role:
        query = query.join(Role).where(Role.name == role)
        
    if is_active is not None:
        query = query.where(User.is_active == is_active)
        
    users = await db.scalars(query.offset(offset).limit(limit))
    
    # Not exact total but good enough for frontend
    items = users.all()
    return {"items": items, "total": len(items)}
