/**
 * Signals Page
 *
 * Browse all trading signals across all symbols with filtering and sorting.
 */

'use client'

import { useSignals, type Signal } from '@/lib/hooks/useSignals'
import Link from 'next/link'
import { useState, useMemo } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

type SignalType = 'BUY' | 'SELL' | 'HOLD' | 'ALL'
type SortKey = 'timestamp' | 'symbol' | 'strength'
type SortOrder = 'asc' | 'desc'

export default function SignalsPage() {
  const {
    data: signals = [],
    isLoading,
    isError,
    error,
  } = useSignals()
  const [filterType, setFilterType] = useState<SignalType>('ALL')
  const [sortKey, setSortKey] = useState<SortKey>('timestamp')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')

  // Filtered and sorted signals
  const filteredSignals = useMemo<Signal[]>(() => {
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
        return 'bg-primary text-primary-foreground border-0'
      case 'SELL':
        return 'bg-red-600 text-white border-0'
      default:
        return 'bg-muted text-muted-foreground border-0'
    }
  }

  const getStrengthColor = (strength: number) => {
    if (strength >= 70) return 'bg-primary'
    if (strength >= 40) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <main className="min-h-screen py-8 px-4">
      <div className="container-app">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <Link
            href="/"
            className="inline-block text-sm text-muted-foreground hover:text-foreground mb-4 transition-colors"
          >
            ← Home
          </Link>
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-2">
            All Signals
          </h1>
          <p className="text-muted-foreground">
            Complete history of trading signals across all tracked symbols
          </p>
        </div>

        {/* Filters */}
        <div className="mb-6 flex flex-wrap gap-4 items-center animate-slide-up">
          <div className="flex gap-2">
            <Badge
              onClick={() => setFilterType('ALL')}
              className={`px-4 py-2 cursor-pointer transition-all ${
                filterType === 'ALL'
                  ? 'bg-primary/20 text-ring border border-primary/40'
                  : 'bg-card text-muted-foreground border border-border hover:border-ring'
              }`}
            >
              All
            </Badge>
            <Badge
              onClick={() => setFilterType('BUY')}
              className={`px-4 py-2 cursor-pointer transition-all ${
                filterType === 'BUY'
                  ? 'bg-primary text-primary-foreground border-0'
                  : 'bg-card text-muted-foreground border border-border hover:border-ring'
              }`}
            >
              Buy
            </Badge>
            <Badge
              onClick={() => setFilterType('SELL')}
              className={`px-4 py-2 cursor-pointer transition-all ${
                filterType === 'SELL'
                  ? 'bg-red-600 text-white border-0'
                  : 'bg-card text-muted-foreground border border-border hover:border-ring'
              }`}
            >
              Sell
            </Badge>
            <Badge
              onClick={() => setFilterType('HOLD')}
              className={`px-4 py-2 cursor-pointer transition-all ${
                filterType === 'HOLD'
                  ? 'bg-muted text-muted-foreground border-0'
                  : 'bg-card text-muted-foreground border border-border hover:border-ring'
              }`}
            >
              Hold
            </Badge>
          </div>
          <div className="ml-auto text-sm text-muted-foreground">
            {filteredSignals.length} signal
            {filteredSignals.length !== 1 ? 's' : ''}
          </div>
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
          <div className="card p-8 text-center animate-pulse">
            <p className="text-muted">Loading signals...</p>
          </div>
        )}

        {/* Signals Table */}
        {!isLoading && !isError && filteredSignals.length > 0 && (
          <Card className="overflow-hidden animate-slide-up border-2">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th
                      className="text-left px-6 py-4 text-sm font-semibold text-foreground cursor-pointer hover:text-ring transition-colors"
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
                    <th className="text-left px-6 py-4 text-sm font-semibold text-foreground">
                      Signal
                    </th>
                    <th
                      className="text-left px-6 py-4 text-sm font-semibold text-foreground cursor-pointer hover:text-ring transition-colors"
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
                    <th className="text-left px-6 py-4 text-sm font-semibold text-foreground">
                      Price
                    </th>
                    <th
                      className="text-left px-6 py-4 text-sm font-semibold text-foreground cursor-pointer hover:text-ring transition-colors"
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
                    <th className="text-left px-6 py-4 text-sm font-semibold text-foreground">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSignals.map((signal, idx) => (
                    <tr
                      key={signal.id}
                      className="border-b border-border hover:bg-muted/30 transition-colors"
                      style={{ animationDelay: `${idx * 30}ms` }}
                    >
                      <td className="px-6 py-4">
                        <Link
                          href={`/signals/${signal.symbol}`}
                          className="font-mono font-semibold text-foreground hover:text-ring transition-colors"
                        >
                          {signal.symbol}
                        </Link>
                      </td>
                      <td className="px-6 py-4">
                        <Badge className={getSignalBadgeClasses(signal.signal_type)}>
                          {signal.signal_type}
                        </Badge>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className={`h-full transition-all ${getStrengthColor(
                                signal.strength
                              )}`}
                              style={{ width: `${signal.strength}%` }}
                            />
                          </div>
                          <span className="text-sm font-mono text-muted-foreground">
                            {Math.round(signal.strength)}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 font-mono text-sm text-foreground">
                        ${signal.price_at_signal?.toFixed(2) || '-'}
                      </td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">
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
                          className="text-sm text-ring hover:text-primary transition-colors"
                        >
                          Details →
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {/* Empty state */}
        {!isLoading && !isError && filteredSignals.length === 0 && (
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
        {!isLoading && !isError && signals.length > 0 && (
          <div className="mt-8 text-center animate-fade-in">
            <Button asChild variant="secondary" size="lg">
              <Link href="/dashboard">View Dashboard</Link>
            </Button>
          </div>
        )}
      </div>
    </main>
  )
}
