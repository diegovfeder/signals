/**
 * Feature Card Component
 *
 * Enhanced card with icon circle, hover effects, and gradient accents
 * Inspired by tweakcn.com feature showcase
 */

import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  className?: string;
  delay?: number;
}

export function FeatureCard({
  icon: Icon,
  title,
  description,
  className,
  delay = 0,
}: FeatureCardProps) {
  return (
    <div
      className={cn(
        "group h-full overflow-hidden rounded-xl border border-border/40 bg-linear-to-b from-card to-card/50 p-6 shadow-md backdrop-blur transition-all hover:border-primary hover:shadow-md",
        className,
      )}
      style={{
        opacity: 1,
        transform: "none",
        animationDelay: `${delay}ms`,
      }}
    >
      <div className="flex h-full flex-col">
        {/* GREEN Icon circle - solid background */}
        <div className="mb-5 flex size-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg transition-all duration-300">
          <Icon className="size-6" />
        </div>

        {/* Title */}
        <h3 className="mb-3 flex items-center gap-2 text-xl font-bold text-foreground">
          {title}
        </h3>

        {/* Description */}
        <p className="text-pretty text-muted-foreground/90 leading-relaxed">
          {description}
        </p>
      </div>
    </div>
  );
}
