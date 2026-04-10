<script lang="ts">
  import { chatHistory } from '$lib/stores/chat';
  import { selectedProfile } from '$lib/stores/profile';
  import { api } from '$lib/services/api';

  let message = '';
  let loading = false;
  let error = '';

  async function sendMessage() {
    if (!message.trim() || !$selectedProfile) return;

    const userMessage = {
      role: 'user' as const,
      content: message.trim(),
      timestamp: new Date().toISOString()
    };

    chatHistory.update((items) => [...items, userMessage]);
    const historySnapshot = [...$chatHistory, userMessage];
    const currentMessage = message;
    message = '';
    loading = true;
    error = '';

    try {
      const result = await api.chat($selectedProfile, historySnapshot, currentMessage);
      chatHistory.update((items) => [
        ...items,
        {
          role: 'assistant',
          content: result.reply,
          timestamp: new Date().toISOString()
        }
      ]);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unable to reach the AI coach.';
    } finally {
      loading = false;
    }
  }
</script>

<section class="glass-panel flex h-full flex-col rounded-[2rem]">
  <div class="rounded-t-[2rem] bg-ember px-6 py-5 text-black">
    <p class="text-sm font-semibold uppercase tracking-[0.3em]">AI Coach</p>
    <h2 class="font-display text-3xl">Chat with your fitness guide</h2>
    <p class="mt-2 text-sm/6 text-black/80">
      Context-aware coaching using your selected profile, goals, tasks, and prior messages.
    </p>
  </div>

  <div class="flex-1 space-y-4 overflow-y-auto px-5 py-5">
    {#if !$chatHistory.length}
      <div class="rounded-2xl border border-dashed border-white/10 p-4 text-sm text-stone-400">
        Ask about workouts, recovery, meal timing, protein intake, cardio, or strength progression.
      </div>
    {/if}

    {#each $chatHistory as item}
      <div class={`max-w-[92%] rounded-2xl px-4 py-3 text-sm ${item.role === 'user' ? 'ml-auto bg-[#5d43d5] text-white' : 'bg-white/5 text-stone-100'}`}>
        {item.content}
      </div>
    {/each}

    {#if error}
      <div class="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</div>
    {/if}
  </div>

  <div class="border-t border-white/10 p-4">
    <div class="flex gap-3">
      <input
        bind:value={message}
        class="min-w-0 flex-1 rounded-full border border-white/10 bg-white/5 px-4 py-3 outline-none"
        placeholder="Ask anything about training or diet..."
        on:keydown={(event) => event.key === 'Enter' && sendMessage()}
      />
      <button class="rounded-full bg-ember px-5 py-3 font-semibold text-black disabled:opacity-60" on:click={sendMessage} disabled={loading}>
        {loading ? '...' : 'Send'}
      </button>
    </div>
  </div>
</section>
