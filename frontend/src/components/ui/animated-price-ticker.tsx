"use client";

import { useEffect, useState } from "react";

interface AnimatedPriceTickerProps {
  startPrice?: number;
  endPrice?: number;
  duration?: number;
  symbol?: string;
}

export function AnimatedPriceTicker({
  startPrice = 45000,
  endPrice = 48230.12,
  duration = 2000,
  symbol = "BTC-USD",
}: AnimatedPriceTickerProps) {
  const [price, setPrice] = useState(startPrice);
  const [mounted, setMounted] = useState(false);

  const percentGain = ((endPrice - startPrice) / startPrice) * 100;

  // Generate sparkline path points
  const points = 12;
  const width = 100;
  const height = 40;
  const sparklineData = Array.from({ length: points }, (_, i) => {
    const x = (i / (points - 1)) * width;
    const progress = i / (points - 1);
    // Add some realistic volatility with sine wave
    const volatility = Math.sin(i * 0.8) * 3;
    const y = height - progress * height * 0.7 + volatility;
    return { x, y };
  });

  const pathD = sparklineData
    .map((point, i) => `${i === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ");

  // Fix hydration - detect client-side mount
  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 0);
    return () => clearTimeout(timer);
  }, []);

  // Animate price counter
  useEffect(() => {
    if (!mounted) return;

    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Easing function for smooth animation
      const eased = 1 - Math.pow(1 - progress, 3);
      const currentPrice = startPrice + (endPrice - startPrice) * eased;

      setPrice(currentPrice);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    const animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [mounted, startPrice, endPrice, duration]);

  return (
    <div
      className="mx-2 flex items-center justify-center rounded-lg border bg-slate-900/30 px-4 py-3 transition-all duration-1000"
      style={{
        borderColor: mounted
          ? "rgba(148, 163, 184, 0.3)"
          : "rgba(148, 163, 184, 0.2)",
        animation: mounted ? "border-pulse 3s ease-in-out infinite" : "none",
      }}
    >
      {mounted && (
        <style jsx>{`
          @keyframes border-pulse {
            0%,
            100% {
              border-color: rgba(148, 163, 184, 0.25);
              box-shadow: 0 0 0 rgba(203, 213, 225, 0);
            }
            50% {
              border-color: rgba(148, 163, 184, 0.4);
              box-shadow: 0 0 8px rgba(203, 213, 225, 0.2);
            }
          }
        `}</style>
      )}
      {/* Price display */}
      <div className="flex items-center">
        <div className="flex flex-col">
          <span className="text-[10px] font-medium uppercase tracking-wider text-slate-400/80">
            {symbol}
          </span>
          <span className="font-mono text-lg font-semibold tabular-nums text-slate-200">
            $
            {price.toLocaleString("en-US", {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </span>
          <span className="flex items-center gap-1 text-[10px] font-medium text-emerald-400">
            <svg
              className="h-3 w-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
              />
            </svg>
            +{percentGain.toFixed(2)}%
          </span>
        </div>
      </div>
    </div>
  );
}
