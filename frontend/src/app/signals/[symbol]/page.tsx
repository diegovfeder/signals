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
  useIndicators,
  useMarketData,
  useSignalBySymbol,
  useSignalHistory,
} from "@/lib/hooks/useSignals";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { RANGE_OPTIONS, RangeValue } from "@/lib/utils/constants";

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

  const {
    data: indicators = [],
    isLoading: indicatorsLoading,
    isError: indicatorsError,
    error: indicatorsErrorObj,
  } = useIndicators(symbol, selectedRange);

  const {
    data: signalHistory = [],
    isLoading: historyLoading,
    isError: historyError,
    error: historyErrorObj,
  } = useSignalHistory(symbol, selectedRange);

  const rangeStats = useMemo(() => {
    if (!marketData.length) return null;
    const start = marketData[0];
    const end = marketData[marketData.length - 1];
    const change = start.close
      ? ((end.close - start.close) / start.close) * 100
      : 0;
    return { start, end, change };
  }, [marketData]);

  const indicatorSnapshot = useMemo(() => {
    if (!indicators.length) return null;
    const latest = indicators[indicators.length - 1];
    return {
      rsi: latest.rsi,
      ema12: latest.ema12,
      ema26: latest.ema26,
    };
  }, [indicators]);

  const confidence = signal
    ? Math.max(0, Math.min(100, Math.round(signal.strength ?? 0)))
    : 0;
  const confidenceLabel =
    confidence >= 70 ? "Strong" : confidence >= 40 ? "Moderate" : "Weak";
  const confidenceBarClass =
    confidence >= 70
      ? "bg-primary"
      : confidence >= 40
        ? "bg-yellow-500"
        : "bg-red-500";

  return (
    <main className="min-h-screen py-8 px-4">
      <div className="container-app">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between gap-6 flex-wrap">
          <div className="flex items-center gap-4">
            <Button asChild variant="secondary" size="sm">
              <Link href="/signals">← Back</Link>
            </Button>
            <h1 className="text-3xl font-bold text-foreground">{symbol}</h1>
          </div>
          <p className="text-sm text-muted-foreground">
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
              <Card className="p-8 flex flex-col justify-between border border-border">
                <div>
                  <p className="text-sm text-muted-foreground mb-3">
                    Current Signal
                  </p>
                  <div
                    className={`text-5xl font-bold mb-4 ${
                      signal.signal_type === "BUY"
                        ? "text-primary"
                        : signal.signal_type === "SELL"
                          ? "text-red-600"
                          : "text-muted-foreground"
                    }`}
                  >
                    {signal.signal_type}
                  </div>
                  <p className="text-xl text-foreground mb-1">
                    ${signal.price_at_signal?.toFixed(2) ?? "-"}
                  </p>
                  <p className="text-sm text-muted-foreground mb-6">
                    Generated at {formatDate(signal.timestamp)}
                  </p>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm text-muted-foreground uppercase">
                      <span>Confidence</span>
                      <span>{confidenceLabel}</span>
                    </div>
                    <div className="h-3 bg-muted rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-500 ${confidenceBarClass}`}
                        style={{ width: `${confidence}%` }}
                      />
                    </div>
                    <p className="text-3xl font-semibold text-foreground font-mono">
                      {confidence}%
                    </p>
                  </div>
                </div>

                {signal.reasoning && signal.reasoning.length > 0 && (
                  <div className="mt-8 text-left">
                    <p className="text-sm text-muted-foreground uppercase mb-2">
                      Reasoning
                    </p>
                    <ul className="space-y-2 text-sm text-foreground/90">
                      {signal.reasoning.map((reason: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="text-ring mt-0.5">•</span>
                          <span>{reason}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </Card>

              {/* Price chart */}
              <Card className="lg:col-span-2 p-6 flex flex-col border border-border">
                <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
                  <h2 className="text-xl font-semibold text-foreground">
                    Price Chart
                  </h2>
                  <div className="flex flex-wrap gap-2">
                    {RANGE_OPTIONS.map((option) => (
                      <Badge
                        key={option.value}
                        onClick={() => setSelectedRange(option.value)}
                        className={`px-3 py-1.5 cursor-pointer text-sm transition-all ${
                          selectedRange === option.value
                            ? "bg-primary border-primary text-white"
                            : "bg-card border-border text-muted-foreground hover:border-primary/50 hover:text-foreground hover:bg-card"
                        }`}
                      >
                        {option.label}
                      </Badge>
                    ))}
                  </div>
                </div>

                {marketLoading && (
                  <div className="h-64 flex items-center justify-center text-muted-foreground animate-pulse bg-muted rounded-xl">
                    Fetching {selectedRange.toUpperCase()} data...
                  </div>
                )}

                {marketError && (
                  <div className="h-64 flex items-center justify-center text-red-600 bg-red-600/10 rounded-xl text-center px-6">
                    Failed to load market data:&nbsp;
                    {String(marketErrorObj?.message ?? marketErrorObj)}
                  </div>
                )}

                {!marketLoading && !marketError && marketData.length === 0 && (
                  <div className="h-64 flex items-center justify-center text-muted-foreground bg-muted rounded-xl">
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
                      indicators={indicators}
                      signals={signalHistory}
                      range={selectedRange}
                    />
                    {indicatorsLoading && (
                      <p className="text-xs text-muted-foreground mt-2">
                        Loading indicator overlays...
                      </p>
                    )}
                    {indicatorsError && indicatorsErrorObj && (
                      <p className="text-xs text-red-500 mt-2">
                        Indicator data unavailable: {String(
                          indicatorsErrorObj.message ?? indicatorsErrorObj,
                        )}
                      </p>
                    )}
                    {historyLoading && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Loading signal markers...
                      </p>
                    )}
                    {historyError && historyErrorObj && (
                      <p className="text-xs text-red-500 mt-1">
                        Signal history unavailable: {String(
                          historyErrorObj.message ?? historyErrorObj,
                        )}
                      </p>
                    )}
                    {rangeStats && (
                      <div className="mt-6 grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-xs text-muted-foreground uppercase mb-1">
                            Range return
                          </p>
                          <p
                            className={`text-lg font-semibold text-foreground`}
                          >
                            {rangeStats.change >= 0 ? "+" : ""}
                            {rangeStats.change.toFixed(2)}%
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground uppercase mb-1">
                            Start
                          </p>
                          <p className="font-mono text-foreground">
                            ${rangeStats.start.close.toFixed(2)}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {formatDate(rangeStats.start.timestamp)}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground uppercase mb-1">
                            End
                          </p>
                          <p className="font-mono text-foreground">
                            ${rangeStats.end.close.toFixed(2)}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {formatDate(rangeStats.end.timestamp)}
                          </p>
                        </div>
                      </div>
                    )}
                    {indicatorSnapshot && (
                      <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-xs text-muted-foreground uppercase mb-1">
                            RSI
                          </p>
                          <p className="font-mono text-foreground">
                            {indicatorSnapshot.rsi != null
                              ? indicatorSnapshot.rsi.toFixed(1)
                              : "-"}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground uppercase mb-1">
                            EMA 12
                          </p>
                          <p className="font-mono text-foreground">
                            {indicatorSnapshot.ema12 != null
                              ? `$${indicatorSnapshot.ema12.toFixed(2)}`
                              : "-"}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground uppercase mb-1">
                            EMA 26
                          </p>
                          <p className="font-mono text-foreground">
                            {indicatorSnapshot.ema26 != null
                              ? `$${indicatorSnapshot.ema26.toFixed(2)}`
                              : "-"}
                          </p>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </Card>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <Card className="p-6 animate-slide-up border border-border">
                <h3 className="text-lg font-semibold mb-4 text-foreground">
                  Next Steps
                </h3>
                <ul className="space-y-3 text-sm text-foreground/90">
                  <li className="flex gap-2">
                    <span className="text-ring">•</span>
                    <span>
                      Compare the chart above with your preferred broker to
                      validate pricing.
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-ring">•</span>
                    <span>
                      Use the range selector to inspect 1M–2Y performance before
                      tweaking rules.
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-ring">•</span>
                    <span>
                      Run&nbsp;
                      <code className="font-mono text-xs bg-muted px-2 py-1 rounded">
                        python -m pipe.flows.signal_generation --mode backfill
                        --backfill-range 2y
                      </code>
                      &nbsp; to refresh history.
                    </span>
                  </li>
                </ul>
              </Card>

              <Card className="p-6 animate-slide-up border border-border">
                <h3 className="text-lg font-semibold mb-4 text-foreground">
                  Backtest Preview
                </h3>
                {backtestLoading && (
                  <div className="h-32 flex items-center justify-center text-muted-foreground animate-pulse">
                    Loading summary...
                  </div>
                )}
                {!backtestLoading && (
                  <>
                    <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                      <div>
                        <p className="text-xs text-muted-foreground uppercase mb-1">
                          Win Rate
                        </p>
                        <p className="text-2xl font-semibold text-foreground">
                          {(backtestSummary?.win_rate ?? 0).toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground uppercase mb-1">
                          Trades
                        </p>
                        <p className="text-2xl font-semibold text-foreground">
                          {backtestSummary?.trades ?? 0}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground uppercase mb-1">
                          Avg Return / Trade
                        </p>
                        <p className="text-2xl font-semibold text-foreground">
                          {(backtestSummary?.avg_return ?? 0).toFixed(2)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground uppercase mb-1">
                          Total Return
                        </p>
                        <p className="text-2xl font-semibold text-foreground">
                          {(backtestSummary?.total_return ?? 0).toFixed(2)}%
                        </p>
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {backtestSummary?.notes ??
                        "Detailed backtesting metrics will appear here once the pipeline is ready."}
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">
                      Last trained&nbsp;
                      {formatDate(backtestSummary?.last_trained_at)}
                    </p>
                  </>
                )}
              </Card>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
