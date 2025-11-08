import "./globals.css";

import type { Metadata } from "next";

import AppHeader from "@/components/layout/AppHeader";
import { Button } from "@/components/ui/button";

import { AppProviders } from "./providers";
import Footer from "@/components/sections/Footer";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Trading Signals - Automated Technical Analysis",
  description:
    "Automated trading signals for crypto and stocks based on proven technical indicators. Get BUY/SELL alerts without the guesswork.",
  keywords: [
    "trading signals",
    "technical analysis",
    "crypto",
    "stocks",
    "RSI",
    "MACD",
  ],
  authors: [{ name: "Diego Feder" }, { name: "Caue Feder" }],
  openGraph: {
    title: "Trading Signals - Automated Technical Analysis",
    description:
      "Get automated BUY/SELL signals for Bitcoin, Ethereum, and Tesla.",
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
