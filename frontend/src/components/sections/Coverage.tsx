/**
 * Coverage Component - Enhanced
 * Asset coverage with shadcn Cards and green accents
 */

import { Bitcoin, Cpu } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function Coverage() {
  const assets = [
    {
      symbol: "AAPL",
      label: "Stock",
      icon: Cpu,
      description: "Apple and blue-chip equities",
      delay: 0,
    },
    {
      symbol: "BTC-USD",
      label: "Crypto",
      icon: Bitcoin,
      description: "Bitcoin and major cryptocurrencies",
      delay: 100,
    },
  ];

  return (
    <section className="relative py-20 px-4 md:py-32 bg-background">
      <div className="container-app">
        <div className="mb-16 flex flex-col items-center justify-center space-y-4 text-center">
          <Badge
            variant="metal"
            className="inline-flex items-center gap-2 px-4 py-2 text-sm shadow-md "
          >
            <span className="text-ring">✦</span> Coverage
          </Badge>
          <h2 className="text-4xl font-bold tracking-tight text-foreground md:text-5xl">
            Multi-asset strategy monitoring
          </h2>
          <p className="max-w-2xl text-muted-foreground/80 md:text-xl">
            Track signals across major markets with diverse technical analyses
          </p>
        </div>

        <div className="grid gap-8 max-w-4xl mx-auto md:grid-cols-2">
          {assets.map((asset) => (
            <Card
              key={asset.symbol}
              className="group relative overflow-hidden border-2 border-border/40 bg-linear-to-br from-card to-card/50 p-8 shadow-lg"
              style={{ animationDelay: `${asset.delay}ms` }}
            >
              <div className="flex flex-col items-center text-center">
                {/* Icon */}
                <div className="mb-6 flex size-16 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg">
                  <asset.icon className="size-8" />
                </div>

                {/* Symbol */}
                <div className="text-3xl font-bold text-foreground mb-2">
                  {asset.symbol}
                </div>

                {/* Asset Type Badge */}
                <Badge variant="muted" className="mb-4">
                  {asset.label}
                </Badge>

                {/* Description */}
                <p className="text-muted-foreground/90">{asset.description}</p>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
