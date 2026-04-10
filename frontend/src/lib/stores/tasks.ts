import { writable } from 'svelte/store';
import type { TaskItem } from '$lib/types';

export const tasks = writable<TaskItem[]>([]);
