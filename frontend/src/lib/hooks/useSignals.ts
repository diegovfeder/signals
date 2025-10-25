/**
 * useSignals Hook
 *
 * Fetch trading signals from API with caching and revalidation.
 */

'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '../api-client'

export interface Signal {
  id: string
  symbol: string
  timestamp: string
  signal_type: 'BUY' | 'SELL' | 'HOLD'
  strength: number
  reasoning: string[]
  price_at_signal: number
}

async function fetchSignals(): Promise<Signal[]> {
  const data = await api.get<{ signals: Signal[] }>('/api/signals', {
    limit: '50',
  })
  return data.signals ?? []
}

export function useSignals() {
  return useQuery({
    queryKey: ['signals'],
    queryFn: fetchSignals,
    refetchInterval: 60_000,
  })
}

export function useSignalBySymbol(symbol: string) {
  return useQuery({
    queryKey: ['signals', symbol],
    queryFn: async () => api.get<Signal>(`/api/signals/${symbol}`),
    enabled: Boolean(symbol),
    refetchInterval: 60_000,
  })
}
