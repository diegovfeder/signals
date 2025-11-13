import "./globals.css";

import type { Metadata } from "next";

import AppHeader from "@/components/layout/AppHeader";
import { Button } from "@/components/ui/button";

import { AppProviders } from "./providers";
import Footer from "@/components/sections/Footer";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Signals — Market insights made human",
  description:
    "Stop staring at charts. We track Apple and Bitcoin 24/7 and email you only when something actually matters. Clear signals you can act on, not hype you have to decode.",
  keywords: [
    "market insights",
    "trading signals",
    "apple stock",
    "bitcoin",
    "AAPL",
    "BTC",
    "market timing",
    "daily market brief",
    "momentum analysis",
    "investment signals",
    "market alerts",
  ],
  authors: [{ name: "Diego Feder" }, { name: "Caue Feder" }],
  openGraph: {
    title: "Signals — Market insights made human",
    description:
      "We watch Apple and Bitcoin so you don't have to. One daily email with clear buy/hold/sell signals and the reasoning behind them. No jargon, just guidance you can trust.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/logo.svg" sizes="32x32" />
      </head>
      <body className="antialiased">
        <AppHeader
          rightSlot={
            <Button asChild size="sm" className="font-semibold px-4">
              <Link href="/signals">Dashboard</Link>
            </Button>
          }
        />
        <AppProviders>{children}</AppProviders>
        <Footer />
      </body>
    </html>
  );
}
