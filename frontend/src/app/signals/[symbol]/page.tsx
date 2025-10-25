/**
 * Symbol Detail Page
 *
 * Detailed view of a specific symbol with live signals, price history, and roadmap placeholders.
 */

"use client";

import { use, useMemo, useState } from "react";
import Link from "next/link";
import SymbolPriceChart from "@/components/charts/SymbolPriceChart";
import {
  useBacktestSummary,
  useMarketData,
  useSignalBySymbol,
} from "@/lib/hooks/useSignals";

type RangeValue = "1m" | "3m" | "6m" | "1y" | "2y";

const RANGE_OPTIONS: { label: string; value: RangeValue }[] = [
  { label: "1M", value: "1m" },
  { label: "3M", value: "3m" },
  { label: "6M", value: "6m" },
  { label: "1Y", value: "1y" },
  { label: "2Y", value: "2y" },
];

const formatDate = (input?: string | null) => {
  if (!input) return "-";
  const date = new Date(input);
  if (Number.isNaN(date.getTime())) return "-";
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
};

export default function SignalDetail({
  params,
}: {
  params: Promise<{ symbol: string }>;
}) {
  const { symbol } = use(params);
  const [selectedRange, setSelectedRange] = useState<RangeValue>("1y");

  const { data: signal, isLoading, isError, error } = useSignalBySymbol(symbol);

  const {
    data: marketData = [],
    isLoading: marketLoading,
    isError: marketError,
    error: marketErrorObj,
  } = useMarketData(symbol, selectedRange);

  const { data: backtestSummary, isLoading: backtestLoading } =
    useBacktestSummary(symbol, selectedRange);

  const rangeStats = useMemo(() => {
    if (!marketData.length) return null;
    const start = marketData[0];
    const end = marketData[marketData.length - 1];
    const change = start.close
      ? ((end.close - start.close) / start.close) * 100
      : 0;
    return { start, end, change };
  }, [marketData]);

  const confidence = signal
    ? Math.max(0, Math.min(100, Math.round(signal.strength ?? 0)))
    : 0;
  const confidenceLabel =
    confidence >= 70 ? "Strong" : confidence >= 40 ? "Moderate" : "Weak";
  const confidenceBarClass =
    confidence >= 70
      ? "bg-success"
      : confidence >= 40
      ? "bg-warning"
      : "bg-danger";

  return (
    <main className="min-h-screen py-8 px-4">
      <div className="container-app">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between gap-6 flex-wrap">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="btn-secondary px-4 py-2 text-sm">
              ← Back
            </Link>
            <h1 className="text-3xl font-bold text-gradient">{symbol}</h1>
          </div>
          <p className="text-sm text-muted">
            Last updated {formatDate(signal?.timestamp)}
          </p>
        </div>

        {isLoading && (
          <div className="card p-8 text-center animate-pulse mb-8">
            <p className="text-muted">Loading signal data...</p>
          </div>
        )}

        {isError && error && (
          <div className="card-premium p-8 text-center border-red-500/30 mb-8">
            <p className="text-danger">Error: {error.message}</p>
          </div>
        )}

        {signal && (
          <>
            <div className="grid gap-6 lg:grid-cols-3 mb-8">
              {/* Current Signal */}
              <div className="card-premium p-8 flex flex-col justify-between">
                <div>
                  <p className="text-sm text-muted mb-3">Current Signal</p>
                  <div
                    className={`text-5xl font-bold mb-4 ${
                      signal.signal_type === "BUY"
                        ? "text-success"
                        : signal.signal_type === "SELL"
                        ? "text-danger"
                        : "text-muted"
                    }`}
                  >
                    {signal.signal_type}
                  </div>
                  <p className="text-xl text-foreground-secondary mb-1">
                    ${signal.price_at_signal?.toFixed(2) ?? "-"}
                  </p>
                  <p className="text-sm text-foreground-muted mb-6">
                    Generated at {formatDate(signal.timestamp)}
                  </p>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm text-muted uppercase">
                      <span>Confidence</span>
                      <span>{confidenceLabel}</span>
                    </div>
                    <div className="h-3 bg-background-tertiary rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-500 ${confidenceBarClass}`}
                        style={{ width: `${confidence}%` }}
                      />
                    </div>
                    <p className="text-3xl font-semibold text-foreground-secondary font-mono">
                      {confidence}%
                    </p>
                  </div>
                </div>

                {signal.reasoning && signal.reasoning.length > 0 && (
                  <div className="mt-8 text-left">
                    <p className="text-sm text-muted uppercase mb-2">
                      Reasoning
                    </p>
                    <ul className="space-y-2 text-sm text-foreground-secondary">
                      {signal.reasoning.map((reason: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="text-primary mt-0.5">•</span>
                          <span>{reason}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Price chart */}
              <div className="card lg:col-span-2 p-6 flex flex-col">
                <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
                  <h2 className="text-xl font-semibold text-foreground-secondary">
                    Price Chart
                  </h2>
                  <div className="flex flex-wrap gap-2">
                    {RANGE_OPTIONS.map((option) => (
                      <button
                        key={option.value}
                        type="button"
                        onClick={() => setSelectedRange(option.value)}
                        className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
                          selectedRange === option.value
                            ? "bg-primary/20 text-primary border border-primary/60 shadow-[0_0_10px_rgba(16,185,129,0.3)]"
                            : "border-border text-foreground-secondary hover:text-foreground"
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </div>

                {marketLoading && (
                  <div className="h-64 flex items-center justify-center text-muted animate-pulse bg-background-tertiary rounded-xl">
                    Fetching {selectedRange.toUpperCase()} data...
                  </div>
                )}

                {marketError && (
                  <div className="h-64 flex items-center justify-center text-danger bg-danger/10 rounded-xl text-center px-6">
                    Failed to load market data:{" "}
                    {String(marketErrorObj?.message ?? marketErrorObj)}
                  </div>
                )}

                {!marketLoading && !marketError && marketData.length === 0 && (
                  <div className="h-64 flex items-center justify-center text-muted bg-background-tertiary rounded-xl">
                    No market data found. Run the Prefect backfill to seed
                    history.
                  </div>
                )}

                {!marketLoading && !marketError && marketData.length > 0 && (
                  <>
                    <SymbolPriceChart
                      symbol={symbol}
                      data={marketData.map((point) => ({
                        timestamp: point.timestamp,
                        close: point.close,
                      }))}
                      range={selectedRange}
                    />
                    {rangeStats && (
                      <div className="mt-6 grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-xs text-muted uppercase mb-1">
                            Range return
                          </p>
                          <p
                            className={`text-lg font-semibold ${
                              rangeStats.change >= 0
                                ? "text-success"
                                : "text-danger"
                            }`}
                          >
                            {rangeStats.change >= 0 ? "+" : ""}
                            {rangeStats.change.toFixed(2)}%
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted uppercase mb-1">
                            Start
                          </p>
                          <p className="font-mono text-foreground-secondary">
                            ${rangeStats.start.close.toFixed(2)}
                          </p>
                          <p className="text-xs text-muted">
                            {formatDate(rangeStats.start.timestamp)}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted uppercase mb-1">
                            End
                          </p>
                          <p className="font-mono text-foreground-secondary">
                            ${rangeStats.end.close.toFixed(2)}
                          </p>
                          <p className="text-xs text-muted">
                            {formatDate(rangeStats.end.timestamp)}
                          </p>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <div className="card p-6 animate-slide-up">
                <h3 className="text-lg font-semibold mb-4 text-foreground-secondary">
                  Next Steps
                </h3>
                <ul className="space-y-3 text-sm text-foreground-secondary">
                  <li className="flex gap-2">
                    <span className="text-primary">•</span>
                    <span>
                      Compare the chart above with your preferred broker to
                      validate pricing.
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary">•</span>
                    <span>
                      Use the range selector to inspect 1M–5Y performance before
                      tweaking rules.
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary">•</span>
                    <span>
                      Run{" "}
                      <code className="font-mono text-xs">
                        python -m flows.signal_generation --mode backfill
                        --backfill-range 5y
                      </code>{" "}
                      to refresh history.
                    </span>
                  </li>
                </ul>
              </div>

              <div className="card p-6 animate-slide-up">
                <h3 className="text-lg font-semibold mb-4 text-foreground-secondary">
                  Backtest Preview
                </h3>
                {backtestLoading && (
                  <div className="h-32 flex items-center justify-center text-muted animate-pulse">
                    Loading summary...
                  </div>
                )}
                {!backtestLoading && (
                  <>
                    <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                      <div>
                        <p className="text-xs text-muted uppercase mb-1">
                          Win Rate
                        </p>
                        <p className="text-2xl font-semibold">
                          {(backtestSummary?.win_rate ?? 0).toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted uppercase mb-1">
                          Trades
                        </p>
                        <p className="text-2xl font-semibold">
                          {backtestSummary?.trades ?? 0}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted uppercase mb-1">
                          Avg Return / Trade
                        </p>
                        <p className="text-2xl font-semibold">
                          {(backtestSummary?.avg_return ?? 0).toFixed(2)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted uppercase mb-1">
                          Total Return
                        </p>
                        <p className="text-2xl font-semibold">
                          {(backtestSummary?.total_return ?? 0).toFixed(2)}%
                        </p>
                      </div>
                    </div>
                    <p className="text-xs text-foreground-muted">
                      {backtestSummary?.notes ??
                        "Detailed backtesting metrics will appear here once the pipeline is ready."}
                    </p>
                    <p className="text-xs text-muted mt-2">
                      Last trained{" "}
                      {formatDate(backtestSummary?.last_trained_at)}
                    </p>
                  </>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
