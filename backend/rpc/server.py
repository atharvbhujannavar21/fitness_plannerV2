import asyncio
import importlib.machinery
import importlib.util
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from models.tasks import ChatMessage, TaskCreate
from models.user import Profile
from rpc.bootstrap import ensure_generated
from services.ai_service import GroqAIService
from services.calendar_service import CalendarDomainService

ensure_generated()
project_root = Path(__file__).resolve().parent.parent
grpc_spec = importlib.machinery.PathFinder.find_spec(
    "grpc",
    [path for path in sys.path if Path(path or ".").resolve() != project_root],
)
if grpc_spec is None or grpc_spec.loader is None:
    raise RuntimeError("grpc package is not installed")
grpc = importlib.util.module_from_spec(grpc_spec)
sys.modules["grpc"] = grpc
grpc_spec.loader.exec_module(grpc)
sys.path.append(str(Path(__file__).resolve().parent.parent / "grpc"))
import fitness_pb2  # type: ignore  # noqa: E402
import fitness_pb2_grpc  # type: ignore  # noqa: E402

load_dotenv()


def _task_message(task: dict) -> fitness_pb2.Task:
    return fitness_pb2.Task(
        id=task.get("id", ""),
        profile_id=task["profile_id"],
        title=task["title"],
        description=task["description"],
        category=task["category"],
        date=task["date"].isoformat() if isinstance(task["date"], datetime) else str(task["date"]),
        generated_by_ai=task["generated_by_ai"],
        plan_scope=task.get("plan_scope", "manual"),
    )


class AIServiceServicer(fitness_pb2_grpc.AIServiceServicer):
    def __init__(self):
        self.ai_service = GroqAIService()

    async def GeneratePlan(self, request, context):
        profile = Profile(
            id=request.profile.id,
            name=request.profile.name,
            age=request.profile.age,
            weight=request.profile.weight,
            height=request.profile.height,
            goal=request.profile.goal,
            dietPreference=request.profile.diet_preference,
            dailyWaterIntake=request.profile.daily_water_intake,
            dietaryGoal=request.profile.dietary_goal,
            medicalConditions=list(request.profile.medical_conditions),
            injuriesOrLimitations=request.profile.injuries_or_limitations,
            workoutHoursPerDay=request.profile.workout_hours_per_day,
            workoutDaysPerWeek=request.profile.workout_days_per_week,
            preferredWorkoutTime=request.profile.preferred_workout_time,
            fitnessLevel=request.profile.fitness_level,
            activityLevel=request.profile.activity_level,
            sleepHours=request.profile.sleep_hours,
            stressLevel=request.profile.stress_level,
            created_at=datetime.fromisoformat(request.profile.created_at.replace("Z", "+00:00")),
        )
        summary, tasks = await self.ai_service.generate_plan(
            profile,
            year=request.year or None,
            month=request.month or None,
        )
        return fitness_pb2.PlanResponse(
            summary=summary,
            tasks=[
                _task_message(
                    {
                        "id": "",
                        "profile_id": task.profile_id,
                        "title": task.title,
                        "description": task.description,
                        "category": task.category,
                        "date": task.date,
                        "generated_by_ai": task.generated_by_ai,
                        "plan_scope": task.plan_scope,
                    }
                )
                for task in tasks
            ],
        )

    async def Chat(self, request, context):
        history = [
            ChatMessage(
                role=item.role,
                content=item.content,
                timestamp=datetime.fromisoformat(item.timestamp.replace("Z", "+00:00")),
            )
            for item in request.history
        ]
        reply = await self.ai_service.chat(
            {
                "id": request.profile.id,
                "name": request.profile.name,
                "age": request.profile.age,
                "weight": request.profile.weight,
                "height": request.profile.height,
                "goal": request.profile.goal,
                "dietPreference": request.profile.diet_preference,
                "dailyWaterIntake": request.profile.daily_water_intake,
                "dietaryGoal": request.profile.dietary_goal,
                "medicalConditions": list(request.profile.medical_conditions),
                "injuriesOrLimitations": request.profile.injuries_or_limitations,
                "workoutHoursPerDay": request.profile.workout_hours_per_day,
                "workoutDaysPerWeek": request.profile.workout_days_per_week,
                "preferredWorkoutTime": request.profile.preferred_workout_time,
                "fitnessLevel": request.profile.fitness_level,
                "activityLevel": request.profile.activity_level,
                "sleepHours": request.profile.sleep_hours,
                "stressLevel": request.profile.stress_level,
                "created_at": request.profile.created_at,
            },
            history,
            request.message,
        )
        return fitness_pb2.ChatResponse(reply=reply)


class CalendarServiceServicer(fitness_pb2_grpc.CalendarServiceServicer):
    def __init__(self):
        self.calendar_service = CalendarDomainService()

    async def GetTasks(self, request, context):
        tasks = self.calendar_service.get_tasks(request.id)
        return fitness_pb2.TaskList(tasks=[_task_message(task) for task in tasks])

    async def AddTask(self, request, context):
        created = self.calendar_service.add_task(
            TaskCreate(
                profile_id=request.profile_id,
                title=request.title,
                description=request.description,
                category=request.category,
                date=datetime.fromisoformat(request.date.replace("Z", "+00:00")),
                generated_by_ai=request.generated_by_ai,
                plan_scope=request.plan_scope or "manual",
            )
        )
        return fitness_pb2.TaskResponse(task=_task_message(created))


async def serve() -> None:
    server = grpc.aio.server()
    fitness_pb2_grpc.add_AIServiceServicer_to_server(AIServiceServicer(), server)
    fitness_pb2_grpc.add_CalendarServiceServicer_to_server(CalendarServiceServicer(), server)

    host = os.getenv("GRPC_HOST", "127.0.0.1")
    port = os.getenv("GRPC_PORT", "50051")
    server.add_insecure_port(f"{host}:{port}")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
