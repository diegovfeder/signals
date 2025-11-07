/**
 * Gradient Section Wrapper
 *
 * Full-width section with gradient background, grid pattern, and floating orbs
 * Perfect for CTA sections
 * Inspired by tweakcn.com CTA design
 */

import { cn } from '@/lib/utils'
import { AnimatedGridBackground } from './animated-grid-background'

interface GradientSectionProps {
  children: React.ReactNode
  className?: string
  variant?: 'primary' | 'secondary'
}

export function GradientSection({
  children,
  className,
  variant = 'primary',
}: GradientSectionProps) {
  const gradientClass =
    variant === 'primary'
      ? 'bg-gradient-to-br from-primary to-primary/80 text-primary-foreground'
      : 'bg-gradient-to-br from-accent to-accent/80 text-accent-foreground'

  return (
    <section
      className={cn(
        'relative isolate w-full overflow-hidden py-20 md:py-32',
        gradientClass,
        className
      )}
    >
      <AnimatedGridBackground variant={variant === 'primary' ? 'primary' : 'neutral'}>
        <div className="container-app relative">{children}</div>
      </AnimatedGridBackground>
    </section>
  )
}
