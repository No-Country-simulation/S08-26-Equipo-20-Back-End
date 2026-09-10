from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    requires_approval: bool = False

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío")
        return value


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    requires_approval: bool | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    requires_approval: bool

    model_config = ConfigDict(from_attributes=True)


class CategoryList(BaseModel):
    items: list[CategoryResponse]
    total: int