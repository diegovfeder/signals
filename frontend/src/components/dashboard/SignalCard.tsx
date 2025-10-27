/**
 * SignalCard Component
 *
 * Display a single trading signal with BUY/SELL/HOLD type, strength, and reasoning.
 * Features glass morphism design inspired by Resend.
 */

import type { JSX } from "react";
import Link from "next/link";

interface SignalCardProps {
  symbol: string;
  signalType: "BUY" | "SELL" | "HOLD";
  strength: number;
  reasoning: string[];
  price: number;
}

export default function SignalCard({
  symbol,
  signalType,
  strength,
  reasoning,
  price,
}: SignalCardProps): JSX.Element {
  // Determine signal badge colors
  const getBadgeClasses = () => {
    switch (signalType) {
      case "BUY":
        return "bg-success/20 text-success border-success/30";
      case "SELL":
        return "bg-danger/20 text-danger border-danger/30";
      default:
        return "bg-neutral/20 text-neutral border-neutral/30";
    }
  };

  // Determine strength bar color
  const numericStrength = Number.isFinite(strength) ? strength : 0;
  const confidence = Math.max(0, Math.min(100, Math.round(numericStrength)));
  const getStrengthColor = () => {
    if (confidence >= 70) return "bg-success";
    if (confidence >= 40) return "bg-warning";
    return "bg-danger";
  };
  const confidenceLabel =
    confidence >= 70 ? "Strong" : confidence >= 40 ? "Moderate" : "Weak";

  return (
    <div className="card p-6 animate-fade-in group h-full flex flex-col justify-between">
      {/* Header with symbol and price */}
      <div className="flex items-baseline justify-between mb-4">
        <h2 className="text-xl font-semibold text-foreground-secondary group-hover:text-foreground transition-colors">
          {symbol}
        </h2>
        <span className="text-sm text-muted font-mono">
          ${price?.toFixed(2) ?? "-"}
        </span>
      </div>

      {/* Signal type badge and strength */}
      <div className="flex items-center justify-between mb-4">
        <div
          className={`px-4 py-1.5 rounded-full text-sm font-semibold border ${getBadgeClasses()} backdrop-blur-sm`}
        >
          {signalType}
        </div>
        <div className="text-right">
          <p className="text-xs uppercase tracking-wide text-muted">
            Confidence
          </p>
          <p className="text-lg font-semibold text-foreground-secondary font-mono">
            {confidence}%
          </p>
          <p className="text-xs text-foreground-muted">{confidenceLabel}</p>
        </div>
      </div>

      {/* Strength meter */}
      <div className="mb-5">
        <div className="h-2 bg-background-tertiary rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${getStrengthColor()}`}
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

      {/* Reasoning */}
      {reasoning?.length > 0 ? (
        <ul className="mb-5 text-sm text-foreground-secondary space-y-2">
          {reasoning.slice(0, 2).map((r: string, idx: number) => (
            <li key={idx} className="flex items-start gap-2">
              <span className="text-primary mt-0.5">•</span>
              <span className="line-clamp-2">{r}</span>
            </li>
          ))}
        </ul>
      ) : (
        <div className="mb-5 text-sm text-muted">No reasoning available</div>
      )}

      {/* View details link */}
      <Link
        href={`/signals/${encodeURIComponent(symbol)}`}
        className="inline-block text-sm text-primary hover:text-primary-hover transition-colors group-hover:underline"
      >
        View details →
      </Link>
    </div>
  );
}
