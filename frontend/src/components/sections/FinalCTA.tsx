/**
 * Final CTA Component
 * Last conversion opportunity
 */

import Link from "next/link";

export default function FinalCTA() {
  return (
    <section className="py-16 px-4">
      <div className="container-app">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-4 text-foreground animate-fade-in">
            Start tracking signals today.
          </h2>
          <p className="text-lg text-foreground-muted mb-8 animate-fade-in">
            Free during MVP testing. No credit card.
          </p>
        </div>
      </div>
    </section>
  );
}
