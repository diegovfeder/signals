/**
 * PriceChart Component
 *
 * Candlestick price chart with technical indicators overlay.
 * Uses Chart.js for rendering.
 */

'use client';

interface PriceChartProps {
  symbol: string;
  data: any[]; // OHLCV data
}

export default function PriceChart({ symbol, data }: PriceChartProps) {
  // TODO: Implement candlestick chart with Chart.js
  // - Candlestick chart type
  // - Time axis
  // - Price axis
  // - Volume bars below
  // - Optional: overlay RSI/MACD

  return null;
}
