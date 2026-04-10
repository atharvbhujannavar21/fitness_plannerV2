export type Goal = 'fat_loss' | 'muscle_gain' | 'maintenance';

export interface Profile {
  id: string;
  name: string;
  age: number;
  weight: number;
  height: number;
  goal: Goal;
  created_at: string;
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
