<script>
  import { createEventDispatcher } from "svelte";

  export let tasks = [];
  export let viewDate = new Date();
  export let selectedDate = null;

  const dispatch = createEventDispatcher();
  const weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  function changeMonth(offset) {
    viewDate = new Date(
      viewDate.getFullYear(),
      viewDate.getMonth() + offset,
      1,
    );
  }

  function selectDay(day) {
    dispatch("select", day);
  }

  function buildCalendarDays() {
    const year = viewDate.getFullYear();
    const month = viewDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const start = new Date(firstDay);
    start.setDate(firstDay.getDate() - firstDay.getDay());

    return Array.from({ length: 42 }, (_, index) => {
      const date = new Date(start);
      date.setDate(start.getDate() + index);
      const iso = date.toISOString().slice(0, 10);
      const dayTasks = tasks.filter((task) => task.date.slice(0, 10) === iso);

      return {
        date,
        iso,
        isCurrentMonth: date.getMonth() === month,
        items: dayTasks,
      };
    });
  }

  $: days = buildCalendarDays();
  $: selectedIso = selectedDate
    ? selectedDate.toISOString().slice(0, 10)
    : null;
</script>

<section class="glass-panel rounded-[2rem] p-5">
  <div
    class="mb-5 flex flex-col gap-4 md:flex-row md:items-center md:justify-between"
  >
    <div>
      <p class="text-sm text-stone-400">Monthly Planner</p>
      <h2 class="font-display text-3xl">
        {viewDate.toLocaleString("en-US", { month: "long", year: "numeric" })}
      </h2>
    </div>
    <div class="flex gap-3">
      <button
        class="rounded-full border border-white/10 px-4 py-2"
        on:click={() => changeMonth(-1)}>Prev</button
      >
      <button
        class="rounded-full border border-white/10 px-4 py-2"
        on:click={() => changeMonth(1)}>Next</button
      >
    </div>
  </div>

  <div
    class="grid grid-cols-7 gap-2 text-xs uppercase tracking-[0.2em] text-stone-500"
  >
    {#each weekDays as day}
      <div class="px-2 pb-2">{day}</div>
    {/each}
  </div>

  <div class="grid grid-cols-7 gap-2">
    {#each days as day}
      <button
        type="button"
        class={`min-h-32 rounded-2xl border p-3 text-left transition ${day.isCurrentMonth ? "border-white/10 bg-white/[0.03]" : "border-white/5 bg-white/[0.015] text-stone-600"} ${day.iso === selectedIso ? "border-amber-300 bg-amber-500/10" : ""}`}
        on:click={() => selectDay(day)}
      >
        <div class="mb-3 flex items-center justify-between">
          <span class="text-sm font-semibold">{day.date.getDate()}</span>
          {#if day.items.some((item) => item.generated_by_ai)}
            <span
              class="rounded-full bg-ember/15 px-2 py-1 text-[10px] text-amber-200"
              >AI</span
            >
          {/if}
        </div>

        <div class="space-y-2">
          {#each day.items.slice(0, 3) as item}
            <div
              class={`rounded-xl px-2 py-1 text-xs ${item.category === "workout" ? "bg-[#352312] text-[#ffc17a]" : "bg-[#1e2d1f] text-[#90f29b]"}`}
            >
              {item.title}
            </div>
          {/each}
          {#if day.items.length > 3}
            <div
              class="rounded-xl bg-white/5 px-2 py-1 text-[0.65rem] text-stone-300"
            >
              +{day.items.length - 3} more
            </div>
          {/if}
        </div>
      </button>
    {/each}
  </div>
</section>
