from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    requires_approval: bool = False


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    requires_approval: bool | None = None


class CategoryOut(BaseModel):
    id: int
    name: str
    description: str | None
    requires_approval: bool

    model_config = ConfigDict(from_attributes=True)
