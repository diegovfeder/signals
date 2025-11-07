/**
 * Animated Grid Background
 *
 * Subtle dot grid pattern with floating blur orbs
 * Inspired by tweakcn.com design system
 */

import { cn } from '@/lib/utils'

interface AnimatedGridBackgroundProps {
  children?: React.ReactNode
  className?: string
  showOrbs?: boolean
  variant?: 'primary' | 'neutral'
}

export function AnimatedGridBackground({
  children,
  className,
  showOrbs = true,
  variant = 'primary',
}: AnimatedGridBackgroundProps) {
  return (
    <div className={cn('relative isolate overflow-hidden', className)}>
      {/* Grid pattern */}
      <div
        className="absolute inset-0 -z-10"
        style={{
          backgroundImage: `linear-gradient(to right, hsl(from var(--${variant === 'primary' ? 'primary' : 'foreground'}) h s l / 0.075) 1px, transparent 1px), linear-gradient(to bottom, hsl(from var(--${variant === 'primary' ? 'primary' : 'foreground'}) h s l / 0.075) 1px, transparent 1px)`,
          backgroundSize: '4rem 4rem',
        }}
      />

      {/* Floating blur orbs */}
      {showOrbs && (
        <>
          <div
            className="absolute -top-24 -left-24 w-64 h-64 rounded-full blur-3xl animate-pulse"
            style={{
              background: `hsl(from var(--${variant === 'primary' ? 'primary' : 'foreground'}) h s l / 0.15)`,
            }}
          />
          <div
            className="absolute -bottom-24 -right-24 w-64 h-64 rounded-full blur-3xl animate-pulse"
            style={{
              background: `hsl(from var(--${variant === 'primary' ? 'primary' : 'foreground'}) h s l / 0.15)`,
              animationDelay: '1.5s',
            }}
          />
        </>
      )}

      {/* Content */}
      <div className="relative">{children}</div>
    </div>
  )
}
