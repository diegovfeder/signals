/**
 * Navbar Component
 * Logo, navigation links, and primary CTA
 */

import Link from 'next/link'

export default function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border backdrop-blur-xl bg-background/80">
      <div className="container-app">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="text-xl font-bold text-foreground hover:text-foreground-secondary transition-colors">
            SIGNALS
          </Link>

          {/* Navigation */}
          <div className="flex items-center gap-6">
            <Link
              href="/dashboard"
              className="text-sm text-foreground-muted hover:text-foreground transition-colors"
            >
              Dashboard
            </Link>
            <a
              href="https://github.com/diegovfeder"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-foreground-muted hover:text-foreground transition-colors"
            >
              GitHub
            </a>
            <button className="btn-primary text-sm">
              Get Email Alerts
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
