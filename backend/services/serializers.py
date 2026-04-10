from typing import Any

from bson import ObjectId


def serialize_profile(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(document["_id"]),
        "name": document["name"],
        "age": document["age"],
        "weight": document["weight"],
        "height": document["height"],
        "goal": document["goal"],
        "created_at": document["created_at"],
    }


def serialize_task(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(document["_id"]),
        "profile_id": document["profile_id"],
        "title": document["title"],
        "description": document["description"],
        "category": document["category"],
        "date": document["date"],
        "generated_by_ai": document["generated_by_ai"],
        "plan_scope": document.get("plan_scope", "manual"),
    }


def as_object_id(value: str) -> ObjectId:
    return ObjectId(value)
