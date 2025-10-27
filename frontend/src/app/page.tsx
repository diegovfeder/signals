/**
 * Landing Page (Marketing)
 *
 * Product-focused landing page with narrative arc:
 * Hero → Value → How → Proof → CTA
 *
 * Design: Minimal, purposeful, human-centered (Resend-inspired)
 */

import type { Metadata } from 'next'
import Link from 'next/link'
import AppHeader from '@/components/layout/AppHeader'
import Hero from '@/components/sections/Hero'
import ValueProps from '@/components/sections/ValueProps'
import HowItWorks from '@/components/sections/HowItWorks'
import Coverage from '@/components/sections/Coverage'
import SocialProof from '@/components/sections/SocialProof'
import FinalCTA from '@/components/sections/FinalCTA'
import Footer from '@/components/sections/Footer'

export const metadata: Metadata = {
  title: 'SIGNALS — Automated Trading Signals (RSI & EMA)',
  description: 'Multi-asset signals every 15 minutes with plain-English explanations. Email alerts for high-confidence setups.',
}

export default function Home() {
  return (
    <>
      <main>
        <AppHeader
          rightSlot={
            <Link href="/dashboard" className="btn-primary text-sm">
              Go to Dashboard
            </Link>
          }
        />
        <Hero />
        <ValueProps />
        <HowItWorks />
        <Coverage />
        <SocialProof />
        <FinalCTA />
      </main>
      <Footer />
    </>
  )
}
