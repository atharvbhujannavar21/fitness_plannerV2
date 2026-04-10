import { PUBLIC_API_BASE_URL } from '$env/static/public';
import type { ChatMessage, Profile, TaskItem } from '$lib/types';

const API_BASE = PUBLIC_API_BASE_URL || 'http://localhost:8000';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers ?? {})
    },
    ...options
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || 'Request failed');
  }

  return response.json() as Promise<T>;
}

export const api = {
  getProfiles: () => request<Profile[]>('/profiles'),
  createProfile: (body: Omit<Profile, 'id' | 'created_at'>) =>
    request<Profile>('/profiles', { method: 'POST', body: JSON.stringify(body) }),
  updateProfile: (id: string, body: Omit<Profile, 'id' | 'created_at'>) =>
    request<Profile>(`/profiles/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteProfile: (id: string) => request<{ status: string }>(`/profiles/${id}`, { method: 'DELETE' }),
  getTasks: (profileId: string) => request<TaskItem[]>(`/tasks/${profileId}`),
  addTask: (body: Omit<TaskItem, 'id'>) => request<TaskItem>('/tasks', { method: 'POST', body: JSON.stringify(body) }),
  generatePlan: (profile: Profile, options?: { year?: number; month?: number }) =>
    request<{ summary: string; tasks: TaskItem[] }>('/generate-plan', {
      method: 'POST',
      body: JSON.stringify({
        profile,
        year: options?.year,
        month: options?.month
      })
    }),
  chat: (profile: Profile, history: ChatMessage[], message: string) =>
    request<{ reply: string }>('/chat', {
      method: 'POST',
      body: JSON.stringify({ profile, history, message })
    })
};
