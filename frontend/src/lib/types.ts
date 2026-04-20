export type Goal = 'fat_loss' | 'muscle_gain' | 'maintenance';
export type DietPreference = 'veg' | 'non-veg' | 'vegan' | 'eggetarian';
export type DietaryGoal = 'weight-loss' | 'muscle-gain' | 'maintenance';
export type MedicalCondition = 'diabetes' | 'hypertension' | 'thyroid' | 'none';
export type PreferredWorkoutTime = 'morning' | 'afternoon' | 'evening';
export type FitnessLevel = 'beginner' | 'intermediate' | 'advanced';
export type ActivityLevel = 'sedentary' | 'light' | 'moderate' | 'active';
export type StressLevel = 'low' | 'moderate' | 'high';

export interface Profile {
  id: string;
  name: string;
  age: number;
  weight: number;
  height: number;
  goal: Goal;
  dietPreference: DietPreference;
  dailyWaterIntake: number;
  dietaryGoal: DietaryGoal;
  medicalConditions: MedicalCondition[];
  injuriesOrLimitations: string;
  workoutHoursPerDay: number;
  workoutDaysPerWeek: number;
  preferredWorkoutTime: PreferredWorkoutTime;
  fitnessLevel: FitnessLevel;
  activityLevel: ActivityLevel;
  sleepHours: number;
  stressLevel: StressLevel;
  created_at: string;
}

export type ProfileInput = Omit<Profile, 'id' | 'created_at'>;

export const defaultProfileValues: ProfileInput = {
  name: '',
  age: 21,
  weight: 70,
  height: 175,
  goal: 'muscle_gain',
  dietPreference: 'non-veg',
  dailyWaterIntake: 2.5,
  dietaryGoal: 'maintenance',
  medicalConditions: ['none'],
  injuriesOrLimitations: '',
  workoutHoursPerDay: 1,
  workoutDaysPerWeek: 5,
  preferredWorkoutTime: 'evening',
  fitnessLevel: 'beginner',
  activityLevel: 'moderate',
  sleepHours: 8,
  stressLevel: 'moderate'
};

export function normalizeMedicalConditions(conditions: unknown): MedicalCondition[] {
  if (!Array.isArray(conditions) || conditions.length === 0) {
    return ['none'];
  }

  const valid = conditions.filter(
    (condition): condition is MedicalCondition =>
      condition === 'diabetes' ||
      condition === 'hypertension' ||
      condition === 'thyroid' ||
      condition === 'none'
  );

  if (valid.length === 0) {
    return ['none'];
  }

  if (valid.includes('none')) {
    return ['none'];
  }

  return Array.from(new Set(valid));
}

export function normalizeProfile(profile: Partial<Profile> | null | undefined): Profile | null {
  if (!profile) return null;

  return {
    id: profile.id ?? '',
    created_at: profile.created_at ?? new Date().toISOString(),
    ...defaultProfileValues,
    ...profile,
    medicalConditions: normalizeMedicalConditions(profile.medicalConditions)
  };
}

export interface TaskItem {
  id: string;
  profile_id: string;
  title: string;
  description: string;
  category: 'workout' | 'diet';
  date: string;
  generated_by_ai: boolean;
  plan_scope?: 'weekly' | 'monthly' | 'manual';
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}
