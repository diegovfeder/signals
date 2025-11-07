/**
 * Final CTA Component - FULL GREEN TAKEOVER
 * Last conversion opportunity with dramatic green gradient
 * Maximum visual impact
 */

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function FinalCTA() {
  return (
    <section className="relative isolate w-full overflow-hidden py-24 md:py-36 px-4 bg-gradient-to-br from-primary via-[#007a47] to-[#004d2e]">
      {/* GREEN animated grid background - VERY visible */}
      <div
        className="absolute inset-0 -z-10 opacity-30"
        style={{
          backgroundImage: `linear-gradient(to right, rgba(255, 255, 255, 0.1) 1px, transparent 1px), linear-gradient(to bottom, rgba(255, 255, 255, 0.1) 1px, transparent 1px)`,
          backgroundSize: "4rem 4rem",
        }}
      />

      {/* Multiple floating green blur orbs */}
      <div
        className="absolute -top-24 -left-24 w-96 h-96 rounded-full blur-3xl animate-pulse -z-10"
        style={{
          background:
            "radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%)",
        }}
      />
      <div
        className="absolute -bottom-24 -right-24 w-96 h-96 rounded-full blur-3xl animate-pulse -z-10"
        style={{
          background:
            "radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%)",
          animationDelay: "1.5s",
        }}
      />

      <div className="container-app relative">
        <div className="flex flex-col items-center justify-center space-y-8 text-center">
          <h2 className="text-4xl font-bold tracking-tight text-white md:text-5xl lg:text-6xl max-w-4xl">
            Start tracking signals today
          </h2>
          <p className="mx-auto max-w-[700px] text-xl text-white/90 md:text-2xl">
            Never miss a high-confidence trading opportunity. Free during MVP
            testing.
          </p>
          <div className="mt-6 flex flex-col gap-5 sm:flex-row">
            <Button
              asChild
              size="lg"
              variant="secondary"
              className="text-lg px-12 py-7 bg-white text-primary hover:bg-white/90 shadow-2xl hover:shadow-[0_0_40px_rgba(255,255,255,0.3)] border-0"
            >
              <Link href="/dashboard">
                Try it now
                <ArrowRight className="ml-2 size-5" />
              </Link>
            </Button>
            <Button
              asChild
              size="lg"
              className="text-lg px-12 py-7 bg-transparent text-white border-2 border-white/40 hover:bg-white/10 hover:border-white shadow-lg"
            >
              <Link
                href="https://github.com/diegovfeder/signals"
                target="_blank"
              >
                View on GitHub
              </Link>
            </Button>
          </div>
          <p className="mt-6 text-base text-white/80">
            No credit card required · Open source · Free to use
          </p>
        </div>
      </div>
    </section>
  );
}
