/**
 * Numbered Step Component
 *
 * Circular numbered badge for step-by-step flows
 * Inspired by tweakcn.com "How It Works" section
 */

import { cn } from "@/lib/utils";

interface NumberedStepProps {
  number: string;
  title: string;
  description: string;
  className?: string;
  delay?: number;
}

export function NumberedStep({
  number,
  title,
  description,
  className,
  delay = 0,
}: NumberedStepProps) {
  return (
    <div
      className={cn("flex flex-col items-center text-center group", className)}
      style={{
        opacity: 1,
        transform: "none",
        animationDelay: `${delay}ms`,
      }}
    >
      {/* HUGE green number circle */}
      <div className="mb-8 flex size-20 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-xl transition-all duration-300">
        <span className="text-4xl font-bold pb-0!">{number}</span>
      </div>

      {/* Title */}
      <h3 className="mb-4 text-2xl font-bold text-foreground md:text-3xl">
        {title}
      </h3>

      {/* Description */}
      <p className="max-w-sm text-lg text-muted-foreground/90 leading-relaxed whitespace-pre-line text-pretty">
        {description}
      </p>
    </div>
  );
}
