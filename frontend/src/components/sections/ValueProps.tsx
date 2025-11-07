/**
 * Value Props Component
 * Four key benefits presented as enhanced feature cards
 * Redesigned with tweakcn design system
 */

import { MessageSquare, Globe, TrendingUp, Mail } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { FeatureCard } from '@/components/ui/feature-card'

export default function ValueProps() {
  const props = [
    {
      icon: MessageSquare,
      title: 'Clarity',
      description: 'Signals explained in plain English, not cryptic jargon.',
      delay: 0,
    },
    {
      icon: Globe,
      title: 'Coverage',
      description: 'Four core markets—crypto, stocks, ETFs, and forex—in one unified view.',
      delay: 100,
    },
    {
      icon: TrendingUp,
      title: 'Confidence Score',
      description: 'Each setup scored from 0–100 so you know the conviction behind every signal.',
      delay: 200,
    },
    {
      icon: Mail,
      title: 'Inbox Alerts',
      description: 'Strong signals delivered to your email when opportunities arise.',
      delay: 300,
    },
  ]

  return (
    <section className="relative isolate w-full py-20 px-4 md:py-32 bg-[#0a0a0a]">
      {/* Darker background with green radial gradient */}
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_center,rgba(0,98,57,0.08),transparent_70%)]" />

      <div className="container-app">
        {/* Section header with green accent */}
        <div className="mb-16 flex flex-col items-center justify-center space-y-4 text-center">
          <Badge className="inline-flex items-center gap-2 px-4 py-2 text-sm shadow-md bg-primary/20 text-ring border border-primary/40 glow-ring">
            <span className="text-ring">✦</span> Features
          </Badge>
          <h2 className="text-4xl font-bold tracking-tight text-foreground md:text-5xl">
            Powerful Signals, Simple Interface
          </h2>
          <p className="max-w-[800px] text-muted-foreground/80 md:text-xl">
            All the tools you need to make informed trading decisions without the complexity.
          </p>
        </div>

        {/* Feature cards grid with more spacing */}
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {props.map((prop) => (
            <FeatureCard
              key={prop.title}
              icon={prop.icon}
              title={prop.title}
              description={prop.description}
              delay={prop.delay}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
