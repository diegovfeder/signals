/**
 * Signals Page
 *
 * Browse all trading signals across all symbols with filtering and sorting.
 */

'use client'

import { useSignals } from '@/lib/hooks/useSignals'
import Link from 'next/link'
import { useState, useMemo } from 'react'

type SignalType = 'BUY' | 'SELL' | 'HOLD' | 'ALL'
type SortKey = 'timestamp' | 'symbol' | 'strength'
type SortOrder = 'asc' | 'desc'

export default function SignalsPage() {
  const { signals, loading, error } = useSignals()
  const [filterType, setFilterType] = useState<SignalType>('ALL')
  const [sortKey, setSortKey] = useState<SortKey>('timestamp')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')

  // Filtered and sorted signals
  const filteredSignals = useMemo(() => {
    let filtered = signals

    // Filter by signal type
    if (filterType !== 'ALL') {
      filtered = filtered.filter((s) => s.signal_type === filterType)
    }

    // Sort
    filtered = [...filtered].sort((a, b) => {
      let comparison = 0

      switch (sortKey) {
        case 'timestamp':
          comparison =
            new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
          break
        case 'symbol':
          comparison = a.symbol.localeCompare(b.symbol)
          break
        case 'strength':
          comparison = a.strength - b.strength
          break
      }

      return sortOrder === 'asc' ? comparison : -comparison
    })

    return filtered
  }, [signals, filterType, sortKey, sortOrder])

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      // Toggle order if same key
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortOrder('desc')
    }
  }

  const getSignalBadgeClasses = (signalType: string) => {
    switch (signalType) {
      case 'BUY':
        return 'bg-success/20 text-success border-success/30'
      case 'SELL':
        return 'bg-danger/20 text-danger border-danger/30'
      default:
        return 'bg-neutral/20 text-neutral border-neutral/30'
    }
  }

  const getStrengthColor = (strength: number) => {
    if (strength >= 70) return 'bg-success'
    if (strength >= 40) return 'bg-warning'
    return 'bg-danger'
  }

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
            All Signals
          </h1>
          <p className="text-foreground-muted">
            Complete history of trading signals across all tracked symbols
          </p>
        </div>

        {/* Filters */}
        <div className="mb-6 flex flex-wrap gap-4 items-center animate-slide-up">
          <div className="flex gap-2">
            <button
              onClick={() => setFilterType('ALL')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filterType === 'ALL'
                  ? 'bg-primary/20 text-primary border border-primary/30'
                  : 'bg-background-card text-foreground-muted border border-border hover:border-border-hover'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilterType('BUY')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filterType === 'BUY'
                  ? 'bg-success/20 text-success border border-success/30'
                  : 'bg-background-card text-foreground-muted border border-border hover:border-border-hover'
              }`}
            >
              Buy
            </button>
            <button
              onClick={() => setFilterType('SELL')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filterType === 'SELL'
                  ? 'bg-danger/20 text-danger border border-danger/30'
                  : 'bg-background-card text-foreground-muted border border-border hover:border-border-hover'
              }`}
            >
              Sell
            </button>
            <button
              onClick={() => setFilterType('HOLD')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filterType === 'HOLD'
                  ? 'bg-neutral/20 text-neutral border border-neutral/30'
                  : 'bg-background-card text-foreground-muted border border-border hover:border-border-hover'
              }`}
            >
              Hold
            </button>
          </div>
          <div className="ml-auto text-sm text-foreground-muted">
            {filteredSignals.length} signal
            {filteredSignals.length !== 1 ? 's' : ''}
          </div>
        </div>

        {/* Error state */}
        {error && (
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
        {loading && (
          <div className="card p-8 text-center animate-pulse">
            <p className="text-muted">Loading signals...</p>
          </div>
        )}

        {/* Signals Table */}
        {!loading && !error && filteredSignals.length > 0 && (
          <div className="card overflow-hidden animate-slide-up">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th
                      className="text-left px-6 py-4 text-sm font-semibold text-foreground-secondary cursor-pointer hover:text-foreground transition-colors"
                      onClick={() => handleSort('symbol')}
                    >
                      <div className="flex items-center gap-2">
                        Symbol
                        {sortKey === 'symbol' && (
                          <span className="text-xs">
                            {sortOrder === 'asc' ? '↑' : '↓'}
                          </span>
                        )}
                      </div>
                    </th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-foreground-secondary">
                      Signal
                    </th>
                    <th
                      className="text-left px-6 py-4 text-sm font-semibold text-foreground-secondary cursor-pointer hover:text-foreground transition-colors"
                      onClick={() => handleSort('strength')}
                    >
                      <div className="flex items-center gap-2">
                        Strength
                        {sortKey === 'strength' && (
                          <span className="text-xs">
                            {sortOrder === 'asc' ? '↑' : '↓'}
                          </span>
                        )}
                      </div>
                    </th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-foreground-secondary">
                      Price
                    </th>
                    <th
                      className="text-left px-6 py-4 text-sm font-semibold text-foreground-secondary cursor-pointer hover:text-foreground transition-colors"
                      onClick={() => handleSort('timestamp')}
                    >
                      <div className="flex items-center gap-2">
                        Time
                        {sortKey === 'timestamp' && (
                          <span className="text-xs">
                            {sortOrder === 'asc' ? '↑' : '↓'}
                          </span>
                        )}
                      </div>
                    </th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-foreground-secondary">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSignals.map((signal, idx) => (
                    <tr
                      key={signal.id}
                      className="border-b border-border hover:bg-background-card/50 transition-colors"
                      style={{ animationDelay: `${idx * 30}ms` }}
                    >
                      <td className="px-6 py-4">
                        <Link
                          href={`/signals/${signal.symbol}`}
                          className="font-mono font-semibold text-foreground hover:text-primary transition-colors"
                        >
                          {signal.symbol}
                        </Link>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold border ${getSignalBadgeClasses(
                            signal.signal_type
                          )}`}
                        >
                          {signal.signal_type}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-20 h-2 bg-background-tertiary rounded-full overflow-hidden">
                            <div
                              className={`h-full transition-all ${getStrengthColor(
                                signal.strength
                              )}`}
                              style={{ width: `${signal.strength}%` }}
                            />
                          </div>
                          <span className="text-sm font-mono text-foreground-muted">
                            {Math.round(signal.strength)}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 font-mono text-sm text-foreground-secondary">
                        ${signal.price_at_signal?.toFixed(2) || '-'}
                      </td>
                      <td className="px-6 py-4 text-sm text-foreground-muted">
                        {new Date(signal.timestamp).toLocaleString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </td>
                      <td className="px-6 py-4">
                        <Link
                          href={`/signals/${signal.symbol}`}
                          className="text-sm text-primary hover:text-primary-hover transition-colors"
                        >
                          Details →
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Empty state */}
        {!loading && !error && filteredSignals.length === 0 && (
          <div className="card p-12 text-center animate-slide-up">
            <p className="text-muted text-lg mb-2">No signals found</p>
            <p className="text-sm text-foreground-muted">
              {filterType !== 'ALL'
                ? `Try changing the filter to see more signals`
                : `Signals will appear here once the pipeline generates them`}
            </p>
          </div>
        )}

        {/* Quick navigation */}
        {!loading && !error && signals.length > 0 && (
          <div className="mt-8 text-center animate-fade-in">
            <Link href="/dashboard" className="btn-secondary inline-block">
              View Dashboard
            </Link>
          </div>
        )}
      </div>
    </main>
  )
}
