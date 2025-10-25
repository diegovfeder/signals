/**
 * useMarketData Hook
 *
 * Fetch market data (OHLCV) and indicators for charts.
 */

'use client';

import { useState, useEffect } from 'react';

interface MarketData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export function useMarketData(symbol: string, limit: number = 100) {
  const [data, setData] = useState<MarketData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // TODO: Implement data fetching
    // Fetch from /api/market-data/{symbol}/ohlcv?limit={limit}

    setLoading(false);
  }, [symbol, limit]);

  return { data, loading, error };
}

export function useIndicators(symbol: string, limit: number = 100) {
  const [indicators, setIndicators] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // TODO: Implement data fetching
    // Fetch from /api/market-data/{symbol}/indicators?limit={limit}

    setLoading(false);
  }, [symbol, limit]);

  return { indicators, loading, error };
}
