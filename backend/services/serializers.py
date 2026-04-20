from typing import Any

from bson import ObjectId


PROFILE_DEFAULTS: dict[str, Any] = {
    "dietPreference": "non-veg",
    "dailyWaterIntake": 2.5,
    "dietaryGoal": "maintenance",
    "medicalConditions": ["none"],
    "injuriesOrLimitations": "",
    "workoutHoursPerDay": 1,
    "workoutDaysPerWeek": 5,
    "preferredWorkoutTime": "evening",
    "fitnessLevel": "beginner",
    "activityLevel": "moderate",
    "sleepHours": 8,
    "stressLevel": "moderate",
}


def serialize_profile(document: dict[str, Any]) -> dict[str, Any]:
    medical_conditions = document.get("medicalConditions", PROFILE_DEFAULTS["medicalConditions"])
    if not medical_conditions:
        medical_conditions = ["none"]
    elif "none" in medical_conditions:
        medical_conditions = ["none"]

    return {
        "id": str(document["_id"]),
        "name": document["name"],
        "age": document["age"],
        "weight": document["weight"],
        "height": document["height"],
        "goal": document["goal"],
        "dietPreference": document.get("dietPreference", PROFILE_DEFAULTS["dietPreference"]),
        "dailyWaterIntake": document.get("dailyWaterIntake", PROFILE_DEFAULTS["dailyWaterIntake"]),
        "dietaryGoal": document.get("dietaryGoal", PROFILE_DEFAULTS["dietaryGoal"]),
        "medicalConditions": medical_conditions,
        "injuriesOrLimitations": document.get("injuriesOrLimitations", PROFILE_DEFAULTS["injuriesOrLimitations"]),
        "workoutHoursPerDay": document.get("workoutHoursPerDay", PROFILE_DEFAULTS["workoutHoursPerDay"]),
        "workoutDaysPerWeek": document.get("workoutDaysPerWeek", PROFILE_DEFAULTS["workoutDaysPerWeek"]),
        "preferredWorkoutTime": document.get("preferredWorkoutTime", PROFILE_DEFAULTS["preferredWorkoutTime"]),
        "fitnessLevel": document.get("fitnessLevel", PROFILE_DEFAULTS["fitnessLevel"]),
        "activityLevel": document.get("activityLevel", PROFILE_DEFAULTS["activityLevel"]),
        "sleepHours": document.get("sleepHours", PROFILE_DEFAULTS["sleepHours"]),
        "stressLevel": document.get("stressLevel", PROFILE_DEFAULTS["stressLevel"]),
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
