export function DailySignalsBadge() {
  return (
    <div className="mt-12 text-center animate-fade-in">
      <div className="inline-flex items-center gap-2 card px-4 py-2">
        <span className="status-live" />
        <span className="text-sm text-muted-foreground">
          Daily signals at 10 PM UTC
        </span>
      </div>
    </div>
  );
}
