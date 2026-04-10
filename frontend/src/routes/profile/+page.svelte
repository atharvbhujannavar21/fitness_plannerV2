<script>
  import { goto } from '$app/navigation';
  import AppShell from '$lib/components/AppShell.svelte';
  import { selectedProfile } from '$lib/stores/profile';
  import { api } from '$lib/services/api';
  let form = {
    name: '',
    age: 0,
    weight: 0,
    height: 0,
    goal: 'maintenance'
  };
  let status = '';

  $: if ($selectedProfile) {
    form = {
      name: $selectedProfile.name,
      age: $selectedProfile.age,
      weight: $selectedProfile.weight,
      height: $selectedProfile.height,
      goal: $selectedProfile.goal
    };
  }

  async function save() {
    if (!$selectedProfile) return;
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
  <section class="glass-panel mx-auto max-w-3xl rounded-[2rem] p-6">
    <h2 class="font-display text-3xl">Edit local profile</h2>
    <p class="mt-2 text-sm text-stone-400">These values power BMI, AI chat prompts, and weekly plan generation.</p>

    <div class="mt-6 grid gap-4 md:grid-cols-2">
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
