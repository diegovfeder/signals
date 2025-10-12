/**
 * Symbol Detail Page
 *
 * Detailed view of a specific symbol with price charts, indicators, and signal history.
 */

export default function SignalDetail({
  params,
}: {
  params: { symbol: string };
}) {
  const { symbol } = params;

  return (
    <main className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">{symbol} - Signal Detail</h1>

        {/* Current Signal */}
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-semibold mb-4">Current Signal</h2>
          {/* TODO: Replace with SignalCard component */}
          <div className="text-center">
            <div className="text-4xl font-bold text-buy mb-2">BUY</div>
            <div className="text-lg text-gray-600">Strength: 82/100</div>
            <div className="mt-4 text-gray-700">
              <p className="mb-2">Reasoning:</p>
              <ul className="text-left max-w-md mx-auto">
                <li>• RSI oversold (28) - potential buying opportunity</li>
                <li>• MACD bullish crossover - upward momentum</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Price Chart */}
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-semibold mb-4">Price Chart</h2>
          {/* TODO: Add PriceChart component with Chart.js */}
          <div className="h-64 flex items-center justify-center bg-gray-100 rounded">
            <p className="text-gray-500">Candlestick chart placeholder</p>
          </div>
        </div>

        {/* Indicators */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">RSI Indicator</h3>
            {/* TODO: Add IndicatorChart component */}
            <div className="h-48 flex items-center justify-center bg-gray-100 rounded">
              <p className="text-gray-500">RSI chart placeholder</p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">MACD Indicator</h3>
            {/* TODO: Add IndicatorChart component */}
            <div className="h-48 flex items-center justify-center bg-gray-100 rounded">
              <p className="text-gray-500">MACD chart placeholder</p>
            </div>
          </div>
        </div>

        {/* Signal History */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Signal History (Last 30 Days)</h2>
          {/* TODO: Add SignalList component */}
          <div className="text-gray-500 text-center py-8">
            Signal history table placeholder
          </div>
        </div>
      </div>
    </main>
  );
}
