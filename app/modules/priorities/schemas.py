from pydantic import BaseModel, ConfigDict, Field, field_validator


class PriorityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    level: int = Field(ge=1, le=10)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío")
        return value


class PriorityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    level: int | None = Field(default=None, ge=1, le=10)


class PriorityResponse(BaseModel):
    id: int
    name: str
    level: int

    model_config = ConfigDict(from_attributes=True)


class PriorityList(BaseModel):
    items: list[PriorityResponse]
    total: int