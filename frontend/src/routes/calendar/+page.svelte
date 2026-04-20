<script>
  import { onMount } from "svelte";
  import AppShell from "$lib/components/AppShell.svelte";
  import CalendarView from "$lib/components/CalendarView.svelte";
  import { selectedProfile } from "$lib/stores/profile";
  import { tasks } from "$lib/stores/tasks";
  import { api } from "$lib/services/api";

  let status = "";
  let viewDate = new Date();
  let selectedDate = null;
  let selectedDayOpen = false;
  let newTaskTitle = "";
  let newTaskDescription = "";
  let newTaskCategory = "workout";

  function parseExercises(description) {
    if (!description) return null;

    const normalized = description
      .replace(/\r\n/g, "\n")
      .replace(/•/g, "|")
      .replace(/\s*[–—-]\s*/g, "|");

    const patterns = [
      /(.+?)[:]\s*(\d+)\s*sets?\s*(?:x|×|of)\s*(\d+)\s*reps?/gi,
      /(.+?)\s*(\d+)\s*sets?\s*(?:x|×|of)\s*(\d+)\s*reps?/gi,
      /(.+?)[:]?\s*(\d+)x(\d+)\b/gi,
    ];

    const exercises = [];
    const seen = new Set();

    for (const regex of patterns) {
      let match;
      while ((match = regex.exec(normalized)) !== null) {
        const name = match[1].trim();
        const sets = match[2];
        const reps = match[3];
        const key = `${name}|${sets}|${reps}`;
        if (!seen.has(key) && name && sets && reps) {
          seen.add(key);
          exercises.push({ name, sets, reps });
        }
      }
    }

    if (exercises.length > 0) {
      return exercises;
    }

    const fragments = normalized
      .split(/\||\n|;/)
      .map((part) => part.trim())
      .filter(Boolean);
    for (const fragment of fragments) {
      const fallbackMatch =
        /(.+?)[:]?\s*(\d+)\s*sets?\s*(?:x|×|of)\s*(\d+)\s*reps?/i.exec(
          fragment,
        ) || /(.+?)[:]?\s*(\d+)x(\d+)\b/i.exec(fragment);
      if (fallbackMatch) {
        const name = fallbackMatch[1].trim();
        const sets = fallbackMatch[2];
        const reps = fallbackMatch[3];
        const key = `${name}|${sets}|${reps}`;
        if (!seen.has(key) && name && sets && reps) {
          seen.add(key);
          exercises.push({ name, sets, reps });
        }
      }
    }

    return exercises.length > 0 ? exercises : null;
  }

  async function load() {
    if (!$selectedProfile) return;
    tasks.set(await api.getTasks($selectedProfile.id));
  }

  async function regenerateMonth() {
    if (!$selectedProfile) return;
    status = `Generating AI tasks for ${viewDate.toLocaleString("en-US", { month: "long", year: "numeric" })}...`;
    const result = await api.generatePlan($selectedProfile, {
      year: viewDate.getFullYear(),
      month: viewDate.getMonth() + 1,
    });
    tasks.set(await api.getTasks($selectedProfile.id));
    selectedDate = null;
    selectedDayOpen = false;
    status = result.summary;
  }

  async function removeTask(taskId) {
    if (!taskId) return;
    await api.deleteTask(taskId);
    tasks.set(await api.getTasks($selectedProfile.id));
    status = "Task removed successfully.";
  }

  async function addNewTask() {
    if (
      !$selectedProfile ||
      !selectedDate ||
      !newTaskTitle.trim() ||
      !newTaskDescription.trim()
    ) {
      status = "Please fill in all fields.";
      return;
    }

    try {
      const dateString = selectedDate.toISOString();
      const newTask = {
        profile_id: $selectedProfile.id,
        title: newTaskTitle,
        description: newTaskDescription,
        category: newTaskCategory,
        date: dateString,
        generated_by_ai: false,
        plan_scope: "manual",
      };

      await api.addTask(newTask);
      tasks.set(await api.getTasks($selectedProfile.id));

      // Reset form
      newTaskTitle = "";
      newTaskDescription = "";
      newTaskCategory = "workout";
      status = "Task added successfully!";
    } catch (error) {
      status = "Failed to add task. Please try again.";
      console.error(error);
    }
  }

  async function regenerateSelectedDay() {
    if (!$selectedProfile || !selectedDate) return;
    const dateString = selectedDate.toISOString().slice(0, 10);
    status = `Regenerating tasks for ${selectedDate.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}...`;
    const result = await api.regenerateDay($selectedProfile, dateString);
    tasks.set(await api.getTasks($selectedProfile.id));
    status =
      result.length > 0
        ? `Regenerated ${result.length} tasks for ${dateString}.`
        : "No tasks regenerated.";
  }

  async function clearCalendar() {
    if (!$selectedProfile) return;
    await api.clearTasks($selectedProfile.id);
    tasks.set([]);
    selectedDate = null;
    selectedDayOpen = false;
    status = "Calendar cleared. Click any day to generate a new plan.";
  }

  async function downloadTasksPdf() {
    if ($tasks.length === 0) {
      status =
        "No tasks available yet. Generate the calendar before exporting.";
      return;
    }

    try {
      const sortedTasks = [...$tasks].sort((a, b) =>
        a.date.localeCompare(b.date),
      );
      const grouped = sortedTasks.reduce((acc, task) => {
        const dateKey = task.date.slice(0, 10);
        if (!acc[dateKey]) acc[dateKey] = [];
        acc[dateKey].push(task);
        return acc;
      }, {});

      let content = "FitFusion Task Export\n";
      content += `Generated: ${new Date().toLocaleString()}\n`;
      content += `Profile: ${$selectedProfile?.name ?? "Unknown"}\n`;
      content += "=".repeat(80) + "\n\n";

      for (const date of Object.keys(grouped).sort()) {
        content += `📅 ${new Date(date).toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}\n`;
        content += "-".repeat(80) + "\n";

        grouped[date].forEach((task) => {
          const icon = task.category === "workout" ? "💪" : "🍽️";
          content += `\n${icon} ${task.category.toUpperCase()}: ${task.title}\n`;
          const exercises =
            task.category === "workout"
              ? parseExercises(task.description)
              : null;
          if (Array.isArray(exercises)) {
            exercises.forEach((ex) => {
              content += `   • ${ex.name}: ${ex.sets} sets x ${ex.reps} reps\n`;
            });
          } else {
            content += `   ${task.description}\n`;
          }
        });
        content += "\n" + "=".repeat(80) + "\n\n";
      }

      const blob = new Blob([content], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `fitfusion-tasks-${new Date().toISOString().slice(0, 10)}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      status = `Tasks exported: fitfusion-tasks-${new Date().toISOString().slice(0, 10)}.txt`;
    } catch (error) {
      status = "Failed to export tasks. Please try again.";
      console.error(error);
    }
  }

  async function handleSelect(event) {
    selectedDate = event.detail.date;
    if ($tasks.length === 0 && $selectedProfile) {
      status = "Calendar is empty. Generating tasks first...";
      await regenerateMonth();
    }
    selectedDayOpen = true;
  }

  function closeSelectedDay() {
    selectedDayOpen = false;
  }

  const todayIso = new Date().toISOString().slice(0, 10);

  $: selectedIso = selectedDate
    ? selectedDate.toISOString().slice(0, 10)
    : null;
  $: todayTasks = $tasks.filter((task) => task.date.slice(0, 10) === todayIso);
  $: selectedDayTasks = selectedIso
    ? $tasks.filter((task) => task.date.slice(0, 10) === selectedIso)
    : [];

  onMount(load);
</script>

<AppShell title="Calendar">
  <div class="space-y-4">
    <section class="glass-panel rounded-[2rem] p-6">
      <div
        class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between"
      >
        <div>
          <h2 class="font-display text-3xl">AI task calendar</h2>
          <p class="mt-2 text-sm text-stone-400">
            Monthly workout and nutrition scheduling for {$selectedProfile?.name ??
              "your selected profile"}.
          </p>
        </div>
        <div class="flex flex-wrap gap-3">
          <button
            class="rounded-full bg-ember px-5 py-3 font-semibold text-black"
            on:click={regenerateMonth}>Refresh AI Tasks</button
          >
          <button
            class="rounded-full border border-white/10 bg-white/5 px-5 py-3 font-semibold text-white hover:bg-white/10"
            on:click={clearCalendar}>Clear Calendar</button
          >
          <button
            class="rounded-full border border-white/10 bg-white/5 px-5 py-3 font-semibold text-white hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed"
            on:click={downloadTasksPdf}
            disabled={$tasks.length === 0}
          >
            Download PDF
          </button>
        </div>
      </div>

      {#if status}
        <div
          class="mt-4 rounded-2xl bg-white/5 px-4 py-3 text-sm text-stone-200"
        >
          {status}
        </div>
      {/if}
    </section>

    <div class="grid gap-4 xl:grid-cols-[1.6fr_0.9fr]">
      <div>
        <CalendarView
          tasks={$tasks}
          bind:viewDate
          {selectedDate}
          on:select={handleSelect}
        />
      </div>

      <aside class="space-y-4">
        <section class="glass-panel rounded-[2rem] p-6">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-sm text-stone-400">Today's tasks</p>
              <h3 class="mt-2 text-2xl font-semibold">
                {new Date().toLocaleDateString("en-US", {
                  month: "long",
                  day: "numeric",
                })}
              </h3>
            </div>
            <span
              class="rounded-full bg-ember px-4 py-2 text-sm font-semibold text-black"
              >{todayTasks.length} items</span
            >
          </div>

          {#if todayTasks.length > 0}
            <div class="mt-5 space-y-3">
              {#each todayTasks as task}
                <div class="rounded-3xl border border-white/10 bg-black/20 p-4">
                  <div class="flex items-center justify-between gap-3">
                    <div>
                      <p class="text-sm text-stone-400">
                        {task.category === "workout" ? "Workout" : "Diet"}
                      </p>
                      <h4 class="mt-1 font-semibold">{task.title}</h4>
                    </div>
                    <span
                      class="rounded-full bg-white/5 px-3 py-1 text-xs uppercase tracking-[0.15em] text-stone-300"
                      >{task.plan_scope ?? "manual"}</span
                    >
                  </div>
                  {#if task.category === "workout"}
                    {#if parseExercises(task.description)?.length}
                      <div class="mt-3 space-y-2">
                        {#each parseExercises(task.description) as exercise}
                          <div
                            class="flex items-center gap-2 text-sm text-stone-300"
                          >
                            <span class="text-amber-400">•</span>
                            <span
                              ><strong>{exercise.name}:</strong>
                              {exercise.sets} sets × {exercise.reps} reps</span
                            >
                          </div>
                        {/each}
                      </div>
                    {:else}
                      <p class="mt-3 text-sm leading-6 text-stone-300">
                        {task.description}
                      </p>
                    {/if}
                  {:else}
                    <p class="mt-3 text-sm leading-6 text-stone-300">
                      {task.description}
                    </p>
                  {/if}
                </div>
              {/each}
            </div>
          {:else}
            <p class="mt-5 text-sm text-stone-400">
              No tasks for today yet. Select a profile and regenerate tasks to
              populate your daily schedule.
            </p>
          {/if}
        </section>
      </aside>
    </div>

    {#if selectedDayOpen}
      <div
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      >
        <section
          class="glass-panel relative w-[min(95%,900px)] max-h-[85vh] overflow-auto rounded-[2rem] p-6"
          role="dialog"
          aria-modal="true"
          tabindex="-1"
        >
          <div class="mb-5 flex items-center justify-between gap-4">
            <div>
              <p class="text-sm text-stone-400">Selected day</p>
              <h3 class="mt-2 text-2xl font-semibold">
                {selectedDate?.toLocaleDateString("en-US", {
                  month: "long",
                  day: "numeric",
                  year: "numeric",
                })}
              </h3>
            </div>
            <div class="flex items-center gap-2">
              <button
                class="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-sm text-stone-100 hover:bg-white/10"
                on:click={closeSelectedDay}
              >
                ✕
              </button>
              <button
                class="rounded-full bg-ember px-4 py-2 text-sm font-semibold text-black"
                on:click={regenerateSelectedDay}
              >
                Regenerate day
              </button>
            </div>
          </div>

          {#if selectedDayTasks.length > 0}
            <div class="max-h-[40vh] space-y-4 overflow-y-auto pr-2">
              {#each selectedDayTasks as task}
                <div class="rounded-3xl border border-white/10 bg-black/20 p-4">
                  <div class="flex items-start justify-between gap-4">
                    <div>
                      <p class="text-sm text-stone-400">
                        {task.category === "workout" ? "Workout" : "Diet"}
                      </p>
                      <h4 class="mt-1 font-semibold">{task.title}</h4>
                    </div>
                    <button
                      class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-stone-100 transition hover:bg-white/10"
                      on:click={() => removeTask(task.id)}
                    >
                      Remove
                    </button>
                  </div>
                  {#if task.category === "workout"}
                    {#if parseExercises(task.description)?.length}
                      <div class="mt-3 space-y-2">
                        {#each parseExercises(task.description) as exercise}
                          <div
                            class="flex items-center gap-2 text-sm text-stone-300"
                          >
                            <span class="text-amber-400">•</span>
                            <span
                              ><strong>{exercise.name}:</strong>
                              {exercise.sets} sets × {exercise.reps} reps</span
                            >
                          </div>
                        {/each}
                      </div>
                    {:else}
                      <p class="mt-3 text-sm leading-6 text-stone-300">
                        {task.description}
                      </p>
                    {/if}
                  {:else}
                    <p class="mt-3 text-sm leading-6 text-stone-300">
                      {task.description}
                    </p>
                  {/if}
                </div>
              {/each}
            </div>
          {:else}
            <div
              class="rounded-3xl border border-white/10 bg-black/20 p-6 text-sm text-stone-400"
            >
              <p>
                Click a day on the calendar to open its detail modal. Then
                remove or regenerate the selected day.
              </p>
            </div>
          {/if}

          <details
            class="mt-6 rounded-3xl border border-white/10 bg-black/20 p-4"
          >
            <summary
              class="cursor-pointer text-lg font-semibold text-stone-100 list-none outline-none transition hover:text-amber-400"
            >
              Add New Task
            </summary>
            <div class="mt-4 space-y-4">
              <div>
                <label
                  for="task-title"
                  class="block text-sm text-stone-400 mb-2"
                >
                  Task Title
                </label>
                <input
                  id="task-title"
                  type="text"
                  bind:value={newTaskTitle}
                  placeholder="e.g., Morning Run"
                  class="w-full rounded-lg border border-white/10 bg-black/40 px-4 py-2 text-stone-100 placeholder-stone-600 focus:border-ember focus:outline-none"
                />
              </div>

              <div>
                <label
                  for="task-desc"
                  class="block text-sm text-stone-400 mb-2"
                >
                  Description
                </label>
                <textarea
                  id="task-desc"
                  bind:value={newTaskDescription}
                  placeholder="e.g., 5km easy pace run at 6 AM"
                  rows="3"
                  class="w-full rounded-lg border border-white/10 bg-black/40 px-4 py-2 text-stone-100 placeholder-stone-600 focus:border-ember focus:outline-none resize-none"
                ></textarea>
              </div>

              <div>
                <label
                  for="task-category"
                  class="block text-sm text-stone-400 mb-2"
                >
                  Category
                </label>
                <select
                  id="task-category"
                  bind:value={newTaskCategory}
                  class="w-full rounded-lg border border-white/10 bg-black/40 px-4 py-2 text-stone-100 focus:border-ember focus:outline-none"
                >
                  <option value="workout">Workout</option>
                  <option value="diet">Diet</option>
                </select>
              </div>

              <button
                type="button"
                on:click={addNewTask}
                class="w-full rounded-full bg-ember px-6 py-2 font-semibold text-black transition hover:bg-amber-500"
              >
                Add Task
              </button>
            </div>
          </details>
        </section>
      </div>
    {/if}
  </div>
</AppShell>
