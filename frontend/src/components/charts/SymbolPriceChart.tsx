"use client";

import type { JSX } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  TimeScale,
  Tooltip,
  Filler,
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
  Filler
);

const RANGE_TO_UNIT: Record<string, "day" | "week" | "month"> = {
  "1d": "day",
  "1w": "day",
  "1m": "week",
  "3m": "week",
  "6m": "month",
  "1y": "month",
  "2y": "month",
};

interface SymbolPriceChartProps {
  symbol: string;
  data: { timestamp: string; close: number }[];
  range: string;
}

export default function SymbolPriceChart({
  symbol,
  data,
  range,
}: SymbolPriceChartProps): JSX.Element {
  const chartData = {
    datasets: [
      {
        label: `${symbol} close`,
        data: data.map((point) => ({
          x: point.timestamp,
          y: point.close,
        })),
        borderColor: "rgba(16, 185, 129, 0.9)",
        backgroundColor: "rgba(16, 185, 129, 0.15)",
        tension: 0.25,
        pointRadius: 0,
        fill: true,
      },
    ],
  };

  const unit = RANGE_TO_UNIT[range] ?? "day";

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const price = context.parsed.y;
            return `Close: $${Number(price).toFixed(2)}`;
          },
        },
      },
    },
    interaction: {
      intersect: false,
      mode: "index" as const,
    },
    scales: {
      x: {
        type: "time" as const,
        time: {
          unit,
          tooltipFormat: "MMM d, yyyy",
        },
        ticks: {
          color: "#9ca3af",
        },
        grid: {
          color: "rgba(255,255,255,0.04)",
        },
      },
      y: {
        beginAtZero: false,
        ticks: {
          color: "#9ca3af",
          callback: (value: string | number) => `$${Number(value).toFixed(2)}`,
        },
        grid: {
          color: "rgba(255,255,255,0.04)",
        },
      },
    },
  };

  return (
    <div className="h-64 md:h-80">
      <Line options={options} data={chartData} />
    </div>
  );
}
