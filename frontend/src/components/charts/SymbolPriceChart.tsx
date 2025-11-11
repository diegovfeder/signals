"use client";

import {
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
  type JSX,
} from "react";
import type { IndicatorPoint, Signal } from "@/lib/hooks/useSignals";
import type { ChartData, ChartOptions, ScriptableContext, TooltipItem } from "chart.js";
import type { TimeSeriesPoint, SignalMarkerPoint } from "@/types/chart-types";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  TimeScale,
  Tooltip,
  Filler,
  Legend,
  ScatterController,
} from "chart.js";
import "chartjs-adapter-date-fns";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  TimeScale,
  Tooltip,
  Filler,
  Legend,
  ScatterController,
);

let zoomPluginRegistered = false;

type ChartTimeUnit = "day" | "week" | "month" | "quarter" | "year";

const RANGE_TO_UNIT: Record<string, ChartTimeUnit> = {
  "1d": "day",
  "1w": "day",
  "1m": "day",
  "3m": "week",
  "6m": "week",
  "1y": "month",
  "2y": "month",
  "5y": "quarter",
  "10y": "year",
};

const SIGNAL_COLORS: Record<Signal["signal_type"], string> = {
  BUY: "#10b981",
  SELL: "#ef4444",
  HOLD: "#64748b",
};

/**
 * Format numbers with abbreviated suffixes (k, M, B)
 * Examples: 140000 → 140k, 1400000 → 1.4M, 0.14 → 0.14
 */
function formatAbbreviatedNumber(value: number): string {
  const absValue = Math.abs(value);

  if (absValue >= 1_000_000_000) {
    const formatted = value / 1_000_000_000;
    return `${formatted % 1 === 0 ? formatted.toFixed(0) : formatted.toFixed(1)}B`;
  }
  if (absValue >= 1_000_000) {
    const formatted = value / 1_000_000;
    return `${formatted % 1 === 0 ? formatted.toFixed(0) : formatted.toFixed(1)}M`;
  }
  if (absValue >= 1_000) {
    const formatted = value / 1_000;
    return `${formatted % 1 === 0 ? formatted.toFixed(0) : formatted.toFixed(1)}k`;
  }

  // For small numbers, show appropriate decimal places
  if (absValue >= 1) {
    // Remove .00 for whole numbers (280.00 -> 280)
    return value % 1 === 0 ? value.toFixed(0) : value.toFixed(2);
  }

  return value.toFixed(4);
}

interface SymbolPriceChartProps {
  symbol: string;
  data: { timestamp: string; close: number }[];
  range: string;
  indicators?: IndicatorPoint[];
  signals?: Signal[];
}

export interface SymbolPriceChartHandle {
  resetZoom: () => void;
}

