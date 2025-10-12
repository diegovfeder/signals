/**
 * Landing Page
 *
 * Main entry point with hero section, how it works, live signals, and email signup.
 */

import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="py-20 px-4 bg-gradient-to-b from-blue-50 to-white">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold mb-6 text-gray-900">
            Automated Trading Signals
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Get BUY/SELL alerts for crypto and stocks based on proven technical indicators.
            No charts. No confusion. Just clear signals.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/dashboard"
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              View Live Signals
            </Link>
            <button className="px-8 py-3 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition">
              Get Email Alerts
            </button>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {/* TODO: Add HowItWorks component */}
            <div className="p-6 border rounded-lg">
              <h3 className="text-xl font-semibold mb-3">1. We Analyze</h3>
              <p className="text-gray-600">
                Our system tracks 3 assets (BTC, ETH, TSLA) and calculates RSI + MACD indicators every hour.
              </p>
            </div>
            <div className="p-6 border rounded-lg">
              <h3 className="text-xl font-semibold mb-3">2. Signals Generated</h3>
              <p className="text-gray-600">
                When indicators align, we generate BUY/SELL signals with confidence scores (0-100).
              </p>
            </div>
            <div className="p-6 border rounded-lg">
              <h3 className="text-xl font-semibold mb-3">3. You Decide</h3>
              <p className="text-gray-600">
                Check the dashboard or get email alerts. Plain English explanations included.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 bg-gray-900 text-white text-center">
        <p>Trading Signals MVP - Built by Diego Feder</p>
      </footer>
    </main>
  );
}
