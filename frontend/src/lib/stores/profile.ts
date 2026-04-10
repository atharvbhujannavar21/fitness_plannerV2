import { browser } from '$app/environment';
import { writable } from 'svelte/store';
import type { Profile } from '$lib/types';

const stored = browser ? window.localStorage.getItem('fitfusion:selected-profile') : null;

function createSelectedProfileStore() {
  const initialValue = stored ? (JSON.parse(stored) as Profile) : null;
  const { subscribe, set } = writable<Profile | null>(initialValue);

  return {
    subscribe,
    set: (value: Profile | null) => {
      if (browser) {
        if (value) {
          window.localStorage.setItem('fitfusion:selected-profile', JSON.stringify(value));
        } else {
          window.localStorage.removeItem('fitfusion:selected-profile');
        }
      }
      set(value);
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
