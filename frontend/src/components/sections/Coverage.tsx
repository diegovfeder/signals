/**
 * Coverage Component
 * Two asset tiles showing market coverage
 */

export default function Coverage() {
  const assets = [
    {
      symbol: 'BTC-USD',
      label: 'Crypto',
      color: 'text-primary',
      delay: '0ms'
    },
    {
      symbol: 'AAPL',
      label: 'Stock',
      color: 'text-success',
      delay: '100ms'
    }
  ]

  return (
    <section className="py-16 px-4 bg-background-secondary/50">
      <div className="container-app">
        <h2 className="text-3xl font-bold text-center mb-12 text-foreground-secondary animate-fade-in">
          Coverage
        </h2>

        <div className="grid grid-cols-2 gap-6 max-w-2xl mx-auto">
          {assets.map((asset) => (
            <div
              key={asset.symbol}
              className="card p-6 text-center animate-slide-up"
              style={{animationDelay: asset.delay}}
            >
              <div className={`text-2xl font-bold mb-2 ${asset.color}`}>
                {asset.symbol}
              </div>
              <div className="text-xs text-foreground-muted uppercase tracking-wider">
                {asset.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
