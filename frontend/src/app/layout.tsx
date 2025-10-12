import type { Metadata } from 'next';
import './globals.css';

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
      <body className="antialiased bg-gray-50 text-gray-900">
        {children}
      </body>
    </html>
  );
}
