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
      className="flex items-center gap-3 rounded-lg border bg-emerald-950/20 px-4 py-2 transition-all duration-1000"
      style={{
        borderColor: mounted ? "rgba(16, 185, 129, 0.3)" : "rgba(16, 185, 129, 0.2)",
        animation: mounted ? "border-pulse 3s ease-in-out infinite" : "none",
      }}
    >
      {mounted && (
        <style jsx>{`
          @keyframes border-pulse {
            0%, 100% {
              border-color: rgba(16, 185, 129, 0.2);
              box-shadow: 0 0 0 rgba(16, 185, 129, 0);
            }
            50% {
              border-color: rgba(16, 185, 129, 0.6);
              box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
            }
          }
        `}</style>
      )}
      {/* Price display */}
      <div className="flex flex-col">
        <span className="text-[10px] font-medium uppercase tracking-wider text-emerald-400/70">
          {symbol}
        </span>
        <span className="font-mono text-lg font-semibold tabular-nums text-emerald-300">
          ${price.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
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

      {/* Animated sparkline with traveling wave */}
      <div className="relative h-[50px] w-[100px]">
        {!mounted ? (
          // Static version for SSR
          <svg
            viewBox={`0 0 ${width} ${height}`}
            className="h-full w-full"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient id="static-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="rgb(52, 211, 153)" stopOpacity="0.3" />
                <stop offset="100%" stopColor="rgb(52, 211, 153)" stopOpacity="0" />
              </linearGradient>
            </defs>
            <path
              d={`${pathD} L ${width} ${height} L 0 ${height} Z`}
              fill="url(#static-gradient)"
              suppressHydrationWarning
            />
            <path
              d={pathD}
              fill="none"
              stroke="rgb(52, 211, 153)"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              suppressHydrationWarning
            />
          </svg>
        ) : (
          // Animated version for client
          <svg
            viewBox={`0 0 ${width} ${height}`}
            className="h-full w-full"
            preserveAspectRatio="none"
          >
            <defs>
              {/* Base gradient fill */}
              <linearGradient id="sparkline-fill" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="rgb(52, 211, 153)" stopOpacity="0.2" />
                <stop offset="100%" stopColor="rgb(52, 211, 153)" stopOpacity="0" />
              </linearGradient>

              {/* Traveling wave gradient */}
              <linearGradient id="wave-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="rgb(52, 211, 153)" stopOpacity="0">
                  <animate
                    attributeName="offset"
                    values="-0.5;1.5"
                    dur="3s"
                    repeatCount="indefinite"
                  />
                </stop>
                <stop offset="30%" stopColor="rgb(52, 211, 153)" stopOpacity="0.8">
                  <animate
                    attributeName="offset"
                    values="-0.2;1.8"
                    dur="3s"
                    repeatCount="indefinite"
                  />
                </stop>
                <stop offset="50%" stopColor="rgb(16, 185, 129)" stopOpacity="1">
                  <animate
                    attributeName="offset"
                    values="0;2"
                    dur="3s"
                    repeatCount="indefinite"
                  />
                </stop>
                <stop offset="70%" stopColor="rgb(52, 211, 153)" stopOpacity="0.8">
                  <animate
                    attributeName="offset"
                    values="0.2;2.2"
                    dur="3s"
                    repeatCount="indefinite"
                  />
                </stop>
                <stop offset="100%" stopColor="rgb(52, 211, 153)" stopOpacity="0">
                  <animate
                    attributeName="offset"
                    values="0.5;2.5"
                    dur="3s"
                    repeatCount="indefinite"
                  />
                </stop>
              </linearGradient>
            </defs>

            {/* Fill area under the line */}
            <path
              d={`${pathD} L ${width} ${height} L 0 ${height} Z`}
              fill="url(#sparkline-fill)"
              className="animate-pulse"
              style={{ animationDuration: "3s" }}
            />

            {/* Base sparkline (dimmer) */}
            <path
              d={pathD}
              fill="none"
              stroke="rgb(52, 211, 153)"
              strokeOpacity="0.4"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Traveling wave highlight */}
            <path
              d={pathD}
              fill="none"
              stroke="url(#wave-gradient)"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]"
            />

            {/* Pulsing endpoint dot */}
            <circle
              cx={sparklineData[sparklineData.length - 1].x}
              cy={sparklineData[sparklineData.length - 1].y}
              r="2.5"
              fill="rgb(52, 211, 153)"
              className="animate-ping"
              style={{ animationDuration: "2s" }}
            />
            <circle
              cx={sparklineData[sparklineData.length - 1].x}
              cy={sparklineData[sparklineData.length - 1].y}
              r="2"
              fill="rgb(16, 185, 129)"
            />
          </svg>
        )}
      </div>
    </div>
  );
}
