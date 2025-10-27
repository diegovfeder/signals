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

export interface MarketBar {
  symbol: string
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface BacktestSummary {
  symbol: string
  range: string
  trades: number
  win_rate: number
  avg_return: number
  total_return: number
  last_trained_at?: string | null
  notes?: string | null
}

export interface SubscriberSummary {
  email: string
  subscribed_at?: string | null
  confirmed: boolean
  confirmed_at?: string | null
  unsubscribed: boolean
  confirmation_token?: string | null
  unsubscribe_token?: string | null
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

export function useMarketData(symbol: string, range: string) {
  return useQuery({
    queryKey: ['market-data', symbol, range],
    enabled: Boolean(symbol),
    refetchInterval: 300_000,
    queryFn: async () =>
      api.get<MarketBar[]>(
        `/api/market-data/${encodeURIComponent(symbol)}/ohlcv`,
        {
          range,
          limit: '5000',
        },
      ),
    select: (rows) =>
      (rows ?? [])
        .map((row) => ({
          ...row,
          open: Number(row.open),
          high: Number(row.high),
          low: Number(row.low),
          close: Number(row.close),
          volume: Number(row.volume),
        }))
        .sort(
          (a, b) =>
            new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
        ),
  })
}

export function useBacktestSummary(symbol: string, range: string) {
  return useQuery({
    queryKey: ['backtests', symbol, range],
    enabled: Boolean(symbol),
    staleTime: 300_000,
    queryFn: async () =>
      api.get<BacktestSummary>(
        `/api/backtests/${encodeURIComponent(symbol)}`,
        { range },
      ),
  })
}

type SubscriberQueryOptions = {
  includeUnsubscribed?: boolean
  includeTokens?: boolean
  limit?: number
  offset?: number
}

export function useSubscribers(options: SubscriberQueryOptions = {}) {
  const {
    includeUnsubscribed = true,
    includeTokens = false,
    limit = 100,
    offset = 0,
  } = options

  const params: Record<string, string> = {
    include_unsubscribed: String(includeUnsubscribed),
    include_tokens: String(includeTokens),
    limit: String(limit),
    offset: String(offset),
  }

  return useQuery({
    queryKey: ['subscribers', params],
    queryFn: async () =>
      api.get<{ subscribers: SubscriberSummary[]; total: number }>(
        '/api/subscribe',
        params,
      ),
    staleTime: 60_000,
    keepPreviousData: true,
  })
}
