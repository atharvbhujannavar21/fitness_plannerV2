<script>
  export let tasks = [];

  $: workoutTasks = tasks.filter((task) => task.category === 'workout');
</script>

<div class="glass-panel rounded-[2rem] p-6">
  <div class="mb-5 flex items-center justify-between">
    <div>
      <p class="text-sm text-stone-400">Workout Summary</p>
      <h2 class="font-display text-2xl">Training Load</h2>
    </div>
    <div class="rounded-full bg-white/5 px-3 py-1 text-sm">{Math.min(workoutTasks.length, 7)} sessions</div>
  </div>

  <div class="max-h-[30rem] space-y-3 overflow-y-auto pr-1">
    {#if workoutTasks.length}
      {#each workoutTasks.slice(0, 7) as task}
        <div class="rounded-2xl border border-white/8 bg-white/5 p-4">
          <div class="flex items-center justify-between gap-3">
            <div class="font-semibold">{task.title}</div>
            {#if task.generated_by_ai}
              <span class="rounded-full bg-ember/15 px-2 py-1 text-xs text-amber-200">AI</span>
            {/if}
          </div>
          <p class="mt-2 text-sm text-stone-400">{task.description}</p>
        </div>
      {/each}
    {:else}
      <p class="rounded-2xl border border-dashed border-white/10 p-4 text-sm text-stone-400">
        No workout tasks yet. Generate an AI plan from the dashboard or calendar page.
      </p>
    {/if}
  </div>
</div>
