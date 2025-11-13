"use client";

import { useMemo } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  TimeScale,
  Tooltip,
  Filler,
  type ChartOptions,
  type ChartData,
  type TooltipItem,
} from "chart.js";
import "chartjs-adapter-date-fns";
import { Line } from "react-chartjs-2";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AnimatedPriceTicker } from "@/components/ui/animated-price-ticker";
import { cn } from "@/lib/utils";
import { formatPercentage, formatPrice } from "@/lib/utils/formatters";
import { SignalPreviewEmailContent } from "@/components/custom/SignalPreview";
import Link from "next/link";
import { MarketAnalysisExample } from "../custom/MarketAnalysisExample";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  TimeScale,
  Tooltip,
  Filler,
);

type BtcPoint = {
  date: string;
  close: number;
};

const btcTwoYearSeries: BtcPoint[] = [
  { date: "2023-02-01", close: 23482 },
  { date: "2023-04-01", close: 28650 },
  { date: "2023-06-01", close: 30510 },
  { date: "2023-08-01", close: 29180 },
  { date: "2023-10-01", close: 34015 },
  { date: "2023-12-01", close: 42150 },
  { date: "2024-02-01", close: 45120 },
  { date: "2024-04-01", close: 59380 },
  { date: "2024-06-01", close: 64350 },
  { date: "2024-08-01", close: 58710 },
  { date: "2024-10-01", close: 63985 },
  { date: "2024-12-01", close: 48230 },
];

const previewSignal = {
  symbol: "BTC-USD",
  signalType: "HOLD" as "BUY" | "SELL" | "HOLD",
  price: 48230.12,
  strength: 82,
  updatedAt: new Date("2025-02-12T12:15:00Z"),
  reasoning: [
    "RSI reclaimed 55 after cooling off from overbought levels.",
    "12/26 EMA crossover stays intact with widening spread.",
  ],
};

const strengthLabel =
  previewSignal.strength >= 70
    ? "Strong"
    : previewSignal.strength >= 40
      ? "Moderate"
      : "Developing";

const strengthBarClass =
  previewSignal.strength >= 70
    ? "bg-primary"
    : previewSignal.strength >= 40
      ? "bg-yellow-500"
      : "bg-red-500";

const formatUpdated = (date: Date) =>
  new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short",
  }).format(date);

