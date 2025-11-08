/**
 * Application Constants
 *
 * Symbol configs, API endpoints, and other constants.
 */

// Tracked symbols (MVP: 3 only)
export const SYMBOLS = [
  {
    symbol: "BTC-USD",
    name: "Bitcoin",
    type: "crypto" as const,
  },
  {
    symbol: "ETH-USD",
    name: "Ethereum",
    type: "crypto" as const,
  },
  {
    symbol: "TSLA",
    name: "Tesla Inc.",
    type: "stock" as const,
  },
] as const;

// Signal types
export const SIGNAL_TYPES = {
  BUY: "BUY",
  SELL: "SELL",
  HOLD: "HOLD",
} as const;

// Signal strength thresholds
export const STRENGTH_THRESHOLDS = {
  STRONG: 70,
  MODERATE: 40,
  WEAK: 0,
} as const;

// Default symbols
export const DEFAULT_SYMBOLS = ["AAPL", "BTC-USD"];

// API endpoints
export const API_ENDPOINTS = {
  SIGNALS: "/api/signals",
  SIGNAL_BY_SYMBOL: (symbol: string) => `/api/signals/${symbol}`,
  MARKET_DATA: (symbol: string) => `/api/market-data/${symbol}/ohlcv`,
  INDICATORS: (symbol: string) => `/api/market-data/${symbol}/indicators`,
  SUBSCRIBE: "/api/subscribe",
} as const;

// Chart colors
export const CHART_COLORS = {
  BUY: "#10b981",
  SELL: "#ef4444",
  NEUTRAL: "#64748b",
  CANDLESTICK_UP: "#10b981",
  CANDLESTICK_DOWN: "#ef4444",
} as const;

// Hero section
export const HERO = {
  TITLE: "Automated trading signals that speak plain English",
  DESCRIPTION:
    "Email alerts and a simple dashboard for opportunities across crypto, stocks, ETFs, and forex.",
};

export const RANGE_OPTIONS = [
  { label: "1M", value: "1m" },
  { label: "3M", value: "3m" },
  { label: "6M", value: "6m" },
  { label: "1Y", value: "1y" },
  { label: "2Y", value: "2y" },
  { label: "5Y", value: "5y" },
  { label: "10Y", value: "10y" },
] as const;

export type RangeValue = (typeof RANGE_OPTIONS)[number]["value"];
