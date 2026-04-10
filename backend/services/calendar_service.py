from datetime import datetime

from api.database import get_tasks_collection
from models.tasks import TaskCreate
from services.serializers import serialize_task


class CalendarDomainService:
    def __init__(self):
        self.collection = get_tasks_collection()

    def get_tasks(self, profile_id: str) -> list[dict]:
        documents = self.collection.find({"profile_id": profile_id}).sort("date", 1)
        return [serialize_task(document) for document in documents]

    def add_task(self, task: TaskCreate) -> dict:
        payload = task.model_dump()
        payload["date"] = (
            task.date
            if isinstance(task.date, datetime)
            else datetime.fromisoformat(str(task.date).replace("Z", "+00:00"))
        )
        result = self.collection.insert_one(payload)
        document = self.collection.find_one({"_id": result.inserted_id})
        return serialize_task(document)

    def replace_generated_tasks(
        self,
        profile_id: str,
        tasks: list[TaskCreate],
        plan_scope: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict]:
        query: dict = {"profile_id": profile_id, "generated_by_ai": True}
        if plan_scope:
            query["plan_scope"] = plan_scope
        if start_date and end_date:
            query["date"] = {"$gte": start_date, "$lt": end_date}
        self.collection.delete_many(query)
        saved_tasks = []
        for task in tasks:
            saved_tasks.append(self.add_task(task))
        return saved_tasks
