/**
 * Dashboard Page
 *
 * Display live trading signals for all tracked symbols (BTC-USD, ETH-USD, TSLA).
 */

export default function Dashboard() {
  return (
    <main className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Trading Signals Dashboard</h1>

        {/* Tracked Symbols */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {/* TODO: Replace with actual SignalCard components */}
          <div className="bg-white p-6 rounded-lg shadow signal-card-buy">
            <h2 className="text-xl font-semibold mb-2">BTC-USD</h2>
            <div className="text-3xl font-bold text-buy mb-2">BUY</div>
            <div className="text-sm text-gray-600">Strength: 82/100</div>
            <ul className="mt-4 text-sm text-gray-700">
              <li>• RSI oversold (28)</li>
              <li>• MACD bullish crossover</li>
            </ul>
          </div>

          <div className="bg-white p-6 rounded-lg shadow signal-card-hold">
            <h2 className="text-xl font-semibold mb-2">ETH-USD</h2>
            <div className="text-3xl font-bold text-neutral mb-2">HOLD</div>
            <div className="text-sm text-gray-600">Strength: 0/100</div>
            <ul className="mt-4 text-sm text-gray-700">
              <li>• No clear signal</li>
            </ul>
          </div>

          <div className="bg-white p-6 rounded-lg shadow signal-card-sell">
            <h2 className="text-xl font-semibold mb-2">TSLA</h2>
            <div className="text-3xl font-bold text-sell mb-2">SELL</div>
            <div className="text-sm text-gray-600">Strength: 75/100</div>
            <ul className="mt-4 text-sm text-gray-700">
              <li>• RSI overbought (72)</li>
              <li>• MACD bearish trend</li>
            </ul>
          </div>
        </div>

        {/* TODO: Add SignalList component with table view */}
        {/* TODO: Add PerformanceMetrics component */}
      </div>
    </main>
  );
}
