import { cn } from "@/lib/utils";
import { Badge } from "../ui/badge";

export const MarketAnalysisExample = () => {
  return (
    <div className="mb-4 md:mb-6 rounded-lg border border-border/40 bg-muted/20 p-3 md:p-5 ">
      <div className="mb-3 flex items-center gap-2">
        <Badge
          className={cn(
            "border-0 px-3 py-1 text-xs font-semibold uppercase tracking-wide bg-muted text-muted-foreground",
          )}
        >
          HOLD
        </Badge>
        <span className="text-sm font-medium text-foreground">
          Market Analysis Example
        </span>
      </div>
      <div className="space-y-3 text-sm text-muted-foreground">
        <p className="leading-relaxed">
          At <span className="font-semibold text-foreground">$48,230</span> with
          a 5-day observation window, our analysis suggests a{" "}
          <span className="font-semibold text-foreground">HOLD</span> position.
        </p>
        <p className="leading-relaxed">
          While macro conditions indicate the market could enter a cooling
          period, institutional buying pressure and retail support are
          maintaining price stability around current levels.
        </p>
        <p className="text-xs italic text-muted-foreground/80">
          This example demonstrates how our signals combine technical indicators
          with market context to provide actionable insights.
        </p>
      </div>
    </div>
  );
};
