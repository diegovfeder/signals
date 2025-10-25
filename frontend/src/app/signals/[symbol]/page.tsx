/**
 * Symbol Detail Page
 *
 * Detailed view of a specific symbol with price charts, indicators, and signal history.
 */

'use client'

import { use } from 'react'
import { useSignalBySymbol } from '@/lib/hooks/useSignals'
import Link from 'next/link'

export default function SignalDetail({
  params,
}: {
  params: Promise<{ symbol: string }>;
}) {
  // Next.js 15: params is a Promise and must be awaited
  const { symbol } = use(params);

  const {
    data: signal,
    isLoading,
    isError,
    error,
  } = useSignalBySymbol(symbol)

  return (
    <main className="min-h-screen py-8 px-4">
      <div className="container-app">
        {/* Header with back button */}
        <div className="mb-8 flex items-center gap-4">
          <Link
            href="/dashboard"
            className="btn-secondary px-4 py-2 text-sm"
          >
            ← Back
          </Link>
          <h1 className="text-3xl font-bold text-gradient">
            {symbol}
          </h1>
        </div>

        {isLoading && (
          <div className="card p-8 text-center animate-pulse">
            <p className="text-muted">Loading signal data...</p>
          </div>
        )}

        {isError && error && (
          <div className="card-premium p-8 text-center border-red-500/30">
            <p className="text-danger">Error: {error.message}</p>
          </div>
        )}

        {signal && (
          <>
            {/* Current Signal */}
            <div className="card-premium p-8 mb-8 animate-fade-in">
              <h2 className="text-xl font-semibold mb-6 text-foreground-secondary">
                Current Signal
              </h2>
              <div className="text-center">
                <div
                  className={`text-5xl font-bold mb-4 ${
                    signal.signal_type === 'BUY'
                      ? 'text-success'
                      : signal.signal_type === 'SELL'
                      ? 'text-danger'
                      : 'text-muted'
                  }`}
                >
                  {signal.signal_type}
                </div>

                <div className="text-xl text-foreground-secondary mb-2">
                  ${signal.price_at_signal?.toFixed(2) || '-'}
                </div>

                <div className="text-lg text-muted mb-6">
                  Strength: {Math.round(signal.strength)}/100
                </div>

                {/* Strength meter */}
                <div className="max-w-md mx-auto mb-6">
                  <div className="h-3 bg-background-tertiary rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${
                        signal.strength >= 70
                          ? 'bg-success'
                          : signal.strength >= 40
                          ? 'bg-warning'
                          : 'bg-danger'
                      }`}
                      style={{ width: `${signal.strength}%` }}
                    />
                  </div>
                </div>

                {signal.reasoning && signal.reasoning.length > 0 && (
                  <div className="mt-6 text-foreground-secondary">
                    <p className="mb-3 font-semibold">Reasoning:</p>
                    <ul className="text-left max-w-md mx-auto space-y-2">
                      {signal.reasoning.map((reason: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="text-primary">•</span>
                          <span>{reason}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>

            {/* Price Chart Placeholder */}
            <div className="card p-6 mb-8 animate-slide-up">
              <h2 className="text-xl font-semibold mb-4 text-foreground-secondary">
                Price Chart
              </h2>
              <div className="h-64 flex items-center justify-center bg-background-tertiary rounded-xl">
                <p className="text-muted">Chart coming in Phase 2</p>
              </div>
            </div>

            {/* Indicators Grid */}
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="card p-6 animate-slide-up">
                <h3 className="text-lg font-semibold mb-4 text-foreground-secondary">
                  RSI Indicator
                </h3>
                <div className="h-48 flex items-center justify-center bg-background-tertiary rounded-xl">
                  <p className="text-muted">RSI chart placeholder</p>
                </div>
              </div>

              <div className="card p-6 animate-slide-up-delayed">
                <h3 className="text-lg font-semibold mb-4 text-foreground-secondary">
                  EMA Indicators
                </h3>
                <div className="h-48 flex items-center justify-center bg-background-tertiary rounded-xl">
                  <p className="text-muted">EMA chart placeholder</p>
                </div>
              </div>
            </div>

            {/* Signal History */}
            <div className="card p-6 animate-slide-up-delayed">
              <h2 className="text-xl font-semibold mb-4 text-foreground-secondary">
                Signal History (Coming Soon)
              </h2>
              <div className="text-muted text-center py-8">
                Historical signals table will be added in Phase 2
              </div>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
