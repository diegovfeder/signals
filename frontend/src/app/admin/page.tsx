import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function AdminHome() {
  return (
    <div className="space-y-8">
      <Card className="p-8 space-y-4 border border-border">
        <h1 className="text-3xl font-bold text-foreground">Admin Console</h1>
        <p className="text-sm text-muted-foreground">
          Internal utilities for developers: rerun backtests, inspect subscriber
          health, and debug new flows. Guard these routes behind auth in
          production.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 pt-2">
          <Button asChild size="lg" className="text-center">
            <Link href="/admin/backtests">View Backtests</Link>
          </Button>
          <Button asChild variant="secondary" size="lg" className="text-center">
            <Link href="/admin/subscribers">View Subscribers</Link>
          </Button>
        </div>
      </Card>
      <Card className="p-8 space-y-4 border border-border">
        <h2 className="text-lg font-semibold text-foreground">Runbook</h2>
        <ol className="list-decimal list-inside space-y-3 text-sm text-muted-foreground">
          <li>
            Backfill data:&nbsp;
            <code className="bg-muted px-2 py-1 rounded font-mono text-xs">
              python -m pipe.flows.historical_backfill --symbols AAPL,BTC-USD
              --backfill-range 2y
            </code>
          </li>
          <li>
            Recompute signals:&nbsp;
            <code className="bg-muted px-2 py-1 rounded font-mono text-xs">
              python -m pipe.flows.signal_replay --symbols AAPL,BTC-USD
              --range-label 2y
            </code>
          </li>
          <li>
            Check summaries here and refresh the dashboard if strategies
            changed.
          </li>
        </ol>
      </Card>
    </div>
  );
}
