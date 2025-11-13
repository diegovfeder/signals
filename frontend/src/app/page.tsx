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
// import Pricing from "@/components/sections/Pricing";
import FinalCTA from "@/components/sections/FinalCTA";
// import ValueProps from "@/components/sections/ValueProps";
import Coverage from "@/components/sections/Coverage";
// import SocialProof from "@/components/sections/SocialProof";
// import FinalCTA from "@/components/sections/FinalCTA";

export const metadata: Metadata = {
  title: "Signals — Market insights made human",
  description:
    "Turn market chaos into clear decisions. We analyze Apple and Bitcoin daily and send you confidence-scored signals you can understand in seconds. Zero effort, just results.",
};

export default function Home() {
  return (
    <>
      <main>
        <Hero />
        <HowItWorks />
        {/* <ValueProps /> */}
        {/*<Pricing />*/}
        <Coverage />
        {/* <SocialProof /> */}
        <FinalCTA />
      </main>
    </>
  );
}
