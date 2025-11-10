"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  useSignals,
  useMarketData,
  useBacktestSummary,
} from "@/lib/hooks/useSignals";
import {
  DEFAULT_SYMBOLS,
  RANGE_OPTIONS,
  RangeValue,
} from "@/lib/utils/constants";

export default function AdminBacktestsPage() {
  const {
    data: signals = [],
    isLoading: signalsLoading,
    isError: signalsError,
    error: signalsErrorObj,
    refetch: refetchSignals,
  } = useSignals();

  const availableSymbols = useMemo(() => {
    const fromSignals = Array.from(new Set(signals.map((s) => s.symbol)));
    return fromSignals.length ? fromSignals : DEFAULT_SYMBOLS;
  }, [signals]);

  const [userSelectedSymbol, setUserSelectedSymbol] = useState<string | null>(
    availableSymbols[0] || DEFAULT_SYMBOLS[0],
  );
  const selectedSymbol = useMemo(() => {
    if (userSelectedSymbol && availableSymbols.includes(userSelectedSymbol)) {
      return userSelectedSymbol;
    }
    return availableSymbols[0] || DEFAULT_SYMBOLS[0];
  }, [userSelectedSymbol, availableSymbols]);
  const [range, setRange] = useState<RangeValue>("1y");

  const {
    data: marketData = [],
    isLoading: marketLoading,
    isError: marketError,
    error: marketErrorObj,
    refetch: refetchMarket,
  } = useMarketData(selectedSymbol, range);

  const {
    data: backtestSummary,
    isLoading: backtestLoading,
    isError: backtestError,
    error: backtestErrorObj,
    refetch: refetchBacktest,
  } = useBacktestSummary(selectedSymbol, range);

  const isAnyLoading = marketLoading || backtestLoading || signalsLoading;
  const latestSignal = signals.find((s) => s.symbol === selectedSymbol);

  const handleRefresh = () => {
    void Promise.all([refetchSignals(), refetchMarket(), refetchBacktest()]);
  };

  return (
    <div className="space-y-8">
      <header className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            Backtests & Diagnostics
          </h1>
          <p className="text-sm text-muted-foreground">
            Verify that the latest Prefect replay populated signals, indicators,
            and summary stats.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={handleRefresh}
            variant="secondary"
            size="sm"
            loading={isAnyLoading}
            disabled={isAnyLoading}
          >
            Refresh data
          </Button>
          <Link
            href="/admin"
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Go back to admin home
          </Link>
        </div>
      </header>

      <Card className="p-6 space-y-4 border border-border">
        <div className="flex flex-wrap items-center gap-4">
          <label className="text-sm uppercase tracking-wide text-muted-foreground">
            Symbol
          </label>
          <select
            className="bg-muted border border-border rounded px-3 py-2 text-sm text-foreground"
            value={selectedSymbol}
            onChange={(event) => setUserSelectedSymbol(event.target.value)}
          >
            {availableSymbols.map((symbol) => (
              <option key={symbol} value={symbol}>
                {symbol}
              </option>
            ))}
          </select>

          <div className="flex items-center gap-2">
            {RANGE_OPTIONS.map((option) => (
              <Badge
                key={option.value}
                onClick={() => setRange(option.value)}
                className={`px-3 py-1.5 cursor-pointer text-sm transition-all ${
                  range === option.value
                    ? "bg-primary border-primary text-white"
                    : "bg-card border-border text-muted-foreground hover:border-primary/50 hover:text-foreground hover:bg-card"
                }`}
              >
                {option.label}
              </Badge>
            ))}
          </div>
        </div>
      </Card>

      <section className="grid md:grid-cols-2 gap-6">
        <Card className="p-6 space-y-3 border border-border">
          <header className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-foreground">
                Market Data
              </h2>
              <p className="text-sm text-muted-foreground">
                {selectedSymbol} · range {range.toUpperCase()}
              </p>
            </div>
            {marketLoading && (
              <span className="text-sm text-muted-foreground">Loading…</span>
            )}
          </header>
          {marketError && (
            <div className="text-red-600 text-sm">
              Failed to load market data:&nbsp;
              {String(marketErrorObj?.message ?? marketErrorObj)}
            </div>
          )}
          {!marketError && (
            <>
              <p className="text-sm text-muted-foreground">
                Showing {marketData.length} rows. Latest close:&nbsp;
                <span className="text-foreground font-semibold">
                  ${marketData[marketData.length - 1]?.close?.toFixed(2) ?? "-"}
                </span>
              </p>
              <pre className="bg-muted text-xs text-foreground p-4 rounded overflow-x-auto max-h-64">
                {JSON.stringify(marketData.slice(-5), null, 2)}
              </pre>
            </>
          )}
        </Card>
        <Card className="p-6 space-y-3 border border-border">
          <header className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-foreground">
              Backtest Summary
            </h2>
            {backtestLoading && (
              <span className="text-sm text-muted-foreground">Loading…</span>
            )}
          </header>
          {backtestError && (
            <div className="text-red-600 text-sm">
              Failed to load backtest:&nbsp;
              {String(backtestErrorObj?.message ?? backtestErrorObj)}
            </div>
          )}
          {!backtestError && backtestSummary && (
            <div className="space-y-2 text-sm text-foreground">
              <p>Trades: {backtestSummary.trades}</p>
              <p>Win Rate: {backtestSummary.win_rate.toFixed(2)}%</p>
              <p>Avg Return: {backtestSummary.avg_return.toFixed(2)}%</p>
              <p>Total Return: {backtestSummary.total_return.toFixed(2)}%</p>
              <p className="text-muted-foreground text-xs">
                Last trained {backtestSummary.last_trained_at || "n/a"}
              </p>
              {backtestSummary.notes && (
                <p className="text-xs text-muted-foreground">
                  Notes: {backtestSummary.notes}
                </p>
              )}
            </div>
          )}
        </Card>
      </section>

      <Card className="p-6 space-y-3 border border-border">
        <header className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-foreground">
            Latest Signal JSON
          </h2>
          {latestSignal && (
            <span className="text-sm text-muted-foreground">
              {selectedSymbol} current signal snapshot
            </span>
          )}
        </header>
        {latestSignal ? (
          <pre className="bg-muted text-xs text-foreground p-4 rounded overflow-x-auto">
            {JSON.stringify(latestSignal, null, 2)}
          </pre>
        ) : (
          <p className="text-sm text-muted-foreground">
            No signal found for {selectedSymbol}. Run the pipeline first.
          </p>
        )}
      </Card>

      <Card className="p-6 space-y-4 border border-border">
        <header className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-foreground">
            Signals ({signals.length})
          </h2>
          {signalsLoading && (
            <span className="text-sm text-muted-foreground">Loading…</span>
          )}
        </header>
        {signalsError && (
          <div className="text-red-600 text-sm">
            Failed to load signals:&nbsp;
            {String(signalsErrorObj?.message ?? signalsErrorObj)}
          </div>
        )}
        {!signalsError && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-muted-foreground border-b border-border">
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
                    <td className="py-2 pr-4 font-mono text-foreground">
                      {signal.symbol}
                    </td>
                    <td className="py-2 pr-4 text-foreground">
                      {signal.signal_type}
                    </td>
                    <td className="py-2 pr-4 text-foreground">
                      {Math.round(signal.strength)} / 100
                    </td>
                    <td className="py-2 pr-4 text-foreground">
                      ${signal.price_at_signal?.toFixed(2) ?? "-"}
                    </td>
                    <td className="py-2 pr-4 text-muted-foreground">
                      {new Date(signal.timestamp).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
