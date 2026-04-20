from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


Goal = Literal["fat_loss", "muscle_gain", "maintenance"]
DietPreference = Literal["veg", "non-veg", "vegan", "eggetarian"]
DietaryGoal = Literal["weight-loss", "muscle-gain", "maintenance"]
MedicalCondition = Literal["diabetes", "hypertension", "thyroid", "none"]
PreferredWorkoutTime = Literal["morning", "afternoon", "evening"]
FitnessLevel = Literal["beginner", "intermediate", "advanced"]
ActivityLevel = Literal["sedentary", "light", "moderate", "active"]
StressLevel = Literal["low", "moderate", "high"]


class ProfileBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    age: int = Field(ge=1, le=120)
    weight: float = Field(gt=0, le=500)
    height: float = Field(gt=0, le=300)
    goal: Goal
    dietPreference: DietPreference = "non-veg"
    dailyWaterIntake: float = Field(default=2.5, ge=0, le=15)
    dietaryGoal: DietaryGoal = "maintenance"
    medicalConditions: list[MedicalCondition] = Field(default_factory=lambda: ["none"])
    injuriesOrLimitations: str = Field(default="", max_length=300)
    workoutHoursPerDay: float = Field(default=1, ge=0.5, le=3)
    workoutDaysPerWeek: int = Field(default=5, ge=1, le=7)
    preferredWorkoutTime: PreferredWorkoutTime = "evening"
    fitnessLevel: FitnessLevel = "beginner"
    activityLevel: ActivityLevel = "moderate"
    sleepHours: float = Field(default=8, ge=0, le=24)
    stressLevel: StressLevel = "moderate"


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class Profile(ProfileBase):
    id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
