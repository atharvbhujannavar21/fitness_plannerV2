<script lang="ts">
  import { page } from '$app/state';
  import { selectedProfile } from '$lib/stores/profile';
  import { goto } from '$app/navigation';

  const links = [
    { href: '/dashboard', label: 'Dashboard', icon: '◧' },
    { href: '/calendar', label: 'Calendar', icon: '◫' },
    { href: '/profile', label: 'Profile', icon: '◎' },
    { href: '/settings', label: 'Settings', icon: '◌' }
  ];

  function backToProfiles() {
    selectedProfile.clear();
    goto('/');
  }
</script>

<aside class="glass-panel flex h-full w-full flex-col rounded-[2rem] p-4 md:max-w-[96px]">
  <div class="mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-ember text-xl font-bold text-black">+</div>

  <nav class="flex flex-1 flex-col gap-3">
    {#each links as link}
      <a
        href={link.href}
        class={`flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition md:justify-center ${
          page.url.pathname === link.href
            ? 'bg-ember text-black'
            : 'bg-white/5 text-stone-300 hover:bg-white/10'
        }`}
      >
        <span class="text-lg">{link.icon}</span>
        <span class="md:hidden">{link.label}</span>
      </a>
    {/each}
  </nav>

  <button class="rounded-2xl border border-white/10 px-4 py-3 text-left text-sm text-stone-300" on:click={backToProfiles}>
    Switch
  </button>
</aside>
