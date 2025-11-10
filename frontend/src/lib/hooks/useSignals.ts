/**
 * useSignals Hook
 *
 * Fetch trading signals from API with caching and revalidation.
 */

"use client"

import { keepPreviousData, useQuery } from "@tanstack/react-query"
import { api } from "../api-client"
import {
  API_ENDPOINTS,
  RANGE_HISTORY_LIMIT_DAYS,
  type RangeValue,
} from "../utils/constants"

export interface Signal {
  id: string
  symbol: string
  timestamp: string
  signal_type: 'BUY' | 'SELL' | 'HOLD'
  strength: number
  reasoning: string[]
  price_at_signal: number | null
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

export interface IndicatorPoint {
  symbol: string
  timestamp: string
  rsi?: number | null
  ema12?: number | null
  ema26?: number | null
  macd?: number | null
  macdSignal?: number | null
  macdHistogram?: number | null
}

type IndicatorApiResponse = {
  symbol: string
  timestamp: string
  rsi: number | null
  ema_12: number | null
  ema_26: number | null
  macd: number | null
  macd_signal: number | null
  macd_histogram: number | null
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
    staleTime: 60 * 60 * 1000, // 1 hour - refetch if visited >1hr after last fetch
    gcTime: 24 * 60 * 60 * 1000, // Keep in cache for 24 hours
    refetchOnWindowFocus: false, // Don't refetch on tab focus
  })
}

export function useSignalBySymbol(symbol: string) {
  return useQuery({
    queryKey: ['signals', symbol],
    queryFn: async () => api.get<Signal>(`/api/signals/${symbol}`),
    enabled: Boolean(symbol),
    staleTime: 60 * 60 * 1000, // 1 hour - refetch if visited >1hr after last fetch
    gcTime: 24 * 60 * 60 * 1000, // Keep in cache for 24 hours
    refetchOnWindowFocus: false, // Don't refetch on tab focus
  })
}

const DEFAULT_HISTORY_DAYS = 30

export function useSignalHistory(symbol: string, range: RangeValue) {
  const historyWindow = RANGE_HISTORY_LIMIT_DAYS[range] ?? DEFAULT_HISTORY_DAYS

  return useQuery({
    queryKey: ['signal-history', symbol, historyWindow],
    enabled: Boolean(symbol),
    staleTime: 30 * 60 * 1000,
    gcTime: 24 * 60 * 60 * 1000,
    refetchOnWindowFocus: false,
    placeholderData: keepPreviousData,
    queryFn: async () =>
      api.get<{ signals: Signal[] }>(
        API_ENDPOINTS.SIGNAL_HISTORY(encodeURIComponent(symbol)),
        { days: String(historyWindow) },
      ),
    select: (response) =>
      (response?.signals ?? [])
        .map((signal) => ({
          ...signal,
          price_at_signal:
            signal.price_at_signal != null
              ? Number(signal.price_at_signal)
              : null,
          strength:
            signal.strength != null ? Number(signal.strength) : signal.strength,
        }))
        .sort(
          (a: Signal, b: Signal) =>
            new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
        ),
  })
}

export function useMarketData(symbol: string, range: string) {
  return useQuery({
    queryKey: ['market-data', symbol, range],
    enabled: Boolean(symbol),
    staleTime: 60 * 60 * 1000, // 1 hour - refetch if visited >1hr after last fetch
    gcTime: 24 * 60 * 60 * 1000, // Keep in cache for 24 hours
    refetchOnWindowFocus: false, // Don't refetch on tab focus
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
          (a: MarketBar, b: MarketBar) =>
            new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
        ),
  })
}

export function useIndicators(symbol: string, range: string) {
  return useQuery({
    queryKey: ['indicators', symbol, range],
    enabled: Boolean(symbol),
    staleTime: 60 * 60 * 1000,
    gcTime: 24 * 60 * 60 * 1000,
    refetchOnWindowFocus: false,
    queryFn: async () =>
      api.get<IndicatorApiResponse[]>(
        `/api/market-data/${encodeURIComponent(symbol)}/indicators`,
        {
          range,
          limit: '5000',
        },
      ),
    select: (rows) =>
      (rows ?? [])
        .map((row) => ({
          symbol: row.symbol,
          timestamp: row.timestamp,
          rsi: row.rsi != null ? Number(row.rsi) : null,
          ema12: row.ema_12 != null ? Number(row.ema_12) : null,
          ema26: row.ema_26 != null ? Number(row.ema_26) : null,
          macd: row.macd != null ? Number(row.macd) : null,
          macdSignal:
            row.macd_signal != null ? Number(row.macd_signal) : null,
          macdHistogram:
            row.macd_histogram != null ? Number(row.macd_histogram) : null,
        }))
        .sort(
          (a: IndicatorPoint, b: IndicatorPoint) =>
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
    placeholderData: keepPreviousData,
  })
}