const SymbolPriceChart = forwardRef<SymbolPriceChartHandle, SymbolPriceChartProps>(
  function SymbolPriceChart(
    {
      symbol,
      data,
      range,
      indicators = [],
      signals = [],
    }: SymbolPriceChartProps,
    ref,
  ): JSX.Element {
    const chartRef = useRef<ChartJS<"line" | "scatter"> | null>(null);
    const [zoomReady, setZoomReady] = useState(zoomPluginRegistered);
    const handleResetZoom = useCallback(() => {
      chartRef.current?.resetZoom();
    }, []);

    useEffect(() => {
      if (zoomPluginRegistered) {
        setZoomReady(true);
        return;
      }
      if (typeof window === "undefined") {
        return;
      }

      let active = true;

      import("chartjs-plugin-zoom").then((module) => {
        if (!active) {
          return;
        }
        const plugin = (module as any)?.default ?? module;
        ChartJS.register(plugin);
        zoomPluginRegistered = true;
        setZoomReady(true);
      });

      return () => {
        active = false;
      };
    }, []);

  const ema12Data = indicators.reduce<{ x: string; y: number }[]>((acc, point) => {
    if (point.ema12 != null) {
      acc.push({ x: point.timestamp, y: point.ema12 });
    }
    return acc;
  }, []);

  const ema26Data = indicators.reduce<{ x: string; y: number }[]>((acc, point) => {
    if (point.ema26 != null) {
      acc.push({ x: point.timestamp, y: point.ema26 });
    }
    return acc;
  }, []);

  const rsiData = indicators.reduce<{ x: string; y: number }[]>((acc, point) => {
    if (point.rsi != null) {
      acc.push({ x: point.timestamp, y: point.rsi });
    }
    return acc;
  }, []);

  const priceSeries = data
    .map((point) => ({
      x: point.timestamp,
      y: point.close,
    }))
    .sort(
      (a, b) => new Date(a.x).getTime() - new Date(b.x).getTime(),
    );

  const signalMarkers = signals
    .map((signal) => {
      const explicitPrice =
        signal.price_at_signal != null
          ? Number(signal.price_at_signal)
          : null;

      if (explicitPrice != null) {
        return {
          x: signal.timestamp,
          y: explicitPrice,
          signalType: signal.signal_type,
          price: explicitPrice,
        } as SignalMarkerPoint;
      }

      const targetTime = new Date(signal.timestamp).getTime();
      if (Number.isNaN(targetTime) || !priceSeries.length) {
        return null;
      }

      let nearest = priceSeries[0];
      let smallestDelta = Math.abs(
        new Date(nearest.x).getTime() - targetTime,
      );

      for (let index = 1; index < priceSeries.length; index += 1) {
        const candidate = priceSeries[index];
        const delta = Math.abs(new Date(candidate.x).getTime() - targetTime);
        if (delta < smallestDelta) {
          nearest = candidate;
          smallestDelta = delta;
        } else if (delta > smallestDelta) {
          break;
        }
      }

      return {
        x: signal.timestamp,
        y: nearest.y,
        signalType: signal.signal_type,
        price: nearest.y,
      } as SignalMarkerPoint;
    })
    .filter((point): point is SignalMarkerPoint => point != null)
    .sort(
      (a, b) => new Date(a.x).getTime() - new Date(b.x).getTime(),
    );

  const earliestTimestampMs = priceSeries.length
    ? new Date(priceSeries[0].x).getTime()
    : undefined;
  const latestTimestampMs = priceSeries.length
    ? new Date(priceSeries[priceSeries.length - 1].x).getTime()
    : undefined;
  const dataWindowKey =
    priceSeries.length > 0 ? `${priceSeries[0].x}-${priceSeries[priceSeries.length - 1].x}` : "empty";

  /**
   * TODO: Remove `any[]` type - Chart.js doesn't properly type mixed chart datasets.
   * We have both 'line' and 'scatter' datasets in the same chart, but TypeScript
   * cannot infer the correct union type for the datasets array when using
   * conditional spread operators. The runtime data structure is correct.
   */
  const datasets: any[] = [
    {
      label: `${symbol} close`,
      data: priceSeries,
      borderColor: "rgba(241, 245, 249, 0.9)",
      backgroundColor: "transparent",
      borderWidth: 1.75,
      tension: 0.25,
      pointRadius: 0,
      fill: false,
      yAxisID: "y",
      spanGaps: true,
    },
    ...(ema12Data.length
      ? [
          {
            label: "EMA 12",
            data: ema12Data,
            borderColor: "rgba(96, 165, 250, 0.9)",
            borderWidth: 1.25,
            pointRadius: 0,
            tension: 0.2,
            fill: false,
            yAxisID: "y",
            spanGaps: true,
          },
        ]
      : []),
    ...(ema26Data.length
      ? [
          {
            label: "EMA 26",
            data: ema26Data,
            borderColor: "rgba(129, 140, 248, 0.85)",
            borderWidth: 1.25,
            pointRadius: 0,
            tension: 0.2,
            fill: false,
            yAxisID: "y",
            spanGaps: true,
          },
        ]
      : []),
    ...(rsiData.length
      ? [
          {
            label: "RSI",
            data: rsiData,
            borderColor: "rgba(250, 204, 21, 0.8)",
            borderWidth: 1,
            pointRadius: 0,
            tension: 0.2,
            fill: false,
            yAxisID: "y1",
            spanGaps: true,
          },
        ]
      : []),
    ...(signalMarkers.length
      ? [
          {
            label: "Signals",
            type: "scatter" as const,
            order: 5,
            data: signalMarkers,
            yAxisID: "y",
            showLine: false,
            pointRadius: 5,
            pointHoverRadius: 6,
            pointHitRadius: 20,
            pointBorderWidth: 0,
            pointStyle: (context: ScriptableContext<"line">) => {
              const raw = context.raw as SignalMarkerPoint | undefined;
              if (!raw) return "circle";
              if (raw.signalType === "BUY") return "triangle";
              if (raw.signalType === "SELL") return "triangle";
              return "rectRounded";
            },
            pointRotation: (context: ScriptableContext<"line">) => {
              const raw = context.raw as SignalMarkerPoint | undefined;
              if (!raw) return 0;
              return raw.signalType === "SELL" ? 180 : 0;
            },
            backgroundColor: (context: ScriptableContext<"line">) => {
              const raw = context.raw as SignalMarkerPoint | undefined;
              return raw ? SIGNAL_COLORS[raw.signalType] : SIGNAL_COLORS.HOLD;
            },
            borderColor: (context: ScriptableContext<"line">) => {
              const raw = context.raw as SignalMarkerPoint | undefined;
              return raw ? SIGNAL_COLORS[raw.signalType] : SIGNAL_COLORS.HOLD;
            },
          },
        ]
      : []),
  ];

  const chartData: ChartData<'line' | 'scatter', (TimeSeriesPoint | SignalMarkerPoint)[]> = {
    datasets,
  };

  const unit = RANGE_TO_UNIT[range] ?? "day";

  const scales: ChartOptions<"line" | "scatter">["scales"] = {
    x: {
      type: "time",
      time: {
        unit,
        tooltipFormat: "MMM d, yyyy",
      },
      ticks: {
        color: "#94a3b8",
        maxRotation: 0,
      },
      grid: {
        color: "rgba(148, 163, 184, 0.08)",
      },
    },
    y: {
      beginAtZero: false,
      ticks: {
        color: "#cbd5f5",
        callback: (value: string | number) => `$${formatAbbreviatedNumber(Number(value))}`,
      },
      grid: {
        color: "rgba(148, 163, 184, 0.08)",
      },
    },
  };

  if (rsiData.length) {
    scales.y1 = {
      position: "right",
      beginAtZero: true,
      min: 0,
      max: 100,
      ticks: {
        color: "#facc15",
        callback: (value: string | number) => `${Number(value).toFixed(0)}`,
      },
      grid: {
        display: false,
      },
      title: {
        display: true,
        text: "RSI",
        color: "#facc15",
      },
    };
  }

  useEffect(() => {
    if (!zoomReady) {
      return;
    }
    chartRef.current?.resetZoom();
  }, [range, dataWindowKey, zoomReady]);

  const options: ChartOptions<"line" | "scatter"> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: datasets.length > 1,
        position: "top",
        labels: {
          color: "#94a3b8",
          usePointStyle: true,
          padding: 18,
        },
      },
      tooltip: {
        displayColors: false,
        position: "nearest",
        yAlign: "bottom",
        caretPadding: 8,
        backgroundColor: "rgba(15, 23, 42, 0.85)",
        borderColor: "rgba(148, 163, 184, 0.35)",
        borderWidth: 1,
        padding: 8,
        bodyFont: { size: 11 },
        titleFont: { size: 12, weight: 600 },
        titleColor: "#cbd5e1",
        bodyColor: "#e2e8f0",

        callbacks: {
          label: (context: TooltipItem<"line" | "scatter">) => {
            const label = context.dataset.label ?? "";

            // Chart.js mixed datasets require `as any` for dataset/type,
            // options, data, and the component ref because react-chartjs-2's
            // type definitions assume homogeneous data.
            if ((context.dataset as any).type === "scatter") {
              const raw = context.raw as SignalMarkerPoint | undefined;
              if (!raw) {
                return label;
              }
              return `${raw.signalType} @ $${raw.price.toFixed(2)}`;
            }

            if (context.dataset.yAxisID === "y1") {
              return `${label}: ${Number(context.parsed.y).toFixed(1)}`;
            }

            return `${label}: $${Number(context.parsed.y).toFixed(2)}`;
          },
        },
      },
      zoom: {
        limits: {
          x: {
            min: earliestTimestampMs,
            max: latestTimestampMs,
            minRange: 1000 * 60 * 60 * 24,
          },
          y: { minRange: 0.5 },
        },
        pan: {
          enabled: true,
          mode: "x",
          threshold: 8,
        },
        zoom: {
          wheel: { enabled: true },
          pinch: { enabled: true },
          drag: {
            enabled: true,
            modifierKey: "shift",
            backgroundColor: "rgba(15, 118, 110, 0.2)",
            borderColor: "rgba(16, 185, 129, 0.9)",
            borderWidth: 1,
          },
          mode: "x",
        },
      },
    },
    interaction: {
      intersect: false,
      mode: "nearest",
      axis: "x",
    },
    scales,
  };

  useImperativeHandle(
    ref,
    () => ({
      resetZoom: () => chartRef.current?.resetZoom(),
    }),
    [],
  );

  if (!zoomReady) {
    return (
      <div className="h-72 md:h-96 rounded-2xl bg-slate-950/50 animate-pulse" />
    );
  }

  return (
    <div className="h-72 md:h-96">
      {/*
        Type assertions required: react-chartjs-2's Line component expects
        ChartData<"line">, ChartOptions<"line">, and ref type for "line" only,
        but we have mixed chart types (ChartData<"line" | "scatter">).
        This is a limitation of the wrapper library's type definitions.
        The Chart.js library itself handles mixed types correctly at runtime.
      */}
      <Line
        ref={chartRef as any}
        options={options as any}
        data={chartData as any}
      />
    </div>
  );
});

SymbolPriceChart.displayName = "SymbolPriceChart";

export default SymbolPriceChart;
