<script>
  import { onMount } from 'svelte';
  import AppShell from '$lib/components/AppShell.svelte';
  import CalendarView from '$lib/components/CalendarView.svelte';
  import { selectedProfile } from '$lib/stores/profile';
  import { tasks } from '$lib/stores/tasks';
  import { api } from '$lib/services/api';

  let status = '';
  let viewDate = new Date();

  async function load() {
    if (!$selectedProfile) return;
    tasks.set(await api.getTasks($selectedProfile.id));
  }

  async function regenerate() {
    if (!$selectedProfile) return;
    status = `Generating AI tasks for ${viewDate.toLocaleString('en-US', { month: 'long', year: 'numeric' })}...`;
    const result = await api.generatePlan($selectedProfile, {
      year: viewDate.getFullYear(),
      month: viewDate.getMonth() + 1
    });
    tasks.set(await api.getTasks($selectedProfile.id));
    status = result.summary;
  }

  onMount(load);
</script>

<AppShell title="Calendar">
  <div class="space-y-4">
    <section class="glass-panel rounded-[2rem] p-6">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 class="font-display text-3xl">AI task calendar</h2>
          <p class="mt-2 text-sm text-stone-400">
            Monthly workout and nutrition scheduling for {$selectedProfile?.name ?? 'your selected profile'}.
          </p>
        </div>
        <button class="rounded-full bg-ember px-5 py-3 font-semibold text-black" on:click={regenerate}>Refresh AI Tasks</button>
      </div>

      {#if status}
        <div class="mt-4 rounded-2xl bg-white/5 px-4 py-3 text-sm text-stone-200">{status}</div>
      {/if}
    </section>

    <CalendarView tasks={$tasks} bind:viewDate />
  </div>
</AppShell>
