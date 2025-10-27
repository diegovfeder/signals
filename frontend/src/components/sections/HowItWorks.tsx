/**
 * How It Works Component
 * Three-step process explanation
 */

export default function HowItWorks() {
  const steps = [
    {
      number: "1",
      title: "We Analyze",
      description: "Fetch prices and compute RSI + EMA.",
      delay: "0ms",
    },
    {
      number: "2",
      title: "We Score",
      description: "Turn conditions into a 0–100 signal.",
      delay: "100ms",
    },
    {
      number: "3",
      title: "You Decide",
      description: "Open the dashboard or act from your inbox.",
      delay: "200ms",
    },
  ];

  return (
    <section className="py-16 px-4">
      <div className="container-app">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 text-foreground-secondary animate-fade-in">
            How It Works
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {steps.map((step) => (
              <div
                key={step.number}
                className="text-center animate-slide-up"
                style={{ animationDelay: step.delay }}
              >
                <div className="w-12 h-12 rounded-full bg-background-tertiary border border-border flex items-center justify-center mx-auto mb-4 text-foreground-secondary font-semibold">
                  {step.number}
                </div>
                <h3 className="text-lg font-semibold mb-2 text-foreground-secondary">
                  {step.title}
                </h3>
                <p className="text-sm text-foreground-muted">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
