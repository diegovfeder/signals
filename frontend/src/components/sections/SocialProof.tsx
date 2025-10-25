/**
 * Social Proof Component
 * Transparency statement and disclaimer
 */

export default function SocialProof() {
  return (
    <section className="py-20 px-4">
      <div className="container-app">
        <div className="max-w-2xl mx-auto text-center animate-fade-in">
          <p className="text-lg text-foreground-secondary mb-4">
            We're shipping openly during MVP testing. No paywall while we learn together.
          </p>
          <p className="text-sm text-muted">
            This is not financial advice.
          </p>
        </div>
      </div>
    </section>
  )
}
