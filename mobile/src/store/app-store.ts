import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type { AgentPlan } from '../types/api';
type AppState = { travelerId: string; saved: string[]; activePlan: AgentPlan | null; setActivePlan: (plan: AgentPlan) => void; toggleSaved: (destination: string) => void; setTravelerId: (id: string) => void };
export const useAppStore = create<AppState>()(persist((set) => ({
  travelerId: process.env.EXPO_PUBLIC_TRAVELER_ID || 'traveler_demo', saved: ['Kyoto', 'Amalfi Coast'], activePlan: null,
  setActivePlan: (activePlan) => set({ activePlan }),
  toggleSaved: (destination) => set((state) => ({ saved: state.saved.includes(destination) ? state.saved.filter((x) => x !== destination) : [...state.saved, destination] })),
  setTravelerId: (travelerId) => set({ travelerId }),
}), { name: 'naviqra-mobile-state', storage: createJSONStorage(() => AsyncStorage), partialize: (state) => ({ travelerId: state.travelerId, saved: state.saved, activePlan: state.activePlan }) as AppState }));
