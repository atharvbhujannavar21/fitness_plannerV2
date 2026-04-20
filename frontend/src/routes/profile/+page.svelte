<script>
  import { goto } from '$app/navigation';
  import AppShell from '$lib/components/AppShell.svelte';
  import { selectedProfile } from '$lib/stores/profile';
  import { api } from '$lib/services/api';
  import { defaultProfileValues, normalizeMedicalConditions } from '$lib/types';

  const medicalConditionOptions = ['diabetes', 'hypertension', 'thyroid', 'none'];
  let form = { ...defaultProfileValues };
  let status = '';

  $: if ($selectedProfile) {
    form = {
      name: $selectedProfile.name,
      age: $selectedProfile.age,
      weight: $selectedProfile.weight,
      height: $selectedProfile.height,
      goal: $selectedProfile.goal,
      dietPreference: $selectedProfile.dietPreference,
      dailyWaterIntake: $selectedProfile.dailyWaterIntake,
      dietaryGoal: $selectedProfile.dietaryGoal,
      medicalConditions: [...$selectedProfile.medicalConditions],
      injuriesOrLimitations: $selectedProfile.injuriesOrLimitations,
      workoutHoursPerDay: $selectedProfile.workoutHoursPerDay,
      workoutDaysPerWeek: $selectedProfile.workoutDaysPerWeek,
      preferredWorkoutTime: $selectedProfile.preferredWorkoutTime,
      fitnessLevel: $selectedProfile.fitnessLevel,
      activityLevel: $selectedProfile.activityLevel,
      sleepHours: $selectedProfile.sleepHours,
      stressLevel: $selectedProfile.stressLevel
    };
  }

  function toggleMedicalCondition(condition) {
    const next = new Set(form.medicalConditions);

    if (condition === 'none') {
      form.medicalConditions = ['none'];
      return;
    }

    next.delete('none');
    if (next.has(condition)) {
      next.delete(condition);
    } else {
      next.add(condition);
    }

    form.medicalConditions = normalizeMedicalConditions(Array.from(next));
  }

  async function save() {
    if (!$selectedProfile) return;
    form.medicalConditions = normalizeMedicalConditions(form.medicalConditions);
    const updated = await api.updateProfile($selectedProfile.id, form);
    selectedProfile.set(updated);
    status = 'Profile updated successfully.';
  }

  async function remove() {
    if (!$selectedProfile) return;
    await api.deleteProfile($selectedProfile.id);
    selectedProfile.clear();
    goto('/');
  }
</script>

