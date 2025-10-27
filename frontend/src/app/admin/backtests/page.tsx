"use client"

import { useMemo, useState, useEffect } from "react"
import Link from "next/link"

import { useSignals, useMarketData, useBacktestSummary } from "@/lib/hooks/useSignals"

const RANGE_OPTIONS = ["1m", "3m", "6m", "1y", "2y"] as const
const DEFAULT_SYMBOLS = ["BTC-USD", "AAPL", "IVV", "BRL=X"]

export default function AdminBacktestsPage() {
  const {
    data: signals = [],
    isLoading: signalsLoading,
    isError: signalsError,
    error: signalsErrorObj,
    refetch: refetchSignals,
  } = useSignals()

  const availableSymbols = useMemo(() => {
    const fromSignals = Array.from(new Set(signals.map((s) => s.symbol)))
    return fromSignals.length ? fromSignals : DEFAULT_SYMBOLS
  }, [signals])

  const [selectedSymbol, setSelectedSymbol] = useState(
    availableSymbols[0] || DEFAULT_SYMBOLS[0],
  )
  const [range, setRange] = useState<(typeof RANGE_OPTIONS)[number]>("1y")

  useEffect(() => {
    if (!availableSymbols.includes(selectedSymbol) && availableSymbols.length) {
      setSelectedSymbol(availableSymbols[0])
    }
  }, [availableSymbols, selectedSymbol])

  const {
    data: marketData = [],
    isLoading: marketLoading,
    isError: marketError,
    error: marketErrorObj,
    refetch: refetchMarket,
  } = useMarketData(selectedSymbol, range)

  const {
    data: backtestSummary,
    isLoading: backtestLoading,
    isError: backtestError,
    error: backtestErrorObj,
    refetch: refetchBacktest,
  } = useBacktestSummary(selectedSymbol, range)

  const latestSignal = signals.find((s) => s.symbol === selectedSymbol)

  const handleRefresh = () => {
    void Promise.all([refetchSignals(), refetchMarket(), refetchBacktest()])
  }

  return (
    <div className="space-y-8">
      <header className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold">Backtests & Diagnostics</h1>
          <p className="text-sm text-muted">
            Verify that the latest Prefect replay populated signals, indicators, and summary stats.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/admin" className="text-sm text-muted hover:text-foreground transition-colors">
            ← Admin home
          </Link>
          <button
            type="button"
            onClick={handleRefresh}
            className="btn-secondary px-4 py-2 text-sm border border-border hover:border-border-accent"
          >
            Refresh data
          </button>
        </div>
      </header>

      <section className="card p-6 space-y-4">
        <div className="flex flex-wrap items-center gap-4">
          <label className="text-sm uppercase tracking-wide text-muted">Symbol</label>
          <select
            className="bg-background-tertiary border border-border rounded px-3 py-2 text-sm"
            value={selectedSymbol}
            onChange={(event) => setSelectedSymbol(event.target.value)}
          >
            {availableSymbols.map((symbol) => (
              <option key={symbol} value={symbol}>
                {symbol}
              </option>
            ))}
          </select>

          <div className="flex items-center gap-2">
            {RANGE_OPTIONS.map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => setRange(option)}
                className={`px-3 py-1 rounded-full text-sm border transition-colors ${
                  range === option
                    ? "bg-primary/20 text-primary border-primary/60"
                    : "border-border text-foreground-secondary hover:text-foreground"
                }`}
              >
                {option.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
        <p className="text-xs text-muted">
          Signals refresh every 60s; market data cached for 5m; backtests reload on demand. After
          running the replay flow, hit Refresh to pull the latest metrics.
        </p>
      </section>

      <section className="card p-6 space-y-4">
        <header className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Signals ({signals.length})</h2>
          {signalsLoading && <span className="text-sm text-muted">Loading…</span>}
        </header>
        {signalsError && (
          <div className="text-danger text-sm">
            Failed to load signals: {String(signalsErrorObj?.message ?? signalsErrorObj)}
          </div>
        )}
        {!signalsError && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-muted border-b border-border">
                  <th className="py-2 pr-4">Symbol</th>
                  <th className="py-2 pr-4">Type</th>
                  <th className="py-2 pr-4">Strength</th>
                  <th className="py-2 pr-4">Price</th>
                  <th className="py-2 pr-4">Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {signals.slice(0, 25).map((signal) => (
                  <tr key={signal.id} className="border-b border-border/40">
                    <td className="py-2 pr-4 font-mono">{signal.symbol}</td>
                    <td className="py-2 pr-4">{signal.signal_type}</td>
                    <td className="py-2 pr-4">{Math.round(signal.strength)} / 100</td>
                    <td className="py-2 pr-4">
                      ${signal.price_at_signal?.toFixed(2) ?? "-"}
                    </td>
                    <td className="py-2 pr-4 text-muted">
                      {new Date(signal.timestamp).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="grid md:grid-cols-2 gap-6">
        <div className="card p-6 space-y-3">
          <header className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold">Market Data</h2>
              <p className="text-sm text-muted">
                {selectedSymbol} · range {range.toUpperCase()}
              </p>
            </div>
            {marketLoading && <span className="text-sm text-muted">Loading…</span>}
          </header>
          {marketError && (
            <div className="text-danger text-sm">
              Failed to load market data: {String(marketErrorObj?.message ?? marketErrorObj)}
            </div>
          )}
          {!marketError && (
            <>
              <p className="text-sm text-muted">
                Showing {marketData.length} rows. Latest close:{" "}
                <span className="text-foreground font-semibold">
                  ${marketData[marketData.length - 1]?.close?.toFixed(2) ?? "-"}
                </span>
              </p>
              <pre className="bg-black/40 text-xs p-4 rounded overflow-x-auto max-h-64">
                {JSON.stringify(marketData.slice(-5), null, 2)}
              </pre>
            </>
          )}
        </div>
        <div className="card p-6 space-y-3">
          <header className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Backtest Summary</h2>
            {backtestLoading && <span className="text-sm text-muted">Loading…</span>}
          </header>
          {backtestError && (
            <div className="text-danger text-sm">
              Failed to load backtest: {String(backtestErrorObj?.message ?? backtestErrorObj)}
            </div>
          )}
          {!backtestError && backtestSummary && (
            <div className="space-y-2 text-sm">
              <p>Trades: {backtestSummary.trades}</p>
              <p>Win Rate: {backtestSummary.win_rate.toFixed(2)}%</p>
              <p>Avg Return: {backtestSummary.avg_return.toFixed(2)}%</p>
              <p>Total Return: {backtestSummary.total_return.toFixed(2)}%</p>
              <p className="text-muted text-xs">
                Last trained {backtestSummary.last_trained_at || "n/a"}
              </p>
              {backtestSummary.notes && (
                <p className="text-xs text-muted">Notes: {backtestSummary.notes}</p>
              )}
            </div>
          )}
        </div>
      </section>

      <section className="card p-6 space-y-3">
        <header className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Latest Signal JSON</h2>
          {latestSignal && (
            <span className="text-sm text-muted">{selectedSymbol} current signal snapshot</span>
          )}
        </header>
        {latestSignal ? (
          <pre className="bg-black/40 text-xs p-4 rounded overflow-x-auto">
            {JSON.stringify(latestSignal, null, 2)}
          </pre>
        ) : (
          <p className="text-sm text-muted">
            No signal found for {selectedSymbol}. Run the pipeline first.
          </p>
        )}
      </section>
    </div>
  )
}
