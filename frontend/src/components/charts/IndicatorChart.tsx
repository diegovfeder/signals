/**
 * IndicatorChart Component
 *
 * Chart for displaying RSI or MACD indicators separately.
 */

'use client';

interface IndicatorChartProps {
  type: 'RSI' | 'MACD';
  data: any[];
}

export default function IndicatorChart({ type, data }: IndicatorChartProps) {
  // TODO: Implement indicator chart
  // - RSI: Line chart with 30/70 threshold lines
  // - MACD: Line chart with histogram bars

  return null;
}
