from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


Goal = Literal["fat_loss", "muscle_gain", "maintenance"]


class ProfileBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    age: int = Field(ge=1, le=120)
    weight: float = Field(gt=0, le=500)
    height: float = Field(gt=0, le=300)
    goal: Goal


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class Profile(ProfileBase):
    id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
