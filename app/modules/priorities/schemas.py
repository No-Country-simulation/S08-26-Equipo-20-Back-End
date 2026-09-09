from pydantic import BaseModel, ConfigDict, Field


class PriorityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    level: int = Field(ge=1)


class PriorityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    level: int | None = Field(default=None, ge=1)


class PriorityOut(BaseModel):
    id: int
    name: str
    level: int

    model_config = ConfigDict(from_attributes=True)
