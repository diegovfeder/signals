import type { Metadata } from 'next';
import './globals.css';
import { AppProviders } from './providers';

export const metadata: Metadata = {
  title: 'Trading Signals - Automated Technical Analysis',
  description: 'Automated trading signals for crypto and stocks based on proven technical indicators. Get BUY/SELL alerts without the guesswork.',
  keywords: ['trading signals', 'technical analysis', 'crypto', 'stocks', 'RSI', 'MACD'],
  authors: [{ name: 'Diego Feder' }],
  openGraph: {
    title: 'Trading Signals - Automated Technical Analysis',
    description: 'Get automated BUY/SELL signals for Bitcoin, Ethereum, and Tesla.',
    type: 'website',
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
        <script
          async
          crossOrigin="anonymous"
          src="https://tweakcn.com/live-preview.min.js"
        />
      </head>
      <body className="antialiased">
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
