import { browser } from '$app/environment';
import { writable } from 'svelte/store';
import { normalizeProfile, type Profile } from '$lib/types';

const stored = browser ? window.localStorage.getItem('fitfusion:selected-profile') : null;

function createSelectedProfileStore() {
  const initialValue = stored ? normalizeProfile(JSON.parse(stored) as Partial<Profile>) : null;
  const { subscribe, set } = writable<Profile | null>(initialValue);

  return {
    subscribe,
    set: (value: Profile | null) => {
      const normalized = normalizeProfile(value);
      if (browser) {
        if (normalized) {
          window.localStorage.setItem('fitfusion:selected-profile', JSON.stringify(normalized));
        } else {
          window.localStorage.removeItem('fitfusion:selected-profile');
        }
      }
      set(normalized);
    },
    clear: () => {
      if (browser) {
        window.localStorage.removeItem('fitfusion:selected-profile');
      }
      set(null);
    }
  };
}

export const selectedProfile = createSelectedProfileStore();
