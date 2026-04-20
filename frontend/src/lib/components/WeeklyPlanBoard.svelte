<script>
  export let tasks = [];
  export let profile = null;

  function toTime(value) {
    return new Date(value).getTime();
  }

  $: sortedTasks = [...tasks].sort((a, b) => toTime(a.date) - toTime(b.date));
  $: groupedDays = Array.from(
    sortedTasks.reduce((map, task) => {
      const dateKey = task.date.slice(0, 10);
      const existing = map.get(dateKey) ?? {
        date: task.date,
        workout: null,
        diet: null
      };

      if (task.category === 'workout') {
        existing.workout = task;
      }

      if (task.category === 'diet') {
        existing.diet = task;
      }

      map.set(dateKey, existing);
      return map;
    }, new Map()).values()
  );
</script>

<section class="glass-panel rounded-[2rem] p-6 lg:col-span-2">
  <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
    <div>
      <p class="text-sm text-stone-400">Weekly roadmap</p>
      <h2 class="font-display text-2xl">7-Day Exercise + Nutrition Plan</h2>
      <p class="mt-2 max-w-3xl text-sm text-stone-400">
        Built around {profile?.name ?? 'your profile'}, with {profile?.preferredWorkoutTime ?? 'your preferred'} training,
        a {profile?.dietPreference ?? 'balanced'} diet style, and a {profile?.goal ?? 'fitness'} goal.
      </p>
    </div>
    <div class="rounded-full bg-white/5 px-3 py-1 text-sm">
      {groupedDays.length}/7 days ready
    </div>
  </div>

  <div class="mt-5 max-h-[42rem] space-y-4 overflow-y-auto pr-1">
    {#if groupedDays.length}
      {#each groupedDays as day, index}
        <article class="rounded-[1.75rem] border border-white/8 bg-white/5 p-5">
          <div class="flex flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p class="text-xs uppercase tracking-[0.25em] text-amber-300">Day {index + 1}</p>
              <h3 class="mt-1 text-xl font-semibold">Day {index + 1}</h3>
            </div>
            <div class="rounded-full border border-white/10 bg-black/20 px-3 py-1 text-xs text-stone-300">
              {profile?.fitnessLevel ?? 'profile-aware'} plan
            </div>
          </div>

          <div class="mt-4 grid gap-4 xl:grid-cols-2">
            <div class="rounded-2xl border border-amber-500/10 bg-black/20 p-4">
              <p class="text-xs uppercase tracking-[0.2em] text-amber-300">Exercise</p>
              {#if day.workout}
                <h4 class="mt-2 font-semibold text-stone-100">{day.workout.title}</h4>
                <p class="mt-2 text-sm leading-6 text-stone-300">{day.workout.description}</p>
              {:else}
                <p class="mt-2 text-sm text-stone-400">No workout generated for this day yet.</p>
              {/if}
            </div>

            <div class="rounded-2xl border border-emerald-500/10 bg-black/20 p-4">
              <p class="text-xs uppercase tracking-[0.2em] text-emerald-300">Nutrition</p>
              {#if day.diet}
                <h4 class="mt-2 font-semibold text-stone-100">{day.diet.title}</h4>
                <p class="mt-2 text-sm leading-6 text-stone-300">{day.diet.description}</p>
              {:else}
                <p class="mt-2 text-sm text-stone-400">No nutrition guidance generated for this day yet.</p>
              {/if}
            </div>
          </div>
        </article>
      {/each}
    {:else}
      <p class="rounded-2xl border border-dashed border-white/10 p-4 text-sm text-stone-400">
        No weekly plan yet. Generate a weekly plan to see day 1 through day 7 workout and nutrition guidance here.
      </p>
    {/if}
  </div>
</section>
