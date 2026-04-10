import asyncio
import os
from datetime import datetime

import grpc
from dotenv import load_dotenv

from grpc.bootstrap import ensure_generated

ensure_generated()

from grpc import fitness_pb2, fitness_pb2_grpc  # type: ignore  # noqa: E402
from models.tasks import ChatMessage, TaskCreate
from models.user import Profile
from services.ai_service import GroqAIService
from services.calendar_service import CalendarDomainService

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
    )


class AIServiceServicer(fitness_pb2_grpc.AIServiceServicer):
    def __init__(self):
        self.ai_service = GroqAIService()

    async def GeneratePlan(self, request, context):
        profile = Profile(
            id=request.id,
            name=request.name,
            age=request.age,
            weight=request.weight,
            height=request.height,
            goal=request.goal,
            created_at=datetime.fromisoformat(request.created_at.replace("Z", "+00:00")),
        )
        summary, tasks = await self.ai_service.generate_plan(profile)
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
