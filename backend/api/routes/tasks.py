from fastapi import APIRouter

from models.tasks import Task, TaskCreate
from services.calendar_service import CalendarDomainService

router = APIRouter()
calendar_service = CalendarDomainService()


@router.get("/tasks/{profile_id}", response_model=list[Task])
def get_tasks(profile_id: str):
    return calendar_service.get_tasks(profile_id)


@router.post("/tasks", response_model=Task)
def create_task(payload: TaskCreate):
    return calendar_service.add_task(payload)
