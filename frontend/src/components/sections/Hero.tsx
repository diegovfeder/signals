/**
 * Hero Component - DRAMATIC VERSION
 * Bigger, greener, more impactful
 * Dark theme with prominent #006239 green accents
 */

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { SubscribeForm } from '@/components/forms/SubscribeForm'

export default function Hero() {
  return (
    <section className="relative isolate overflow-hidden pt-20 pb-16 sm:pt-32 sm:pb-20 px-4 min-h-[90vh] flex items-center">
      {/* GREEN animated grid background - more visible */}
      <div
        className="absolute inset-0 -z-10 opacity-40"
        style={{
          backgroundImage: `linear-gradient(to right, rgba(0, 98, 57, 0.15) 1px, transparent 1px), linear-gradient(to bottom, rgba(0, 98, 57, 0.15) 1px, transparent 1px)`,
          backgroundSize: '4rem 4rem',
        }}
      />

      {/* GIANT green blur orb */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[1200px] rounded-full blur-[150px] animate-pulse -z-10"
        style={{
          background: 'radial-gradient(circle, rgba(0, 98, 57, 0.2) 0%, transparent 70%)',
        }}
      />

      {/* Floating green particles */}
      <div className="absolute top-20 left-10 w-3 h-3 rounded-full bg-ring/60 particle-green -z-10" />
      <div
        className="absolute top-40 right-20 w-2 h-2 rounded-full bg-ring/40 particle-green -z-10"
        style={{ animationDelay: '1s' }}
      />
      <div
        className="absolute bottom-40 left-1/4 w-2.5 h-2.5 rounded-full bg-ring/50 particle-green -z-10"
        style={{ animationDelay: '2s' }}
      />

      <div className="container-app relative">
        <div className="mx-auto max-w-4xl text-center">
          {/* Live status badge with green glow */}
          <div className="mb-10 animate-fade-in">
            <Badge className="inline-flex items-center gap-2 px-5 py-2 text-base shadow-lg bg-primary text-primary-foreground glow-green border-0">
              <span className="status-live" />
              Live · daily scans at 10 PM UTC
            </Badge>
          </div>

          {/* Hero headline */}
          <h1 className="mb-8 text-4xl font-bold leading-[1.1] tracking-tight animate-slide-up md:text-5xl lg:text-6xl text-foreground">
            Automated trading signals that speak plain English
          </h1>

          {/* Larger subheadline */}
          <p
            className="mx-auto mb-12 max-w-2xl text-2xl text-muted-foreground/90 animate-slide-up"
            style={{ animationDelay: '100ms' }}
          >
            Email alerts and a simple dashboard for opportunities across crypto,
            stocks, ETFs, and forex.
          </p>

          {/* Subscribe form */}
          <div
            id="subscribe"
            className="my-14 animate-slide-up"
            style={{ animationDelay: '150ms' }}
          >
            <SubscribeForm
              className="mx-auto max-w-2xl"
              helperText="No spam. We only email when a conviction-level signal triggers."
            />
          </div>

          {/* BIGGER CTA Button with green glow */}
          <div
            className="flex flex-col items-center justify-center gap-4 sm:flex-row animate-slide-up"
            style={{ animationDelay: '200ms' }}
          >
            <Button asChild size="lg" className="text-lg px-10 py-6 glow-green">
              <Link href="/dashboard">Go to Dashboard</Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
