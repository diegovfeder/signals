/**
 * How It Works Component
 * Three-step process explanation with numbered badges
 * Enhanced with tweakcn design system
 */

import { Badge } from "@/components/ui/badge";
import { NumberedStep } from "@/components/ui/numbered-step";
import { SubscribeForm } from "../forms/SubscribeForm";

export default function HowItWorks() {
  const steps = [
    {
      number: "01",
      title: "Sync",
      description:
        "Each evening Prefect ingests fresh Yahoo Finance OHLCV for your symbols, validates gaps, and stores everything in Supabase.",
      delay: 0,
    },
    {
      number: "02",
      title: "Diagnose",
      description:
        "Signals runs RSI, EMA, and custom heuristics to produce a 0–100 confidence score plus bullet-point reasoning you can read.",
      delay: 100,
    },
    {
      number: "03",
      title: "Brief",
      description:
        "Resend emails and the dashboard publish the same plain-English recap so you can act—or ignore—with full context in seconds.",
      delay: 200,
    },
  ];

  return (
    <section className="relative isolate w-full bg-[#0d0d0d] py-20 px-4 md:py-32">
      {/* Subtle green gradient */}
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_center,rgba(0,98,57,0.06),transparent_70%)]" />

      <div className="container-app">
        <div className="mx-auto max-w-6xl">
          {/* Section header with green */}
          <div className="mb-20 flex flex-col items-center justify-center space-y-4 text-center">
            <Badge className="mb-6 inline-flex items-center gap-2 px-4 py-2 text-sm shadow-md bg-primary/20 text-ring border border-primary/40">
              <span className="text-ring">✦</span> How It Works
            </Badge>
            <h2 className="text-4xl font-bold tracking-tight text-foreground md:text-5xl">
              From nightly sync to inbox-ready briefings
            </h2>
            <p className="max-w-2xl text-muted-foreground/80 md:text-xl">
              Three deliberate steps turn raw market data into human-language
              signals you can trust every morning.
            </p>
          </div>

          {/* Steps grid with connecting lines */}
          <div className="relative grid gap-16 md:grid-cols-3 md:gap-12">
            {steps.map((step) => (
              <NumberedStep
                key={step.number}
                number={step.number}
                title={step.title}
                description={step.description}
                delay={step.delay}
              />
            ))}
          </div>
        </div>
        {/* Subscribe form */}
        <div
          id="subscribe"
          className="mt-14 sm:mt-20 animate-slide-up"
          style={{ animationDelay: "150ms" }}
        >
          <SubscribeForm
            className="mx-auto max-w-2xl"
            helperText="No spam. We only email when a conviction-level signal triggers."
          />
        </div>
      </div>
    </section>
  );
}
