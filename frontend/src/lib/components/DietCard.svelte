<script>
  export let tasks = [];

  $: dietTasks = tasks.filter((task) => task.category === 'diet');
</script>

<div class="glass-panel rounded-[2rem] p-6">
  <div class="mb-5 flex items-center justify-between">
    <div>
      <p class="text-sm text-stone-400">Diet Summary</p>
      <h2 class="font-display text-2xl">Nutrition Focus</h2>
    </div>
    <div class="rounded-full bg-white/5 px-3 py-1 text-sm">{Math.min(dietTasks.length, 7)} meals</div>
  </div>

  <div class="max-h-[30rem] space-y-3 overflow-y-auto pr-1">
    {#if dietTasks.length}
      {#each dietTasks.slice(0, 7) as task}
        <div class="rounded-2xl border border-white/8 bg-white/5 p-4">
          <div class="flex items-center justify-between gap-3">
            <div class="font-semibold">{task.title}</div>
            <span class="text-xs text-stone-400">{new Date(task.date).toLocaleDateString()}</span>
          </div>
          <p class="mt-2 text-sm text-stone-400">{task.description}</p>
        </div>
      {/each}
    {:else}
      <p class="rounded-2xl border border-dashed border-white/10 p-4 text-sm text-stone-400">
        No diet tasks yet. Generate a weekly plan to populate your calendar and nutrition feed.
      </p>
    {/if}
  </div>
</div>
