from datetime import UTC, datetime

from fastapi import APIRouter

from rpc.client import GRPCClient
from models.tasks import ChatRequestModel, ChatResponseModel, PlanGenerateRequestModel, PlanResponseModel
from models.tasks import TaskCreate
from services.calendar_service import CalendarDomainService

router = APIRouter()
grpc_client = GRPCClient()
calendar_service = CalendarDomainService()

def _month_bounds(year: int, month: int) -> tuple[datetime, datetime]:
    start = datetime(year, month, 1, tzinfo=UTC)
    if month == 12:
        end = datetime(year + 1, 1, 1, tzinfo=UTC)
    else:
        end = datetime(year, month + 1, 1, tzinfo=UTC)
    return start, end


@router.post("/generate-plan", response_model=PlanResponseModel)
async def generate_plan(payload: PlanGenerateRequestModel):
    profile = payload.profile
    response = await grpc_client.generate_plan(
        {
            "id": profile["id"],
            "name": profile["name"],
            "age": profile["age"],
            "weight": profile["weight"],
            "height": profile["height"],
            "goal": profile["goal"],
            "created_at": profile["created_at"],
        },
        year=payload.year or 0,
        month=payload.month or 0,
    )

    start_date = None
    end_date = None
    if payload.year and payload.month:
        start_date, end_date = _month_bounds(payload.year, payload.month)

    tasks = calendar_service.replace_generated_tasks(
        profile["id"],
        [
            TaskCreate(
                profile_id=item.profile_id,
                title=item.title,
                description=item.description,
                category=item.category,
                date=datetime.fromisoformat(item.date.replace("Z", "+00:00")),
                generated_by_ai=item.generated_by_ai,
                plan_scope=item.plan_scope or ("monthly" if payload.year and payload.month else "weekly"),
            )
            for item in response.tasks
        ],
        plan_scope="monthly" if payload.year and payload.month else "weekly",
        start_date=start_date,
        end_date=end_date,
    )
    return {"summary": response.summary, "tasks": tasks}


@router.post("/chat", response_model=ChatResponseModel)
async def chat(payload: ChatRequestModel):
    response = await grpc_client.chat(
        {
            "id": payload.profile["id"],
            "name": payload.profile["name"],
            "age": payload.profile["age"],
            "weight": payload.profile["weight"],
            "height": payload.profile["height"],
            "goal": payload.profile["goal"],
            "created_at": payload.profile["created_at"],
        },
        [
            {
                "role": item.role,
                "content": item.content,
                "timestamp": item.timestamp.isoformat(),
            }
            for item in payload.history
        ],
        payload.message,
    )
    return {"reply": response.reply}
