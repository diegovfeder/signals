'use client'

import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

type SubscriptionState = {
  email: string | null
  setEmail: (email: string | null) => void
}

export const useSubscriptionStore = create<SubscriptionState>()(
  persist(
    (set) => ({
      email: null,
      setEmail: (email) => set({ email }),
    }),
    {
      name: 'signals-subscription',
      storage: createJSONStorage(() => localStorage),
    },
  ),
)
