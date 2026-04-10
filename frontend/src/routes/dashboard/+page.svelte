<script>
  import { onMount } from 'svelte';
  import AppShell from '$lib/components/AppShell.svelte';
  import BMICard from '$lib/components/BMICard.svelte';
  import WorkoutCard from '$lib/components/WorkoutCard.svelte';
  import DietCard from '$lib/components/DietCard.svelte';
  import ChatbotPanel from '$lib/components/ChatbotPanel.svelte';
  import { selectedProfile } from '$lib/stores/profile';
  import { tasks } from '$lib/stores/tasks';
  import { api } from '$lib/services/api';

  let generating = false;
  let summary = '';
  let error = '';
  let weeklyTasks = [];

  function toTime(value) {
    return new Date(value).getTime();
  }

  function extractWeeklyTasks(allTasks) {
    return allTasks
      .filter((task) => task.plan_scope === 'weekly')
      .sort((a, b) => toTime(a.date) - toTime(b.date));
  }

  async function loadTasks() {
    if (!$selectedProfile) return;
    try {
      const allTasks = await api.getTasks($selectedProfile.id);
      tasks.set(allTasks);
      weeklyTasks = extractWeeklyTasks(allTasks);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unable to load tasks.';
    }
  }

  async function generatePlan() {
    if (!$selectedProfile) return;
    generating = true;
    error = '';
    try {
      const result = await api.generatePlan($selectedProfile);
      summary = result.summary;
      const allTasks = await api.getTasks($selectedProfile.id);
      tasks.set(allTasks);
      weeklyTasks = extractWeeklyTasks(allTasks);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unable to generate plan.';
    } finally {
      generating = false;
    }
  }

  onMount(loadTasks);
</script>

<AppShell title="Dashboard">
  {#if $selectedProfile}
    <div class="grid gap-4 xl:grid-cols-[1.3fr_0.9fr]">
      <div class="space-y-4">
        <section class="glass-panel rounded-[2rem] p-6">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p class="text-sm text-stone-400">Personalized plan</p>
              <h2 class="font-display text-4xl">Hello, {$selectedProfile.name}</h2>
              <p class="mt-2 max-w-2xl text-sm text-stone-400">
                Generate a weekly AI workout and diet schedule tuned to your age, body metrics, and goal.
              </p>
            </div>
            <button class="rounded-full bg-ember px-5 py-3 font-semibold text-black" on:click={generatePlan} disabled={generating}>
              {generating ? 'Generating...' : 'Generate AI Plan'}
            </button>
          </div>

          {#if summary}
            <div class="mt-5 rounded-2xl bg-ember/10 px-4 py-3 text-sm text-amber-100">{summary}</div>
          {/if}

          {#if error}
            <div class="mt-5 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</div>
          {/if}
        </section>

        <div class="grid gap-4 lg:grid-cols-3">
          <BMICard profile={$selectedProfile} />
          <WorkoutCard tasks={weeklyTasks} />
          <DietCard tasks={weeklyTasks} />
        </div>
      </div>

      <div class="min-h-[720px]">
        <ChatbotPanel />
      </div>
    </div>
  {/if}
</AppShell>
