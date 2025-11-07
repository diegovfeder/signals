/**
 * How It Works Component
 * Three-step process explanation with numbered badges
 * Enhanced with tweakcn design system
 */

import { Badge } from '@/components/ui/badge'
import { NumberedStep } from '@/components/ui/numbered-step'

export default function HowItWorks() {
  const steps = [
    {
      number: '01',
      title: 'We Analyze',
      description:
        'Fetch real-time prices and compute RSI + EMA indicators across all markets.',
      delay: 0,
    },
    {
      number: '02',
      title: 'We Score',
      description:
        'Turn technical conditions into a 0–100 confidence score for every signal.',
      delay: 100,
    },
    {
      number: '03',
      title: 'You Decide',
      description:
        'Review signals in the dashboard or act immediately from email alerts.',
      delay: 200,
    },
  ]

  return (
    <section className="relative isolate w-full bg-[#0d0d0d] py-20 px-4 md:py-32">
      {/* Subtle green gradient */}
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_center,rgba(0,98,57,0.06),transparent_70%)]" />

      <div className="container-app">
        <div className="mx-auto max-w-6xl">
          {/* Section header with green */}
          <div className="mb-20 flex flex-col items-center justify-center space-y-4 text-center">
            <Badge className="inline-flex items-center gap-2 px-4 py-2 text-sm shadow-md bg-primary/20 text-ring border border-primary/40 glow-ring">
              <span className="text-ring">✦</span> How It Works
            </Badge>
            <h2 className="text-4xl font-bold tracking-tight text-foreground md:text-5xl">
              Simple Process, Beautiful Results
            </h2>
            <p className="max-w-2xl text-muted-foreground/80 md:text-xl">
              Three steps from data to decision. Automated, transparent, actionable.
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
      </div>
    </section>
  )
}
