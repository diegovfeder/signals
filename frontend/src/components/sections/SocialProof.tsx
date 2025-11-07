/**
 * Social Proof Component - Enhanced
 * Transparency with green card layout
 */

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Shield, Code, Zap } from "lucide-react";

export default function SocialProof() {
  return (
    <section className="relative py-20 px-4 md:py-32 bg-[#0a0a0a]">
      {/* Subtle green gradient */}
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_center,rgba(0,98,57,0.06),transparent_70%)]" />

      <div className="container-app">
        <div className="max-w-4xl mx-auto">
          <Card className="border-2 border-primary/20 bg-gradient-to-br from-card to-card/50 p-8 md:p-12 shadow-xl text-center">
            {/* MVP Badge */}
            <div className="mb-8">
              <Badge className="inline-flex items-center gap-2 px-5 py-2 text-base shadow-lg bg-primary text-primary-foreground glow-green border-0">
                <Zap className="size-4" />
                MVP Testing
              </Badge>
            </div>

            {/* Main message */}
            <h3 className="text-2xl md:text-3xl font-bold text-foreground mb-6">
              We're shipping openly
            </h3>
            <p className="text-lg md:text-xl text-muted-foreground/90 mb-8 max-w-2xl mx-auto">
              No paywall while we learn together. Free access during MVP
              testing.
            </p>

            {/* Trust indicators */}
            <div className="grid gap-6 md:grid-cols-2 max-w-2xl mx-auto mt-10">
              <div className="flex items-start gap-3 text-left">
                <div className="flex size-10 items-center justify-center rounded-full bg-primary/10 text-ring">
                  <Shield className="size-5" />
                </div>
                <div>
                  <div className="font-semibold text-foreground mb-1">
                    Transparent
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Open-source code, clear methodology
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-3 text-left">
                <div className="flex size-10 items-center justify-center rounded-full bg-primary/10 text-ring">
                  <Code className="size-5" />
                </div>
                <div>
                  <div className="font-semibold text-foreground mb-1">
                    Educational
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Learn technical analysis fundamentals
                  </div>
                </div>
              </div>
            </div>

            {/* Disclaimer */}
            <p className="mt-10 text-sm text-muted-foreground/70 border-t border-border/40 pt-6">
              ⚠️ This is not financial advice. Trading involves risk. Use at
              your own discretion.
            </p>
          </Card>
        </div>
      </div>
    </section>
  );
}
