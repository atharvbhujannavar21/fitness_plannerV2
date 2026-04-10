import { writable } from 'svelte/store';
import type { ChatMessage } from '$lib/types';

export const chatHistory = writable<ChatMessage[]>([]);
