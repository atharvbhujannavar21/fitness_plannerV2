<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { api } from '$lib/services/api';
  import { selectedProfile } from '$lib/stores/profile';
  import type { Goal, Profile } from '$lib/types';

  type ProfileForm = {
    name: string;
    age: number;
    weight: number;
    height: number;
    goal: Goal;
  };

  const emptyForm: ProfileForm = {
    name: '',
    age: 21,
    weight: 70,
    height: 175,
    goal: 'muscle_gain'
  };

  let profiles: Profile[] = [];
  let showModal = false;
  let editing: Profile | null = null;
  let loading = true;
  let error = '';
  let form: ProfileForm = { ...emptyForm };

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

  function openCreate() {
    editing = null;
    form = { ...emptyForm };
    showModal = true;
  }

  function openEdit(profile: Profile) {
    editing = profile;
    form = {
      name: profile.name,
      age: profile.age,
      weight: profile.weight,
      height: profile.height,
      goal: profile.goal
    };
    showModal = true;
  }

  async function saveProfile() {
    error = '';
    try {
      if (editing) {
        await api.updateProfile(editing.id, form);
      } else {
        await api.createProfile(form);
      }
      showModal = false;
      await loadProfiles();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unable to save profile.';
    }
  }

  async function removeProfile(id: string) {
    try {
      await api.deleteProfile(id);
      await loadProfiles();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unable to delete profile.';
    }
  }

  async function selectProfile(profile: Profile) {
    selectedProfile.set(profile);
    await goto('/dashboard');
  }

  onMount(loadProfiles);
</script>

<section class="min-h-screen px-4 py-10 md:px-10">
  <div class="mx-auto max-w-6xl rounded-[2rem] border border-white/10 bg-[#0c0d10]/90 p-6 shadow-glow backdrop-blur md:p-10">
    <div class="mb-10 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm uppercase tracking-[0.4em] text-amber-200/60">FitFusion</p>
        <h1 class="font-display text-4xl font-bold md:text-6xl">Choose your training profile</h1>
        <p class="mt-3 max-w-2xl text-sm text-stone-400 md:text-base">
          Local-only fitness profiles with a Netflix-inspired selector, AI coaching, workout planning, and diet tracking.
        </p>
      </div>
      <button
        class="rounded-full bg-ember px-5 py-3 font-semibold text-black transition hover:scale-[1.02]"
        on:click={openCreate}
      >
        Add Profile
      </button>
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
                <span class="rounded-full bg-white/5 px-3 py-1">{profile.height} cm</span>
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
  <div class="fixed inset-0 z-40 flex items-center justify-center bg-black/70 p-4">
    <div class="glass-panel w-full max-w-xl rounded-[2rem] p-6">
      <div class="mb-6 flex items-center justify-between">
        <div>
          <h3 class="font-display text-3xl">{editing ? 'Edit profile' : 'Create profile'}</h3>
          <p class="mt-1 text-sm text-stone-400">Profiles stay local in MongoDB. No login and no auth flow.</p>
        </div>
        <button class="text-2xl text-stone-400" on:click={() => (showModal = false)}>×</button>
      </div>

      <div class="grid gap-4 md:grid-cols-2">
        <label class="flex flex-col gap-2 text-sm">
          Name
          <input bind:value={form.name} class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none" />
        </label>
        <label class="flex flex-col gap-2 text-sm">
          Age
          <input bind:value={form.age} type="number" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none" />
        </label>
        <label class="flex flex-col gap-2 text-sm">
          Weight (kg)
          <input bind:value={form.weight} type="number" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none" />
        </label>
        <label class="flex flex-col gap-2 text-sm">
          Height (cm)
          <input bind:value={form.height} type="number" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none" />
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

      <div class="mt-6 flex justify-end gap-3">
        <button class="rounded-full border border-white/10 px-5 py-3" on:click={() => (showModal = false)}>Cancel</button>
        <button class="rounded-full bg-ember px-5 py-3 font-semibold text-black" on:click={saveProfile}>
          {editing ? 'Update' : 'Create'}
        </button>
      </div>
    </div>
  </div>
{/if}
