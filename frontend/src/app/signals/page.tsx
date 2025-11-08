/**
 * Signals Page (Merged Dashboard + Signals)
 *
 * Unified signals page with:
 * - Card view (default) - Latest signal per symbol, visual layout
 * - Table view (toggle) - Complete history with filtering and sorting
 */

"use client";

import type { JSX } from "react";
import { useMemo, useState } from "react";
import Link from "next/link";
import SignalCard from "@/components/dashboard/SignalCard";
import { useSignals, type Signal } from "@/lib/hooks/useSignals";
import { SubscribeForm } from "@/components/forms/SubscribeForm";
import { DailySignalsBadge } from "@/components/custom/DailySignalsBadge";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

type SignalType = "BUY" | "SELL" | "HOLD" | "ALL";
type SortKey = "timestamp" | "symbol" | "strength";
type SortOrder = "asc" | "desc";
type ViewMode = "cards" | "table";

const PLACEHOLDER_COUNT = 4;

export default function SignalsPage(): JSX.Element {
  const { data: signals = [], isLoading, isError, error } = useSignals();

  // View mode and filters
  const [viewMode, setViewMode] = useState<ViewMode>("cards");
  const [filterType, setFilterType] = useState<SignalType>("ALL");
  const [sortKey, setSortKey] = useState<SortKey>("timestamp");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");

  // For card view: get latest signal per symbol
  const latestSignals = useMemo<Signal[]>(() => {
    const map = new Map<string, Signal>();
    for (const signal of signals) {
      if (!map.has(signal.symbol)) {
        map.set(signal.symbol, signal);
      }
    }
    return Array.from(map.values()).sort(
      (a, b) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
    );
  }, [signals]);

  // For table view: filter and sort all signals
  const filteredAndSortedSignals = useMemo<Signal[]>(() => {
    let filtered = signals;

    // Filter by signal type
    if (filterType !== "ALL") {
      filtered = filtered.filter((s) => s.signal_type === filterType);
    }

    // Sort
    filtered = [...filtered].sort((a, b) => {
      let comparison = 0;

      switch (sortKey) {
        case "timestamp":
          comparison =
            new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
          break;
        case "symbol":
          comparison = a.symbol.localeCompare(b.symbol);
          break;
        case "strength":
          comparison = a.strength - b.strength;
          break;
      }

      return sortOrder === "asc" ? comparison : -comparison;
    });

    return filtered;
  }, [signals, filterType, sortKey, sortOrder]);

  // Apply filter to card view as well
  const filteredLatestSignals = useMemo<Signal[]>(() => {
    if (filterType === "ALL") return latestSignals;
    return latestSignals.filter((s) => s.signal_type === filterType);
  }, [latestSignals, filterType]);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortOrder("desc");
    }
  };

  const getSignalBadgeClasses = (signalType: string) => {
    switch (signalType) {
      case "BUY":
        return "bg-primary text-white border-0";
      case "SELL":
        return "bg-red-600 text-white border-0";
      default:
        return "bg-muted text-muted-foreground border-0";
    }
  };

  const getStrengthColor = (strength: number) => {
    if (strength >= 70) return "bg-primary";
    if (strength >= 40) return "bg-yellow-500";
    return "bg-red-500";
  };

  const placeholders = Array.from({
    length: Math.max(filteredLatestSignals.length || 0, PLACEHOLDER_COUNT),
  });

  const displayCount =
    viewMode === "cards"
      ? filteredLatestSignals.length
      : filteredAndSortedSignals.length;

  return (
    <main className="min-h-screen py-10 px-4">
      <div className="container-app">
        {/* View Toggle and Filters */}
        <div className="mb-6 flex flex-col md:flex-row gap-4 items-start md:items-center justify-between animate-slide-up">
          {/* View Mode Toggle */}
          <div className="flex gap-2 order-1 md:order-2">
            <Button
              size="sm"
              onClick={() => setViewMode("cards")}
              className={`px-4 py-4 cursor-pointer font-semibold focus-visible:ring-0 transition-colors border ${
                viewMode === "cards"
                  ? "bg-primary border-primary text-white"
                  : "bg-card border-border text-muted-foreground hover:border-primary/50 hover:text-foreground hover:bg-card"
              }`}
            >
              Cards
            </Button>
            <Button
              size="sm"
              onClick={() => setViewMode("table")}
              className={`px-4 py-4 cursor-pointer font-semibold focus-visible:ring-0 transition-colors border ${
                viewMode === "table"
                  ? "bg-primary border-primary text-white"
                  : "bg-card border-border text-muted-foreground hover:border-primary/50 hover:text-foreground hover:bg-card"
              }`}
            >
              Table
            </Button>
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-2 items-center order-2 md:order-1">
            <Badge
              onClick={() => setFilterType("ALL")}
              className={`px-4 py-2 cursor-pointer transition-colors font-semibold ${
                filterType === "ALL"
                  ? "bg-primary border-primary text-white"
                  : "bg-card border-border text-muted-foreground hover:border-primary/50 hover:text-foreground hover:bg-card"
              }`}
            >
              All
            </Badge>
            <Badge
              onClick={() => setFilterType("BUY")}
              className={`px-4 py-2 cursor-pointer transition-colors font-semibold ${
                filterType === "BUY"
                  ? "bg-primary border-primary text-white"
                  : "bg-card border-border text-muted-foreground hover:border-primary/50 hover:text-foreground hover:bg-card"
              }`}
            >
              Buy
            </Badge>
            <Badge
              onClick={() => setFilterType("SELL")}
              className={`px-4 py-2 cursor-pointer transition-colors font-semibold ${
                filterType === "SELL"
                  ? "bg-primary border-primary text-white"
                  : "bg-card border-border text-muted-foreground hover:border-primary/50 hover:text-foreground hover:bg-card"
              }`}
            >
              Sell
            </Badge>
            <Badge
              onClick={() => setFilterType("HOLD")}
              className={`px-4 py-2 cursor-pointer transition-colors font-semibold ${
                filterType === "HOLD"
                  ? "bg-primary border-primary text-white"
                  : "bg-card border-border text-muted-foreground hover:border-primary/50 hover:text-foreground hover:bg-card"
              }`}
            >
              Hold
            </Badge>
            <span className="text-sm text-muted-foreground ml-2">
              {displayCount} signal{displayCount !== 1 ? "s" : ""}
            </span>
          </div>
        </div>

        {/* Error State */}
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

        {/* Loading State */}
        {isLoading && viewMode === "cards" && (
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

        {isLoading && viewMode === "table" && (
          <div className="card p-8 text-center animate-pulse">
            <p className="text-muted">Loading signals...</p>
          </div>
        )}

        {/* Cards View */}
        {!isLoading && !isError && viewMode === "cards" && (
          <>
            {filteredLatestSignals.length > 0 ? (
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {filteredLatestSignals.map((signal, idx) => (
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
            ) : (
              <div className="card-premium p-6 text-center animate-fade-in">
                <p className="text-lg font-semibold mb-2">
                  {filterType !== "ALL"
                    ? `No ${filterType} signals found`
                    : "No signals yet for your symbols"}
                </p>
                <p className="text-sm text-foreground-muted">
                  {filterType !== "ALL"
                    ? "Try changing the filter to see more signals"
                    : "Run the Prefect flow to populate the database, then refresh."}
                </p>
              </div>
            )}
          </>
        )}

        {/* Table View */}
        {!isLoading && !isError && viewMode === "table" && (
          <>
            {filteredAndSortedSignals.length > 0 ? (
              <Card className="overflow-hidden animate-slide-up border border-border">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border">
                        <th
                          className="text-left px-6 py-4 text-sm font-semibold text-foreground cursor-pointer hover:text-ring transition-colors"
                          onClick={() => handleSort("symbol")}
                        >
                          <div className="flex items-center gap-2">
                            Symbol
                            {sortKey === "symbol" && (
                              <span className="text-xs">
                                {sortOrder === "asc" ? "↑" : "↓"}
                              </span>
                            )}
                          </div>
                        </th>
                        <th className="text-left px-6 py-4 text-sm font-semibold text-foreground">
                          Signal
                        </th>
                        <th
                          className="text-left px-6 py-4 text-sm font-semibold text-foreground cursor-pointer hover:text-ring transition-colors"
                          onClick={() => handleSort("strength")}
                        >
                          <div className="flex items-center gap-2">
                            Strength
                            {sortKey === "strength" && (
                              <span className="text-xs">
                                {sortOrder === "asc" ? "↑" : "↓"}
                              </span>
                            )}
                          </div>
                        </th>
                        <th className="text-left px-6 py-4 text-sm font-semibold text-foreground">
                          Price
                        </th>
                        <th
                          className="text-left px-6 py-4 text-sm font-semibold text-foreground cursor-pointer hover:text-ring transition-colors"
                          onClick={() => handleSort("timestamp")}
                        >
                          <div className="flex items-center gap-2">
                            Time
                            {sortKey === "timestamp" && (
                              <span className="text-xs">
                                {sortOrder === "asc" ? "↑" : "↓"}
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
                      {filteredAndSortedSignals.map((signal, idx) => (
                        <tr
                          key={signal.id}
                          className="border-b border-border hover:bg-muted/30 transition-colors text-nowrap"
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
                            <Badge
                              className={getSignalBadgeClasses(
                                signal.signal_type,
                              )}
                            >
                              {signal.signal_type}
                            </Badge>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-3">
                              <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
                                <div
                                  className={`h-full transition-all ${getStrengthColor(
                                    signal.strength,
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
                            ${signal.price_at_signal?.toFixed(2) || "-"}
                          </td>
                          <td className="px-6 py-4 text-sm text-muted-foreground">
                            {new Date(signal.timestamp).toLocaleString(
                              "en-US",
                              {
                                month: "short",
                                day: "numeric",
                                hour: "2-digit",
                                minute: "2-digit",
                              },
                            )}
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
            ) : (
              <div className="card p-12 text-center animate-slide-up">
                <p className="text-foreground text-lg mb-2">No signals found</p>
                <p className="text-sm text-foreground-muted">
                  {filterType !== "ALL"
                    ? "Try changing the filter to see more signals"
                    : "Signals will appear here once the pipeline generates them"}
                </p>
              </div>
            )}
          </>
        )}

        {/* Daily Signals Badge (only in cards view with data) */}
        {!isLoading &&
          !isError &&
          viewMode === "cards" &&
          filteredLatestSignals.length > 0 && <DailySignalsBadge />}
      </div>

      {/* Subscribe Form */}
      <div id="subscribe" className="my-8 animate-fade-in">
        <SubscribeForm
          helperText="We only send alerts when a conviction-level setup fires."
          successTitle="Subscribed! Watch your inbox for the next alert."
        />
      </div>
    </main>
  );
}
