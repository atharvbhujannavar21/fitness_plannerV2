<script lang="ts">
  import { selectedProfile } from '$lib/stores/profile';

  export let title = 'Dashboard';
</script>

<header class="glass-panel flex flex-col gap-4 rounded-[2rem] px-5 py-4 md:flex-row md:items-center md:justify-between">
  <div>
    <p class="text-xs uppercase tracking-[0.3em] text-stone-500">Daily coaching</p>
    <h1 class="font-display text-3xl">{title}</h1>
  </div>

  {#if $selectedProfile}
    <div class="flex items-center gap-3 rounded-full bg-white/5 px-3 py-2">
      <div class="flex h-11 w-11 items-center justify-center rounded-full bg-ember font-bold text-black">
        {$selectedProfile.name.slice(0, 1).toUpperCase()}
      </div>
      <div>
        <div class="font-semibold">{$selectedProfile.name}</div>
        <div class="text-xs capitalize text-stone-400">{$selectedProfile.goal.replace('_', ' ')}</div>
      </div>
    </div>
  {/if}
</header>
