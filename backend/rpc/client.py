import importlib.machinery
import importlib.util
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from rpc.bootstrap import ensure_generated

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


class GRPCClient:
    def __init__(self):
        host = os.getenv("GRPC_HOST", "127.0.0.1")
        port = os.getenv("GRPC_PORT", "50051")
        self.channel = grpc.aio.insecure_channel(f"{host}:{port}")
        self.ai_stub = fitness_pb2_grpc.AIServiceStub(self.channel)
        self.calendar_stub = fitness_pb2_grpc.CalendarServiceStub(self.channel)

    async def generate_plan(self, profile: dict, year: int = 0, month: int = 0):
        request = fitness_pb2.PlanGenerateRequest(
            profile=fitness_pb2.UserProfile(**profile),
            year=year,
            month=month,
        )
        return await self.ai_stub.GeneratePlan(request)

    async def chat(self, profile: dict, history: list[dict], message: str):
        request = fitness_pb2.ChatRequest(
            profile=fitness_pb2.UserProfile(**profile),
            history=[fitness_pb2.ChatHistoryItem(**item) for item in history],
            message=message,
        )
        return await self.ai_stub.Chat(request)

    async def get_tasks(self, profile_id: str):
        return await self.calendar_stub.GetTasks(fitness_pb2.UserID(id=profile_id))

    async def add_task(self, task: dict):
        return await self.calendar_stub.AddTask(fitness_pb2.Task(**task))
