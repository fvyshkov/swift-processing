import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ThemeStore {
  mode: 'light' | 'dark';
  toggleTheme: () => void;
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      mode: 'light',
      toggleTheme: () => set((state) => ({ mode: state.mode === 'light' ? 'dark' : 'light' })),
    }),
    {
      name: 'theme-storage',
    }
  )
);

