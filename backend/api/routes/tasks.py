from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException

from models.tasks import DayRegenerateRequestModel, Task, TaskCreate
from models.user import Profile
from services.ai_service import GroqAIService
from services.calendar_service import CalendarDomainService

router = APIRouter()
calendar_service = CalendarDomainService()
ai_service = GroqAIService()


@router.get("/tasks/{profile_id}", response_model=list[Task])
def get_tasks(profile_id: str):
    return calendar_service.get_tasks(profile_id)


@router.post("/tasks", response_model=Task)
def create_task(payload: TaskCreate):
    return calendar_service.add_task(payload)


@router.delete("/tasks/{task_id}", response_model=Task)
def delete_task(task_id: str):
    deleted = calendar_service.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return deleted


@router.delete("/tasks/profile/{profile_id}")
def clear_profile_tasks(profile_id: str):
    deleted_count = calendar_service.clear_tasks(profile_id)
    return {"deleted": deleted_count}


@router.post("/tasks/regenerate-day", response_model=list[Task])
async def regenerate_day(payload: DayRegenerateRequestModel):
    target_date = payload.date
    start_date = datetime(target_date.year, target_date.month, target_date.day, tzinfo=UTC)
    end_date = start_date + timedelta(days=1)

    profile = Profile.model_validate(payload.profile)
    summary, generated_tasks = await ai_service.generate_daily_plan(profile, target_date)
    replaced_tasks = calendar_service.replace_generated_tasks(
        profile.id,
        generated_tasks,
        start_date=start_date,
        end_date=end_date,
    )
    return replaced_tasks
