import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type Plan = {
  name: string;
  price: string;
  cadence: string;
  description: string;
  features: string[];
  highlight?: boolean;
  badge?: string;
  helper?: string;
  cta?: string;
};

const plans: Plan[] = [
  {
    name: "Free",
    price: "$0",
    cadence: "/mo",
    description:
      "Stay in the loop with our two flagship symbols and nightly recaps.",
    features: [
      "BTC-USD + AAPL coverage",
      "Nightly RSI + EMA commentary",
      "Email alerts when strength ≥ 70",
    ],
    cta: "Start for free",
  },
  {
    name: "Signals+ Monthly",
    price: "$39",
    cadence: "/mo",
    description:
      "Unlock the full dashboard, custom watchlists, and intraday reruns.",
    features: [
      "Up to 10 tracked symbols",
      "On-demand intraday refresh",
      "Priority dashboard + email alerts",
      "Full reasoning history",
    ],
    cta: "Upgrade monthly",
  },
  {
    name: "Signals+ Yearly",
    price: "$312",
    cadence: "/yr",
    description:
      "Best for calm operators who want the daily briefing all year long.",
    features: [
      "Everything in Monthly",
      "Quarterly strategy check-in",
      "Signal backlog exports",
    ],
    highlight: true,
    badge: "4 months free",
    helper: "~$26/mo effective",
    cta: "Go yearly",
  },
];

export default function Pricing() {
  return (
    <section
      aria-labelledby="pricing-heading"
      className="relative isolate px-4 py-16 sm:py-24"
    >
      <div className="container-app">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-muted-foreground">
            Pricing
          </p>
          <h2
            id="pricing-heading"
            className="mt-4 text-3xl font-semibold text-foreground sm:text-4xl"
          >
            Calm pricing for explainable market signals
          </h2>
          <p className="mt-4 text-base text-muted-foreground sm:text-lg">
            Every tier ships the same audited RSI + EMA pipeline, Resend alerts,
            and a dashboard that speaks plain English.
          </p>
        </div>

        <div className="mx-auto mt-12 grid max-w-6xl gap-6 md:grid-cols-2 lg:grid-cols-3">
          {plans.map((plan) => (
            <Card
              key={plan.name}
              className={cn(
                "relative flex h-full flex-col border border-border/60 bg-card/80 p-6 shadow-lg",
                plan.highlight &&
                  "border-primary bg-primary text-primary-foreground",
              )}
            >
              {plan.badge && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full border border-border/80 bg-background/90 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-foreground shadow-sm">
                  {plan.badge}
                </span>
              )}
              <div className="flex flex-1 flex-col">
                <div>
                  <h3 className="text-2xl font-semibold">{plan.name}</h3>
                  <p
                    className={cn(
                      "mt-2 text-sm text-muted-foreground",
                      plan.highlight && "text-primary-foreground/80",
                    )}
                  >
                    {plan.description}
                  </p>
                </div>

                <div className="mt-6">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span
                    className={cn(
                      "text-base text-muted-foreground",
                      plan.highlight && "text-primary-foreground/80",
                    )}
                  >
                    {plan.cadence}
                  </span>
                  {plan.helper && (
                    <p
                      className={cn(
                        "mt-1 text-sm text-muted-foreground",
                        plan.highlight && "text-primary-foreground/80",
                      )}
                    >
                      {plan.helper}
                    </p>
                  )}
                </div>

                <ul
                  className={cn(
                    "mt-8 space-y-3 text-sm text-muted-foreground",
                    plan.highlight && "text-primary-foreground/80",
                  )}
                >
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2">
                      <span className="mt-0.5 text-lg leading-none">•</span>
                      <span className="leading-6">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <Button
                asChild
                variant={plan.highlight ? "secondary" : "outline"}
                className={cn(
                  "mt-8 w-full font-semibold",
                  plan.highlight && "bg-white text-primary hover:bg-white/90",
                )}
              >
                <Link href="/signals">{plan.cta ?? "Get started"}</Link>
              </Button>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
