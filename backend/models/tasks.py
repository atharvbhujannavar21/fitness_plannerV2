from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


TaskCategory = Literal["workout", "diet"]


class TaskCreate(BaseModel):
    profile_id: str
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=1000)
    category: TaskCategory
    date: datetime
    generated_by_ai: bool = False
    plan_scope: Literal["weekly", "monthly", "manual"] = "manual"


class Task(TaskCreate):
    id: str


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatRequestModel(BaseModel):
    profile: dict
    history: list[ChatMessage] = Field(default_factory=list)
    message: str


class ChatResponseModel(BaseModel):
    reply: str


class PlanResponseModel(BaseModel):
    summary: str
    tasks: list[Task]


class PlanGenerateRequestModel(BaseModel):
    profile: dict
    year: int | None = None
    month: int | None = None


class DayRegenerateRequestModel(BaseModel):
    profile: dict
    date: datetime
