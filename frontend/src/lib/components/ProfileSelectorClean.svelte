<script>
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { api } from '$lib/services/api';
  import { selectedProfile } from '$lib/stores/profile';
  import { defaultProfileValues, normalizeMedicalConditions } from '$lib/types';

  const medicalConditionOptions = ['diabetes', 'hypertension', 'thyroid', 'none'];
  let profiles = [];
  let showModal = false;
  let editing = null;
  let loading = true;
  let error = '';
  let form = { ...defaultProfileValues };

  async function loadProfiles() {
    loading = true;
    error = '';

    try {
      profiles = await api.getProfiles();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unable to load profiles.';
    } finally {
      loading = false;
    }
  }

  function resetForm() {
    form = { ...defaultProfileValues, medicalConditions: [...defaultProfileValues.medicalConditions] };
  }

  function openCreate() {
    editing = null;
    resetForm();
    showModal = true;
  }

  function openEdit(profile) {
    editing = profile;
    form = {
      name: profile.name,
      age: profile.age,
      weight: profile.weight,
      height: profile.height,
      goal: profile.goal,
      dietPreference: profile.dietPreference,
      dailyWaterIntake: profile.dailyWaterIntake,
      dietaryGoal: profile.dietaryGoal,
      medicalConditions: [...profile.medicalConditions],
      injuriesOrLimitations: profile.injuriesOrLimitations,
      workoutHoursPerDay: profile.workoutHoursPerDay,
      workoutDaysPerWeek: profile.workoutDaysPerWeek,
      preferredWorkoutTime: profile.preferredWorkoutTime,
      fitnessLevel: profile.fitnessLevel,
      activityLevel: profile.activityLevel,
      sleepHours: profile.sleepHours,
      stressLevel: profile.stressLevel
    };
    showModal = true;
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

  async function saveProfile() {
    error = '';
    form.medicalConditions = normalizeMedicalConditions(form.medicalConditions);

    try {
      if (editing) {
        const updated = await api.updateProfile(editing.id, form);
        if ($selectedProfile?.id === updated.id) {
          selectedProfile.set(updated);
        }
      } else {
        await api.createProfile(form);
      }

      showModal = false;
      await loadProfiles();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unable to save profile.';
    }
  }

  async function removeProfile(id) {
    try {
      await api.deleteProfile(id);
      if ($selectedProfile?.id === id) {
        selectedProfile.clear();
      }
      await loadProfiles();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unable to delete profile.';
    }
  }

  async function selectProfile(profile) {
    selectedProfile.set(profile);
    await goto('/dashboard');
  }

  onMount(loadProfiles);
</script>

<section class="min-h-screen px-4 py-10 md:px-10">
  <div class="mx-auto max-w-6xl rounded-[2rem] border border-white/10 bg-[#0c0d10]/90 p-6 shadow-glow backdrop-blur md:p-10">
    <div class="mb-10">
      <p class="text-sm uppercase tracking-[0.4em] text-amber-200/60">FitFusion</p>
      <h1 class="font-display text-4xl font-bold md:text-6xl">Choose your training profile</h1>
      <p class="mt-3 max-w-2xl text-sm text-stone-400 md:text-base">
        Local-only fitness profiles with a Netflix-inspired selector, AI coaching, workout planning, and diet tracking.
      </p>
    </div>

    {#if error}
      <div class="mb-6 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</div>
    {/if}

    <div class="glass-panel soft-grid rounded-[2rem] p-8">
      {#if loading}
        <div class="py-16 text-center text-stone-400">Loading profiles...</div>
      {:else}
        <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {#each profiles as profile}
            <div class="group rounded-[1.75rem] border border-white/8 bg-white/[0.02] p-5 text-left transition hover:-translate-y-1 hover:border-ember/40 hover:bg-white/[0.05]">
              <div class="mb-5 flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-[#ffd6bd] via-[#ffc299] to-[#ff8c00] text-3xl font-bold text-[#251200]">
                {profile.name.slice(0, 1).toUpperCase()}
              </div>
              <h2 class="font-display text-2xl font-semibold">{profile.name}</h2>
              <p class="mt-1 text-sm capitalize text-stone-400">{profile.goal.replace('_', ' ')}</p>
              <div class="mt-4 flex flex-wrap gap-2 text-xs text-stone-300">
                <span class="rounded-full bg-white/5 px-3 py-1">{profile.age} yrs</span>
                <span class="rounded-full bg-white/5 px-3 py-1">{profile.weight} kg</span>
                <span class="rounded-full bg-white/5 px-3 py-1">{profile.activityLevel}</span>
                <span class="rounded-full bg-white/5 px-3 py-1">{profile.dietPreference}</span>
              </div>
              <div class="mt-5 flex flex-wrap gap-2">
                <button
                  class="rounded-full bg-ember px-3 py-2 text-xs font-semibold text-black"
                  on:click={() => selectProfile(profile)}
                >
                  Open
                </button>
                <button
                  class="rounded-full border border-white/10 px-3 py-2 text-xs"
                  on:click={() => openEdit(profile)}
                >
                  Edit
                </button>
                <button
                  class="rounded-full border border-red-500/20 bg-red-500/10 px-3 py-2 text-xs text-red-200"
                  on:click={() => removeProfile(profile.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          {/each}

          <button
            class="flex min-h-[280px] flex-col items-center justify-center rounded-[1.75rem] border border-dashed border-amber-100/20 bg-[#16181d] transition hover:border-ember/50 hover:bg-[#1a1d22]"
            on:click={openCreate}
          >
            <div class="flex h-24 w-24 items-center justify-center rounded-full bg-[#ffd6bd] text-5xl text-[#1b130a]">+</div>
            <span class="mt-5 text-lg font-semibold text-stone-200">Create profile</span>
          </button>
        </div>
      {/if}
    </div>
  </div>
</section>

{#if showModal}
  <div class="fixed inset-0 z-40 overflow-y-auto bg-black/70 p-4">
    <div class="mx-auto w-full max-w-5xl glass-panel rounded-[2rem] p-6">
      <div class="mb-6 flex items-center justify-between">
        <div>
          <h3 class="font-display text-3xl">{editing ? 'Edit profile' : 'Create profile'}</h3>
          <p class="mt-1 text-sm text-stone-400">Profiles stay local in MongoDB. No login and no auth flow.</p>
        </div>
        <button class="text-2xl text-stone-400" on:click={() => (showModal = false)}>x</button>
      </div>

      <div class="space-y-8">
        <div>
          <h4 class="text-sm uppercase tracking-[0.3em] text-amber-200/60">Basics</h4>
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
          <h4 class="text-sm uppercase tracking-[0.3em] text-amber-200/60">Diet & Nutrition</h4>
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
          <h4 class="text-sm uppercase tracking-[0.3em] text-amber-200/60">Health</h4>
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
                    <span class="capitalize">{condition}</span>
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
          <h4 class="text-sm uppercase tracking-[0.3em] text-amber-200/60">Workout Planning</h4>
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
          <h4 class="text-sm uppercase tracking-[0.3em] text-amber-200/60">Fitness Profile</h4>
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
          <h4 class="text-sm uppercase tracking-[0.3em] text-amber-200/60">Lifestyle</h4>
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

      <div class="mt-6 flex justify-end gap-3">
        <button class="rounded-full border border-white/10 px-5 py-3" on:click={() => (showModal = false)}>Cancel</button>
        <button class="rounded-full bg-ember px-5 py-3 font-semibold text-black" on:click={saveProfile}>
          {editing ? 'Update' : 'Create'}
        </button>
      </div>
    </div>
  </div>
{/if}