<AppShell title="Profile">
  <section class="glass-panel mx-auto max-w-5xl rounded-[2rem] p-6">
    <h2 class="font-display text-3xl">Edit local profile</h2>
    <p class="mt-2 text-sm text-stone-400">These values power BMI, AI chat prompts, and plan generation across workouts, diet, and recovery.</p>

    <div class="mt-6 space-y-8">
      <div>
        <h3 class="text-sm uppercase tracking-[0.3em] text-amber-200/60">Basics</h3>
        <div class="mt-4 grid gap-4 md:grid-cols-2">
          <label class="flex flex-col gap-2 text-sm">
            Name
            <input bind:value={form.name} class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none" />
          </label>
          <label class="flex flex-col gap-2 text-sm">
            Age
            <input bind:value={form.age} type="number" min="1" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none" />
          </label>
          <label class="flex flex-col gap-2 text-sm">
            Weight (kg)
            <input bind:value={form.weight} type="number" min="1" step="0.1" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none" />
          </label>
          <label class="flex flex-col gap-2 text-sm">
            Height (cm)
            <input bind:value={form.height} type="number" min="1" step="0.1" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none" />
          </label>
          <label class="flex flex-col gap-2 text-sm md:col-span-2">
            Goal
            <select bind:value={form.goal} class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none">
              <option value="fat_loss">Fat Loss</option>
              <option value="muscle_gain">Muscle Gain</option>
              <option value="maintenance">Maintenance</option>
            </select>
          </label>
        </div>
      </div>

      <div>
        <h3 class="text-sm uppercase tracking-[0.3em] text-amber-200/60">Diet & Nutrition</h3>
        <div class="mt-4 grid gap-4 md:grid-cols-2">
          <label class="flex flex-col gap-2 text-sm">
            Diet Preference
            <select bind:value={form.dietPreference} class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none">
              <option value="veg">Veg</option>
              <option value="non-veg">Non-Veg</option>
              <option value="vegan">Vegan</option>
              <option value="eggetarian">Eggetarian</option>
            </select>
          </label>
          <label class="flex flex-col gap-2 text-sm">
            Daily Water Intake (liters)
            <input bind:value={form.dailyWaterIntake} type="number" min="0" step="0.1" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none" />
          </label>
          <label class="flex flex-col gap-2 text-sm md:col-span-2">
            Dietary Goal
            <select bind:value={form.dietaryGoal} class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none">
              <option value="weight-loss">Weight Loss</option>
              <option value="muscle-gain">Muscle Gain</option>
              <option value="maintenance">Maintenance</option>
            </select>
          </label>
        </div>
      </div>

      <div>
        <h3 class="text-sm uppercase tracking-[0.3em] text-amber-200/60">Health</h3>
        <div class="mt-4 grid gap-4 md:grid-cols-2">
          <div class="md:col-span-2">
            <p class="text-sm text-stone-200">Medical Conditions</p>
            <div class="mt-3 flex flex-wrap gap-3">
              {#each medicalConditionOptions as condition}
                <label class="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm">
                  <input
                    type="checkbox"
                    checked={form.medicalConditions.includes(condition)}
                    on:change={() => toggleMedicalCondition(condition)}
                  />
                  <span class="capitalize">{condition.replace('-', ' ')}</span>
                </label>
              {/each}
            </div>
          </div>
          <label class="flex flex-col gap-2 text-sm md:col-span-2">
            Injuries or Limitations
            <textarea bind:value={form.injuriesOrLimitations} rows="3" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none"></textarea>
          </label>
        </div>
      </div>

      <div>
        <h3 class="text-sm uppercase tracking-[0.3em] text-amber-200/60">Workout Planning</h3>
        <div class="mt-4 grid gap-4 md:grid-cols-2">
          <label class="flex flex-col gap-2 text-sm">
            Workout Hours Per Day
            <input bind:value={form.workoutHoursPerDay} type="number" min="0.5" max="3" step="0.5" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none" />
          </label>
          <label class="flex flex-col gap-2 text-sm">
            Workout Days Per Week
            <input bind:value={form.workoutDaysPerWeek} type="number" min="1" max="7" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none" />
          </label>
          <label class="flex flex-col gap-2 text-sm md:col-span-2">
            Preferred Workout Time
            <select bind:value={form.preferredWorkoutTime} class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none">
              <option value="morning">Morning</option>
              <option value="afternoon">Afternoon</option>
              <option value="evening">Evening</option>
            </select>
          </label>
        </div>
      </div>

      <div>
        <h3 class="text-sm uppercase tracking-[0.3em] text-amber-200/60">Fitness Profile</h3>
        <div class="mt-4 grid gap-4 md:grid-cols-2">
          <label class="flex flex-col gap-2 text-sm">
            Fitness Level
            <select bind:value={form.fitnessLevel} class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none">
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </label>
          <label class="flex flex-col gap-2 text-sm">
            Activity Level
            <select bind:value={form.activityLevel} class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none">
              <option value="sedentary">Sedentary</option>
              <option value="light">Light</option>
              <option value="moderate">Moderate</option>
              <option value="active">Active</option>
            </select>
          </label>
        </div>
      </div>

      <div>
        <h3 class="text-sm uppercase tracking-[0.3em] text-amber-200/60">Lifestyle</h3>
        <div class="mt-4 grid gap-4 md:grid-cols-2">
          <label class="flex flex-col gap-2 text-sm">
            Sleep Hours
            <input bind:value={form.sleepHours} type="number" min="0" max="24" step="0.5" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none" />
          </label>
          <label class="flex flex-col gap-2 text-sm">
            Stress Level
            <select bind:value={form.stressLevel} class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none">
              <option value="low">Low</option>
              <option value="moderate">Moderate</option>
              <option value="high">High</option>
            </select>
          </label>
        </div>
      </div>
    </div>

    {#if status}
      <div class="mt-4 rounded-2xl bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">{status}</div>
    {/if}

    <div class="mt-6 flex flex-wrap justify-between gap-3">
      <button class="rounded-full border border-red-500/20 bg-red-500/10 px-5 py-3 text-red-200" on:click={remove}>
        Delete profile
      </button>
      <button class="rounded-full bg-ember px-5 py-3 font-semibold text-black" on:click={save}>Save changes</button>
    </div>
  </section>
</AppShell>
