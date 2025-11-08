import Link from "next/link";
import { Button } from "@/components/ui/button";
import { HERO } from "@/lib/utils/constants";

export default function Hero() {
  return (
    <section className="relative isolate overflow-hidden pt-20 pb-16 sm:pt-32 sm:pb-20 px-4 min-h-[94vh] flex items-center">
      {/* GREEN animated grid background - more visible */}
      <div
        className="absolute inset-0 -z-10 opacity-40"
        style={{
          backgroundImage: `linear-gradient(to right, rgba(0, 98, 57, 0.5) 1px, transparent 1px), linear-gradient(to bottom, rgba(0, 98, 57, 0.15) 1px, transparent 1px)`,
          backgroundSize: "4rem 4rem",
        }}
      />

      {/* GIANT green blur orb */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[1200px] rounded-full blur-[150px] animate-pulse -z-10"
        style={{
          background:
            "radial-gradient(circle, rgba(0, 98, 57, 0.9) 0%, transparent 40%)",
        }}
      />

      {/* Floating green particles */}
      <div className="absolute top-20 left-10 w-3 h-3 rounded-full bg-ring/60 particle-green -z-10" />
      <div
        className="absolute top-40 right-20 w-2 h-2 rounded-full bg-ring/40 particle-green -z-10"
        style={{ animationDelay: "1s" }}
      />
      <div
        className="absolute bottom-40 left-1/4 w-2.5 h-2.5 rounded-full bg-ring/50 particle-green -z-10"
        style={{ animationDelay: "2s" }}
      />

      <div className="container-app relative">
        <div className="mx-auto max-w-4xl text-center">
          <h1 className="my-8 text-4xl font-bold leading-1.5 tracking-tight animate-slide-up md:text-5xl lg:text-6xl text-foreground">
            {HERO.TITLE}
          </h1>
          <h2
            className="mx-auto mb-12 max-w-2xl text-2xl text-muted-foreground/90 animate-slide-up"
            style={{ animationDelay: "100ms" }}
          >
            {HERO.DESCRIPTION}
          </h2>

          <div
            className="mb-8 flex flex-col items-center justify-center gap-4 sm:flex-row animate-slide-up"
            style={{ animationDelay: "200ms" }}
          >
            <Button
              asChild
              size="xl"
              className="text-lg px-10 py-6 font-semibold"
            >
              <Link href="/signals">View Live Signals →</Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}
