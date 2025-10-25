/**
 * Value Props Component
 * Four key benefits presented as cards
 */

export default function ValueProps() {
  const props = [
    {
      title: 'Clarity',
      description: 'Signals explained in plain English.',
      delay: '0ms'
    },
    {
      title: 'Coverage',
      description: 'Four core markets in one view.',
      delay: '100ms'
    },
    {
      title: 'Confidence Score',
      description: 'Each setup scored from 0–100.',
      delay: '200ms'
    },
    {
      title: 'Inbox Alerts',
      description: 'Strong signals delivered to your email.',
      delay: '300ms'
    }
  ]

  return (
    <section className="py-20 px-4">
      <div className="container-app">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
          {props.map((prop) => (
            <div
              key={prop.title}
              className="card p-6 animate-slide-up"
              style={{animationDelay: prop.delay}}
            >
              <h3 className="text-lg font-semibold mb-2 text-foreground-secondary">
                {prop.title}
              </h3>
              <p className="text-sm text-foreground-muted">
                {prop.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
