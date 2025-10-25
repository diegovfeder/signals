/**
 * Dashboard Page
 *
 * Display live trading signals for all tracked symbols with Resend-inspired dark UI.
 */

"use client"

import type { JSX } from "react"
import { useMemo } from "react"
import SignalCard from "@/components/dashboard/SignalCard"
import { useSignals, type Signal } from "@/lib/hooks/useSignals"
import Link from "next/link"

const PLACEHOLDER_COUNT = 4

export default function Dashboard(): JSX.Element {
  const {
    data: signals = [],
    isLoading,
    isError,
    error,
  } = useSignals()

  const latestSignals = useMemo<Signal[]>(() => {
    const map = new Map<string, Signal>()
    for (const signal of signals) {
      if (!map.has(signal.symbol)) {
        map.set(signal.symbol, signal)
      }
    }
    return Array.from(map.values()).sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
    )
  }, [signals])

  const placeholders = Array.from({
    length: Math.max(latestSignals.length || 0, PLACEHOLDER_COUNT),
  })

  return (
    <main className="min-h-screen py-8 px-4">
      <div className="container-app">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <Link
            href="/"
            className="inline-block text-sm text-muted hover:text-foreground-secondary mb-4 transition-colors"
          >
            ← Home
          </Link>
          <h1 className="text-4xl md:text-5xl font-bold text-gradient mb-2">
            Trading Signals
          </h1>
          <p className="text-foreground-muted">
            Live signals powered by RSI + EMA indicators
          </p>
        </div>

        {/* Error state */}
        {isError && error && (
          <div className="card-premium p-6 mb-8 border-red-500/30 animate-slide-up">
            <div className="flex items-start gap-3">
              <span className="text-danger text-xl">⚠</span>
              <div>
                <p className="text-danger font-semibold mb-1">
                  Failed to load signals
                </p>
                <p className="text-sm text-foreground-muted">
                  {String(error.message || error)}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Loading state */}
        {isLoading && (
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {placeholders.map((_, idx) => (
              <div key={idx} className="card p-6 animate-pulse">
                <div className="h-6 bg-background-tertiary rounded mb-4 w-24" />
                <div className="h-8 bg-background-tertiary rounded mb-4" />
                <div className="h-2 bg-background-tertiary rounded mb-5" />
                <div className="space-y-2">
                  <div className="h-4 bg-background-tertiary rounded w-full" />
                  <div className="h-4 bg-background-tertiary rounded w-3/4" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Signals grid */}
        {!isLoading && !isError && latestSignals.length > 0 && (
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {latestSignals.map((signal, idx) => (
              <div
                key={`${signal.symbol}-${signal.id}`}
                className="animate-slide-up"
                style={{ animationDelay: `${idx * 50}ms` }}
              >
                <SignalCard
                  symbol={signal.symbol}
                  signalType={signal.signal_type || "HOLD"}
                  strength={signal.strength ?? 0}
                  reasoning={signal.reasoning ?? []}
                  price={signal.price_at_signal ?? 0}
                />
              </div>
            ))}
          </div>
        )}

        {!isLoading && !isError && latestSignals.length === 0 && (
          <div className="card-premium p-6 text-center animate-fade-in">
            <p className="text-lg font-semibold mb-2">
              No signals yet for your symbols
            </p>
            <p className="text-sm text-foreground-muted">
              Run the Prefect flow (`python -m flows.signal_generation`) to
              populate the database, then refresh this page.
            </p>
          </div>
        )}

        {!isLoading && !isError && latestSignals.length > 0 && (
          <div className="mt-12 text-center animate-fade-in">
            <div className="inline-flex items-center gap-2 card px-4 py-2">
              <span className="status-live" />
              <span className="text-sm text-foreground-muted">
                Auto-refreshes every 60 seconds
              </span>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
