/**
 * SignalCard Component
 *
 * Display a single trading signal with BUY/SELL/HOLD type, strength, and reasoning.
 * Updated with shadcn Card component and dark theme optimizations.
 */

import type { JSX } from "react";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

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
  // Determine signal badge variant and color
  const getBadgeVariant = () => {
    switch (signalType) {
      case "BUY":
        return "default" as const;
      case "SELL":
        return "destructive" as const;
      default:
        return "secondary" as const;
    }
  };

  const getBadgeStyles = () => {
    switch (signalType) {
      case "BUY":
        return "bg-primary text-primary-foreground border-0";
      case "SELL":
        return "bg-red-600 text-white border-0";
      default:
        return "bg-muted text-muted-foreground border-0";
    }
  };

  // Determine strength bar color
  const numericStrength = Number.isFinite(strength) ? strength : 0;
  const confidence = Math.max(0, Math.min(100, Math.round(numericStrength)));
  const getStrengthColor = () => {
    if (confidence >= 70) return "bg-primary";
    if (confidence >= 40) return "bg-yellow-500";
    return "bg-red-500";
  };
  const confidenceLabel =
    confidence >= 70 ? "Strong" : confidence >= 40 ? "Moderate" : "Weak";

  return (
    <Card className="p-6 animate-fade-in group h-full flex flex-col justify-between border-2 border-border hover:border-primary transition-all duration-300 hover:shadow-lg">
      {/* Header with symbol and price */}
      <div className="flex items-baseline justify-between mb-4">
        <h2 className="text-xl font-semibold text-foreground group-hover:text-ring transition-colors">
          {symbol}
        </h2>
        <span className="text-sm text-muted-foreground font-mono">
          ${price?.toFixed(2) ?? "-"}
        </span>
      </div>

      {/* Signal type badge and strength */}
      <div className="flex items-center justify-between mb-4">
        <Badge className={getBadgeStyles()}>
          {signalType}
        </Badge>
        <div className="text-right">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">
            Confidence
          </p>
          <p className="text-lg font-semibold text-foreground font-mono">
            {confidence}%
          </p>
          <p className="text-xs text-muted-foreground">{confidenceLabel}</p>
        </div>
      </div>

      {/* Strength meter */}
      <div className="mb-5">
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${getStrengthColor()}`}
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

      {/* Reasoning */}
      {reasoning?.length > 0 ? (
        <ul className="mb-5 text-sm text-foreground/90 space-y-2">
          {reasoning.slice(0, 2).map((r: string, idx: number) => (
            <li key={idx} className="flex items-start gap-2">
              <span className="text-ring mt-0.5">•</span>
              <span className="line-clamp-2">{r}</span>
            </li>
          ))}
        </ul>
      ) : (
        <div className="mb-5 text-sm text-muted-foreground">No reasoning available</div>
      )}

      {/* View details link */}
      <Link
        href={`/signals/${encodeURIComponent(symbol)}`}
        className="inline-block text-sm text-ring hover:text-primary transition-colors group-hover:underline"
      >
        View details →
      </Link>
    </Card>
  );
}
