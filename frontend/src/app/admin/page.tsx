import Link from 'next/link'

export default function AdminHome() {
  return (
    <div className="space-y-8">
      <section className="card p-6 space-y-3">
        <h1 className="text-3xl font-bold">Admin Console</h1>
        <p className="text-sm text-muted">
          Internal utilities for developers: rerun backtests, inspect subscriber health, and debug
          new flows. Guard these routes behind auth in production.
        </p>
        <div className="flex flex-col sm:flex-row gap-3">
          <Link href="/admin/backtests" className="btn-primary text-center px-6 py-3 rounded-xl">
            View Backtests
          </Link>
          <Link href="/admin/subscribers" className="btn-secondary text-center px-6 py-3 rounded-xl border border-border">
            View Subscribers
          </Link>
        </div>
      </section>
      <section className="card p-6 space-y-2 text-sm text-muted">
        <h2 className="text-lg font-semibold text-foreground">Runbook</h2>
        <ol className="list-decimal list-inside space-y-2">
          <li>
            Backfill data: <code className="code-block">python -m flows.historical_backfill --symbols BTC-USD,AAPL --backfill-range 2y</code>
          </li>
          <li>
            Recompute signals: <code className="code-block">python -m flows.signal_replay --symbols BTC-USD,AAPL --range-label 2y</code>
          </li>
          <li>
            Check summaries here and refresh the dashboard if strategies changed.
          </li>
        </ol>
      </section>
    </div>
  )
}
