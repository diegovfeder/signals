import type { Point } from 'chart.js';

/**
 * Time-series data point with string timestamps.
 *
 * Chart.js's built-in Point type only accepts x: number, but the time scale
 * adapter (chartjs-adapter-date-fns) accepts string timestamps at runtime.
 * This interface bridges that gap for TypeScript type safety.
 */
export interface TimeSeriesPoint {
  x: string | number;
  y: number;
}

/**
 * Signal marker point with additional metadata for buy/sell/hold signals.
 * Used for scatter plot overlays on price charts.
 */
export interface SignalMarkerPoint extends TimeSeriesPoint {
  signalType: 'BUY' | 'SELL' | 'HOLD';
  price: number;
}
