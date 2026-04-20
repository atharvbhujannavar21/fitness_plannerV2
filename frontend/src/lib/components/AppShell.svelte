<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { selectedProfile } from '$lib/stores/profile';
  import Sidebar from '$lib/components/SidebarClean.svelte';
  import Navbar from '$lib/components/Navbar.svelte';

  export let title = 'Dashboard';

  onMount(() => {
    if (!$selectedProfile) {
      goto('/');
    }
  });
</script>

<div class="min-h-screen p-4 md:p-6">
  <div class="mx-auto grid max-w-[1600px] items-start gap-4 md:grid-cols-[96px_minmax(0,1fr)]">
    <Sidebar />
    <div class="min-w-0 space-y-4">
      <Navbar {title} />
      <slot />
    </div>
  </div>
</div>
