from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ObjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    story: str = Field(min_length=1, max_length=3000)
    room: str = Field(min_length=1, max_length=80)
    material: str = Field(min_length=1, max_length=80)
    mood: str = Field(min_length=1, max_length=80)
    color: str = Field(default="Unspecified", min_length=1, max_length=40)
    acquired_year: int | None = Field(default=None, ge=1000, le=2100)
    estimated_age: int | None = Field(default=None, ge=0, le=10000)
    significance: int = Field(default=3, ge=1, le=5)
    favorite: bool = False


class ObjectCreate(ObjectBase):
    pass


class ObjectUpdate(ObjectBase):
    pass


class ObjectRead(ObjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class FavoriteUpdate(BaseModel):
    favorite: bool


class ExhibitRequest(BaseModel):
    theme: str | None = Field(default=None, max_length=120)
    count: int = Field(default=4, ge=1, le=12)


class ExhibitResponse(BaseModel):
    title: str
    curatorial_note: str
    objects: list[ObjectRead]


class StatsResponse(BaseModel):
    total: int
    favorites: int
    average_significance: float
    oldest_acquired_year: int | None
    recent_count: int
    by_room: dict[str, int]
    by_material: dict[str, int]
    by_mood: dict[str, int]
