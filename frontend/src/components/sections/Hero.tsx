/**
 * Hero Component
 * Main headline, subheadline, CTAs, and live status
 */

import Link from 'next/link'

export default function Hero() {
  return (
    <section className="pt-32 pb-20 px-4 relative">
      <div className="container-app">
        <div className="max-w-3xl mx-auto text-center">
          {/* Live status pill */}
          <div className="inline-flex items-center gap-2 card px-3 py-1.5 mb-8 animate-fade-in">
            <span className="status-live" />
            <span className="text-xs text-foreground-muted">
              Live · scans every 15 minutes
            </span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-6xl font-bold mb-6 text-foreground leading-tight animate-slide-up">
            Automated trading signals that speak plain English.
          </h1>

          {/* Subheadline */}
          <p className="text-xl text-foreground-muted mb-10 animate-slide-up" style={{animationDelay: '100ms'}}>
            Email alerts and a simple dashboard for opportunities across crypto, stocks, ETFs, and forex.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-slide-up" style={{animationDelay: '200ms'}}>
            <Link href="/dashboard" className="btn-primary">
              Go to Dashboard
            </Link>
            <button className="btn-secondary">
              Get Email Alerts
            </button>
          </div>
        </div>
      </div>

      {/* Subtle background accent */}
      <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-primary/5 rounded-full blur-[120px]" />
      </div>
    </section>
  )
}
