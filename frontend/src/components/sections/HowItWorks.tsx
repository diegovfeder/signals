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
      title: "Track",
      description:
        "We watch the market 24/7 so you don't have to stare at charts all day.\n Fresh insights, zero effort",
      delay: 0,
    },
    {
      number: "02",
      title: "Analyze",
      description:
        "We spot the best times to buy or sell by reading price patterns and momentum.\n Each signal gets a confidence score you can trust.",
      delay: 100,
    },
    {
      number: "03",
      title: "Alert",
      description:
        "You get a simple email explaining what's happening and whether it matters.\n No jargon, just clear guidance you can act on.",
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
            <Badge variant="metal" className="mb-8 gap-2 px-4 py-2 text-sm">
              <span className="text-ring">✦</span> How It Works
            </Badge>
            <h2 className="text-4xl font-bold tracking-tight text-foreground md:text-5xl">
              From market chaos to clear decisions
            </h2>
            <p className="max-w-2xl text-muted-foreground/80 md:text-xl">
              Three simple steps turn overwhelming price charts into actionable
              signals you can understand in seconds.
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
