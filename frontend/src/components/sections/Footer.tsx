/**
 * Footer Component
 * Credits and navigation links
 */

import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="py-8 px-4 border-t border-border">
      <div className="container-app">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Credits */}
          <p className="text-sm text-foreground-muted">
            SIGNALS MVP — by Diego Feder
          </p>

          {/* Links */}
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
          </div>
        </div>
      </div>
    </footer>
  )
}
