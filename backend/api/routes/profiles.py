from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from api.database import get_profiles_collection, get_tasks_collection
from models.user import Profile, ProfileCreate, ProfileUpdate
from services.serializers import as_object_id, serialize_profile

router = APIRouter()
collection = get_profiles_collection()
tasks_collection = get_tasks_collection()


@router.get("/profiles", response_model=list[Profile])
def get_profiles():
    documents = collection.find().sort("created_at", 1)
    return [serialize_profile(document) for document in documents]


@router.post("/profiles", response_model=Profile)
def create_profile(payload: ProfileCreate):
    document = payload.model_dump()
    document["created_at"] = datetime.now(timezone.utc)
    result = collection.insert_one(document)
    created = collection.find_one({"_id": result.inserted_id})
    return serialize_profile(created)


@router.put("/profiles/{profile_id}", response_model=Profile)
def update_profile(profile_id: str, payload: ProfileUpdate):
    result = collection.update_one({"_id": as_object_id(profile_id)}, {"$set": payload.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    updated = collection.find_one({"_id": as_object_id(profile_id)})
    return serialize_profile(updated)


@router.delete("/profiles/{profile_id}")
def delete_profile(profile_id: str):
    result = collection.delete_one({"_id": as_object_id(profile_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    tasks_collection.delete_many({"profile_id": profile_id})
    return {"status": "deleted"}
