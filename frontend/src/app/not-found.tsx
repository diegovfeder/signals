import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center max-w-2xl">
        {/* Animated 404 */}
        <div className="relative mb-8">
          <h1 className="text-[12rem] font-bold leading-none bg-gradient-to-br from-primary via-ring to-primary bg-clip-text text-transparent animate-pulse">
            404
          </h1>
          <div className="absolute inset-0 blur-2xl opacity-40 bg-gradient-to-br from-primary/60 via-ring/60 to-primary/60" />
        </div>

        {/* Message */}
        <h2 className="text-3xl font-bold text-foreground mb-4">
          Signal Not Found
        </h2>
        <p className="text-lg text-muted-foreground mb-8 max-w-md mx-auto">
          No signal detected at this location. The market moves fast—this page
          may have been delisted or the URL might be incorrect.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link
            href="/signals"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-gradient-to-r from-primary/80 via-primary to-primary/80 border border-primary text-primary-foreground font-semibold hover:shadow-lg hover:shadow-primary/30 transition-all duration-300"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
              />
            </svg>
            View Signals
          </Link>
        </div>

        {/* Decorative Elements */}
        <div className="mt-16 flex justify-center gap-2">
          <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
          <div className="w-2 h-2 rounded-full bg-ring animate-pulse delay-150" />
          <div className="w-2 h-2 rounded-full bg-primary animate-pulse delay-300" />
        </div>
      </div>
    </div>
  );
}
