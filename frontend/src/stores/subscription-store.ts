'use client'

import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

type SubscriptionState = {
  email: string | null
  setEmail: (email: string | null) => void
  isMinimized: boolean
  setIsMinimized: (value: boolean) => void
}

export const useSubscriptionStore = create<SubscriptionState>()(
  persist(
    (set) => ({
      email: null,
      setEmail: (email) => set({ email }),
      isMinimized: false,
      setIsMinimized: (value) => set({ isMinimized: value }),
    }),
    {
      name: 'signals-subscription',
      storage: createJSONStorage(() => localStorage),
    },
  ),
)
