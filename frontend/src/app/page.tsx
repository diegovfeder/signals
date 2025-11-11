/**
 * Landing Page (Marketing)
 *
 * Product-focused landing page with narrative arc:
 * Hero → Value → How → Proof → CTA
 *
 * Design: Minimal, purposeful, human-centered (Resend-inspired)
 */

import type { Metadata } from "next";

import Hero from "@/components/sections/Hero";
import HowItWorks from "@/components/sections/HowItWorks";
import Pricing from "@/components/sections/Pricing";
import FinalCTA from "@/components/sections/FinalCTA";
// import SignalsPreview from "@/components/sections/SignalsPreview";
// import ValueProps from "@/components/sections/ValueProps";
// import Coverage from "@/components/sections/Coverage";
// import SocialProof from "@/components/sections/SocialProof";
// import FinalCTA from "@/components/sections/FinalCTA";

export const metadata: Metadata = {
  title: "SIGNALS — Automated Trading Signals (RSI & EMA)",
  description:
    "Daily multi-asset signals with plain-English explanations. Email alerts for high-confidence setups.",
};

export default function Home() {
  return (
    <>
      <main>
        <Hero />
        <HowItWorks />
        {/* <ValueProps /> */}
        {/*<Pricing />*/}
        {/* <Coverage /> */}
        {/* <SocialProof /> */}
        <FinalCTA />
      </main>
    </>
  );
}