const hexToRgba = (hex: string, alpha: number) => {
  const normalized = hex.replace("#", "").trim();
  if (normalized.length !== 6) {
    return hex;
  }

  const r = parseInt(normalized.slice(0, 2), 16);
  const g = parseInt(normalized.slice(2, 4), 16);
  const b = parseInt(normalized.slice(4, 6), 16);

  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

export default function SignalsPreview() {
  const { chartColor, gridColor, tickColor, tooltipBackground } =
    useMemo(() => {
      if (typeof window === "undefined") {
        return {
          chartColor: "#4ade80",
          gridColor: "rgba(41, 41, 41, 0.4)",
          tickColor: "#a2a2a2",
          tooltipBackground: "rgba(23, 23, 23, 0.92)",
        };
      }
      const rootStyles = getComputedStyle(document.documentElement);
      const chart = rootStyles.getPropertyValue("--chart-1").trim();
      const border = rootStyles.getPropertyValue("--border").trim();
      const card = rootStyles.getPropertyValue("--card").trim();
      const muted = rootStyles.getPropertyValue("--muted-foreground").trim();

      return {
        chartColor: chart || "#4ade80",
        gridColor: border ? hexToRgba(border, 0.35) : "rgba(41, 41, 41, 0.4)",
        tickColor: muted || "#a2a2a2",
        tooltipBackground: card
          ? hexToRgba(card, 0.92)
          : "rgba(23, 23, 23, 0.92)",
      };
    }, []);

  const gain = useMemo(() => {
    if (!btcTwoYearSeries.length) {
      return 0;
    }
    const start = btcTwoYearSeries[0].close;
    const end = btcTwoYearSeries[btcTwoYearSeries.length - 1].close;
    return ((end - start) / start) * 100;
  }, []);

  const chartData = useMemo<ChartData<"line">>(() => {
    return {
      labels: btcTwoYearSeries.map((point) => point.date),
      datasets: [
        {
          label: "BTC-USD",
          data: btcTwoYearSeries.map((point) => point.close),
          fill: {
            target: "origin",
            above: hexToRgba(chartColor, 0.12),
          },
          borderColor: chartColor,
          tension: 0.35,
          pointRadius: 0,
          borderWidth: 3,
        },
      ],
    };
  }, [chartColor]);

  const chartOptions = useMemo<ChartOptions<"line">>(() => {
    return {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index" as const,
        intersect: false,
      },
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          callbacks: {
            label(context: TooltipItem<"line">) {
              if (context.parsed?.y == null) {
                return "";
              }
              return formatPrice(context.parsed.y);
            },
          },
          backgroundColor: tooltipBackground,
          borderColor: gridColor,
          borderWidth: 1,
          titleColor: "#e2e8f0",
          bodyColor: "#f1f5f9",
          padding: 12,
        },
      },
      scales: {
        x: {
          type: "time" as const,
          ticks: {
            color: tickColor,
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 5,
          },
          grid: {
            display: false,
          },
        },
        y: {
          type: "linear" as const,
          ticks: {
            color: tickColor,
            padding: 10,
            callback(tickValue: number | string) {
              if (typeof tickValue === "number") {
                return formatPrice(tickValue);
              }
              return tickValue;
            },
          },
          grid: {
            color: gridColor,
            drawBorder: false,
          },
        },
      },
    };
  }, [gridColor, tickColor, tooltipBackground]);

  return (
    <section
      aria-labelledby="signals-preview-heading"
      className="relative isolate mx-auto max-w-6xl px-2 md:px-4"
    >
      <div className="rounded-4xl border border-border/60 bg-card/40 p-3 md:p-6 shadow-2xl backdrop-blur">
        <div className="grid gap-4 md:gap-6 sm:grid-cols-2 lg:auto-rows-fr md:grid-cols-5">
          <Card
            role="group"
            aria-labelledby="signals-preview-card-heading"
            className="flex flex-col border border-border/60 bg-card/80 p-4 md:p-6 sm:col-span-1 md:col-span-2 justify-center"
          >
            <div className="flex flex-col gap-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    Latest signal
                  </p>
                  <h3
                    id="signals-preview-card-heading"
                    className="mt-2 text-xl font-semibold text-foreground"
                  >
                    {previewSignal.symbol}
                  </h3>
                </div>
                <Badge
                  className={cn(
                    "border-0 px-3 py-1 text-xs font-semibold uppercase tracking-wide",
                    previewSignal.signalType === "BUY"
                      ? "bg-primary text-primary-foreground"
                      : previewSignal.signalType === "SELL"
                        ? "bg-destructive text-destructive-foreground"
                        : "bg-muted text-muted-foreground",
                  )}
                >
                  {previewSignal.signalType}
                </Badge>
              </div>

              <div>
                <p className="mt-2 text-xs text-muted-foreground">
                  Updated {formatUpdated(previewSignal.updatedAt)}
                </p>
              </div>

              <div>
                <div className="flex items-center justify-between text-xs uppercase tracking-wide text-muted-foreground">
                  <span>Strength</span>
                  <span>{strengthLabel}</span>
                </div>
                <div className="mt-2 h-2 rounded-full bg-muted">
                  <div
                    className={cn(
                      "h-full rounded-full transition-all",
                      strengthBarClass,
                    )}
                    style={{
                      width: `${previewSignal.strength}%`,
                    }}
                  />
                </div>
                <p className="mt-2 font-mono text-sm text-foreground">
                  {previewSignal.strength}%
                </p>
              </div>

              <ul className="space-y-2 text-sm text-muted-foreground/90">
                {previewSignal.reasoning.slice(0, 2).map((item, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="mt-0.5 text-ring">•</span>
                    <span className="leading-6">{item}</span>
                  </li>
                ))}
              </ul>
              <Button
                variant="link"
                className="mt-6 px-0 text-sm font-semibold text-primary hover:text-primary/90"
                asChild
              >
                <Link
                  href="/signals"
                  aria-label="Explore how trading signals are generated"
                  className="px-3 my-2"
                >
                  <span className="text-wrap text-lg text-foreground py-4">
                    Inspect our signals to see how they are being generated.
                  </span>
                </Link>
              </Button>
              <div className="mt-4">
                <AnimatedPriceTicker
                  startPrice={45000}
                  endPrice={previewSignal.price}
                  duration={2000}
                  symbol={previewSignal.symbol}
                />
              </div>
            </div>
          </Card>

          <Card
            role="group"
            aria-labelledby="signals-preview-email-heading"
            className="hidden sm:flex h-full flex-col border border-border/60 bg-card/80 p-4 sm:p-6 sm:col-span-1 md:col-span-3 sm:justify-center"
          >
            <div className="mb-5">
              <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Email alert
              </p>
              <h3
                id="signals-preview-email-heading"
                className="mt-2 text-xl font-semibold text-foreground"
              >
                Inbound preview
              </h3>
              <p className="mt-2 text-xs text-muted-foreground">
                Sent {formatUpdated(previewSignal.updatedAt)}
              </p>
            </div>

            {/*FIXME: Might remove component below and use the Example*/}
            <div className="flex-1">
              <MarketAnalysisExample />
            </div>
            {/*<SignalPreviewEmailContent className="border-0 bg-muted/30" />*/}
          </Card>

          <div
            role="group"
            aria-labelledby="signals-preview-chart-heading"
            className="flex h-fit flex-col border border-border/60 bg-card/80 p-4 md:p-6 sm:col-span-2 md:col-span-5"
          >
            {/* Market Context Explanation - Hidden on lg+ breakpoint */}
            {/*<MarketAnalysisExample />*/}

            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  2-year snapshot
                </p>
                <h3
                  id="signals-preview-chart-heading"
                  className="mt-2 text-xl font-semibold text-foreground"
                >
                  BTC-USD performance
                </h3>
              </div>
              <Badge
                variant="metal"
                className="px-3 py-1 text-xs uppercase tracking-wide"
              >
                {formatPercentage(gain)}
              </Badge>
            </div>
            <div className="mt-6 h-72 lg:h-80">
              <Line
                data={chartData}
                options={chartOptions}
                aria-hidden="true"
              />
            </div>
            <p className="mt-4 text-xs text-muted-foreground">
              Static illustration showing how we visualise long-term momentum
              with our built-in chart tools.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
