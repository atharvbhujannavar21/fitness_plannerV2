import calendar
import json
import os
from datetime import UTC, datetime, timedelta

import httpx
from dotenv import load_dotenv

from models.tasks import ChatMessage, TaskCreate
from models.user import Profile

load_dotenv()


class GroqAIService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    async def _chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            return (
                "Groq is not configured yet. Add GROQ_API_KEY to the backend .env file to enable live coaching. "
                "Until then, use the generated profile-aware fallback guidance."
            )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    async def chat(self, profile: dict, history: list[ChatMessage], message: str) -> str:
        system_prompt = (
            "You are a concise, encouraging fitness coach. Answer using the selected local app profile as context. "
            "Give practical workout, nutrition, recovery, and habit advice. Mention safety when relevant."
        )
        history_text = "\n".join(f"{entry.role}: {entry.content}" for entry in history[-8:])
        user_prompt = (
            f"Selected profile: {json.dumps(profile)}\n"
            f"Conversation history:\n{history_text}\n"
            f"Latest user message: {message}\n"
            "Respond with actionable fitness advice tailored to the profile."
        )
        return await self._chat_completion(system_prompt, user_prompt)

    async def generate_plan(
        self,
        profile: Profile,
        year: int | None = None,
        month: int | None = None,
    ) -> tuple[str, list[TaskCreate]]:
        is_monthly = year is not None and month is not None
        system_prompt = (
            f"You create structured {'monthly' if is_monthly else 'weekly'} fitness plans. Output valid JSON only. "
            "Return an object with keys 'summary' and 'tasks'. "
            "Each task must include title, description, category, and date. "
            "For workout tasks, format description as: 'Exercise 1: X sets x Y reps | Exercise 2: X sets x Y reps | ...' (3-4 exercises). "
            "Use the user's health, diet, workout availability, sleep, stress, activity level, and limitations to personalize the plan."
        )
        profile_context = self._profile_context(profile)
        if is_monthly:
            start_dt, end_dt = self._month_bounds(year, month)
            user_prompt = (
                f"User context: {profile_context}. "
                f"Generate a full workout and diet plan for {calendar.month_name[month]} {year}, "
                f"starting on {start_dt.date().isoformat()} and ending on {(end_dt - timedelta(days=1)).date().isoformat()}. "
                "Include at least one workout task and one diet task for each day of the month. "
                "For each workout task, list 3-4 specific exercises with sets x reps (e.g., 'Squat: 4 sets x 8 reps'). "
                "Keep it realistic, varied, recovery-aware, and safe for a general fitness app."
            )
        else:
            start_dt = datetime.now(UTC).replace(hour=7, minute=0, second=0, microsecond=0)
            end_dt = start_dt + timedelta(days=7)
            user_prompt = (
                f"User context: {profile_context}. "
                f"Generate a 7-day workout and diet plan starting on {start_dt.date().isoformat()}. "
                "Include at least one workout task and one diet task per day. "
                "For each workout, list 3-4 specific exercises with sets x reps format. "
                "Keep it realistic, recovery-aware, and suitable for the user's schedule."
            )

        raw = self._sanitize_json_payload(await self._chat_completion(system_prompt, user_prompt))
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = self._fallback_plan(profile, start_dt, end_dt)

        tasks: list[TaskCreate] = []
        plan_scope = "monthly" if is_monthly else "weekly"
        for item in parsed["tasks"]:
            title = self._coerce_text(
                item.get("title"),
                self._default_task_title(item.get("category")),
            )
            description = self._coerce_text(
                item.get("description"),
                self._default_task_description(profile, item.get("category")),
            )
            if len(description) > 1000:
                description = description[:997].rstrip() + "..."
            category = self._normalize_task_category(item.get("category"), title, description)
            task_date = self._parse_task_date(item.get("date"), start_dt)

            tasks.append(
                TaskCreate(
                    profile_id=profile.id,
                    title=title,
                    description=description,
                    category=category,
                    date=task_date,
                    generated_by_ai=True,
                    plan_scope=plan_scope,
                )
            )
        return parsed["summary"], tasks

    async def generate_daily_plan(self, profile: Profile, target_date: datetime) -> tuple[str, list[TaskCreate]]:
        system_prompt = (
            "You create a single-day fitness schedule. Output valid JSON only. "
            "Return an object with keys 'summary' and 'tasks'. "
            "Each task must include title, description, category, and date. "
            "For workout tasks, format description as: 'Exercise 1: X sets x Y reps | Exercise 2: X sets x Y reps | ...'. "
            "Use the user's profile details, workout availability, diet preferences, recovery, and safety to personalize the day."
        )
        profile_context = self._profile_context(profile)
        date_label = target_date.date().isoformat()
        user_prompt = (
            f"User context: {profile_context}. "
            f"Generate one workout task and one diet task for {date_label}. "
            "For the workout: include 3-4 specific exercises with sets x reps (e.g., 'Barbell Bench Press: 4 sets x 6 reps'). "
            "Keep the plan realistic, balanced, safe, and aligned with the user's fitness goal."
        )

        raw = self._sanitize_json_payload(await self._chat_completion(system_prompt, user_prompt))
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = self._fallback_day(profile, target_date)

        tasks: list[TaskCreate] = []
        for item in parsed["tasks"]:
            title = self._coerce_text(
                item.get("title"),
                self._default_task_title(item.get("category")),
            )
            description = self._coerce_text(
                item.get("description"),
                self._default_task_description(profile, item.get("category")),
            )
            if len(description) > 1000:
                description = description[:997].rstrip() + "..."
            category = self._normalize_task_category(item.get("category"), title, description)
            task_date = self._parse_task_date(item.get("date"), target_date)

            tasks.append(
                TaskCreate(
                    profile_id=profile.id,
                    title=title,
                    description=description,
                    category=category,
                    date=task_date,
                    generated_by_ai=True,
                    plan_scope="manual",
                )
            )
        return parsed["summary"], tasks

    def _fallback_day(self, profile: Profile, target_date: datetime) -> dict:
        workout_title = {
            "fat_loss": "Conditioning Circuit",
            "muscle_gain": "Pull Strength",
            "maintenance": "Balanced Strength",
        }[profile.goal]
        meal_focus = {
            "weight-loss": "portion-aware, high-protein meals",
            "muscle-gain": "protein-forward meals with extra carbs",
            "maintenance": "balanced meals and hydration",
        }[profile.dietaryGoal]
        exercise_details = (
            "Barbell Deadlift: 4 sets x 6 reps | Bent-over Row: 4 sets x 8 reps | "
            "Lat Pulldown: 3 sets x 10 reps | Face Pulls: 3 sets x 12 reps"
        )
        description = (
            f"{exercise_details}. A {profile.workoutHoursPerDay:g}-hour {profile.preferredWorkoutTime} session for a {profile.fitnessLevel} athlete. "
            f"Respect injuries or limitations: {profile.injuriesOrLimitations or 'none'}. "
            f"Support goal: {profile.goal}."
        )
        recovery_note = (
            f"Aim for {profile.sleepHours} hours of sleep, {profile.dailyWaterIntake}L water, "
            f"and monitor stress at {profile.stressLevel}."
        )
        return {
            "summary": f"Fallback daily plan for {profile.name} on {target_date.date().isoformat()}.",
            "tasks": [
                {
                    "title": workout_title,
                    "description": description,
                    "category": "workout",
                    "date": target_date.isoformat(),
                },
                {
                    "title": "Nutrition Prep",
                    "description": f"Follow {meal_focus}. {recovery_note}",
                    "category": "diet",
                    "date": target_date.isoformat(),
                },
            ],
        }

    def _sanitize_json_payload(self, content: str) -> str:
        stripped = content.strip()
        if stripped.startswith("```"):
            stripped = stripped.strip("`")
            if stripped.startswith("json"):
                stripped = stripped[4:]
        return stripped.strip()

    def _month_bounds(self, year: int, month: int) -> tuple[datetime, datetime]:
        start = datetime(year, month, 1, 7, 0, 0, tzinfo=UTC)
        if month == 12:
            end = datetime(year + 1, 1, 1, 7, 0, 0, tzinfo=UTC)
        else:
            end = datetime(year, month + 1, 1, 1, 7, 0, 0, tzinfo=UTC)
        return start, end

    def _fallback_plan(self, profile: Profile, start: datetime, end: datetime) -> dict:
        summary = (
            f"Fallback plan for {profile.name}: {profile.fitnessLevel}-appropriate training with nutrition, hydration, and recovery support for {profile.goal}."
        )
        tasks = []
        workout_focus = {
            "fat_loss": ["Conditioning Circuit", "Lower Body HIIT", "Power Walk + Core"],
            "muscle_gain": ["Push Strength", "Pull Strength", "Leg Hypertrophy"],
            "maintenance": ["Full Body Strength", "Mobility Flow", "Zone 2 Cardio"],
        }[profile.goal]
        meal_focus = {
            "weight-loss": "portion-aware, high-protein meals",
            "muscle-gain": "protein-forward meals with extra carbs",
            "maintenance": "balanced meals and hydration",
        }[profile.dietaryGoal]
        condition_note = self._condition_note(profile)
        recovery_note = (
            f"Aim for {profile.sleepHours} hours of sleep, {profile.dailyWaterIntake}L water, and {profile.stressLevel} stress load management."
        )
        workout_description = (
            f"{profile.workoutHoursPerDay:g}-hour {profile.preferredWorkoutTime} session for a {profile.fitnessLevel} athlete, "
            f"scheduled {profile.workoutDaysPerWeek} days/week with {profile.activityLevel} baseline activity."
        )
        if profile.injuriesOrLimitations:
            workout_description += f" Respect this limitation: {profile.injuriesOrLimitations}."
        if condition_note:
            workout_description += f" Health note: {condition_note}."

        total_days = (end.date() - start.date()).days
        exercise_sets = [
            "Barbell Deadlift: 4 sets x 6 reps",
            "Bent-over Row: 4 sets x 8 reps",
            "Lat Pulldown: 3 sets x 10 reps",
            "Face Pulls: 3 sets x 12 reps",
        ]
        for offset in range(total_days):
            day = start + timedelta(days=offset)
            workout_desc = (
                f"{exercise_sets[0]} | {exercise_sets[1]} | {exercise_sets[2]} | {exercise_sets[3]}. "
                f"{workout_description} Tailor intensity to support {profile.goal} with progressive overload and recovery cues."
            )
            tasks.append(
                {
                    "title": workout_focus[offset % len(workout_focus)],
                    "description": workout_desc,
                    "category": "workout",
                    "date": day.isoformat(),
                }
            )
            tasks.append(
                {
                    "title": f"Nutrition Prep Day {offset + 1}",
                    "description": f"Follow {meal_focus} for a {profile.dietPreference} diet. {recovery_note}",
                    "category": "diet",
                    "date": (day + timedelta(hours=5)).isoformat(),
                }
            )

        return {"summary": summary, "tasks": tasks}

    def _profile_context(self, profile: Profile) -> str:
        medical_conditions = ", ".join(profile.medicalConditions)
        limitations = profile.injuriesOrLimitations or "none"
        return (
            f"{profile.name}, age {profile.age}, {profile.weight}kg, {profile.height}cm, goal {profile.goal}, "
            f"diet {profile.dietPreference}, dietary goal {profile.dietaryGoal}, water {profile.dailyWaterIntake}L/day, "
            f"medical conditions: {medical_conditions}, injuries or limitations: {limitations}, "
            f"training availability {profile.workoutHoursPerDay} hours/day for {profile.workoutDaysPerWeek} days/week, "
            f"preferred workout time {profile.preferredWorkoutTime}, fitness level {profile.fitnessLevel}, "
            f"activity level {profile.activityLevel}, sleep {profile.sleepHours} hours, stress {profile.stressLevel}"
        )

    def _condition_note(self, profile: Profile) -> str:
        conditions = [condition for condition in profile.medicalConditions if condition != "none"]
        return ", ".join(conditions)

    def _normalize_task_category(self, raw_category: str | None, title: str, description: str) -> str:
        normalized = (raw_category or "").strip().lower()
        if normalized in {"workout", "diet"}:
            return normalized

        if normalized in {"meal", "meals", "nutrition", "food", "dietary", "hydration"}:
            return "diet"

        if normalized in {"exercise", "training", "strength", "cardio", "mobility"}:
            return "workout"

        content = f"{title} {description}".lower()
        diet_keywords = {
            "meal",
            "meals",
            "nutrition",
            "protein",
            "calorie",
            "calories",
            "hydrate",
            "hydration",
            "water",
            "snack",
            "breakfast",
            "lunch",
            "dinner",
            "diet",
        }
        workout_keywords = {
            "sets",
            "reps",
            "workout",
            "exercise",
            "training",
            "strength",
            "cardio",
            "run",
            "squat",
            "bench",
            "deadlift",
            "session",
        }

        if any(keyword in content for keyword in diet_keywords):
            return "diet"
        if any(keyword in content for keyword in workout_keywords):
            return "workout"

        return "diet" if normalized == "recovery" else "workout"

    def _coerce_text(self, value: object, fallback: str) -> str:
        text = str(value or "").strip()
        return text or fallback

    def _parse_task_date(self, raw_date: object, fallback: datetime) -> datetime:
        text = str(raw_date or "").strip()
        if not text:
            return fallback
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return fallback

    def _default_task_title(self, raw_category: str | None) -> str:
        category = (raw_category or "").strip().lower()
        if category in {"diet", "meal", "meals", "nutrition", "food", "hydration", "recovery"}:
            return "Nutrition Plan"
        return "Workout Plan"

    def _default_task_description(self, profile: Profile, raw_category: str | None) -> str:
        category = (raw_category or "").strip().lower()
        if category in {"diet", "meal", "meals", "nutrition", "food", "hydration", "recovery"}:
            return (
                f"Follow a {profile.dietPreference} nutrition plan that supports {profile.dietaryGoal}, "
                f"drink {profile.dailyWaterIntake}L of water, and prioritize recovery habits."
            )
        return (
            f"Complete a {profile.workoutHoursPerDay:g}-hour {profile.preferredWorkoutTime} workout "
            f"matched to a {profile.fitnessLevel} athlete working toward {profile.goal}."
        )
