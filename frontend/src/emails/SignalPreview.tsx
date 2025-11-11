import {
  Body,
  Container,
  Head,
  Heading,
  Html,
  Preview,
  Section,
  Text,
} from "@react-email/components";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { formatPrice } from "@/lib/utils/formatters";
import { Button } from "@/components/ui/button";

const previewSignal = {
  symbol: "BTC-USD",
  signalType: "BUY" as const,
  price: 48230.12,
  strength: 82,
  updatedAt: new Date("2025-02-12T12:15:00Z"),
  summary: "Momentum and moving averages are aligned after a higher low.",
  points: [
    "RSI reclaimed 55 after cooling off from overbought levels.",
    "12/26 EMA crossover stays intact with widening spread.",
    "Price continues to respect the 50-day support channel.",
  ],
};

const previewText = `${previewSignal.symbol} ${previewSignal.signalType} signal — strength ${previewSignal.strength}%`;

const strengthLabel = previewSignal.strength >= 70 ? "Strong" : "Moderate";

const formatUpdated = (date: Date) =>
  new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short",
  }).format(date);

export interface SignalPreviewEmailContentProps {
  className?: string;
}

export function SignalPreviewEmailContent({
  className,
}: SignalPreviewEmailContentProps) {
  return (
    <Section
      aria-labelledby="signal-preview-email-heading"
      className={cn(
        "rounded-2xl border border-border bg-card/95 p-6 shadow-lg backdrop-blur",
        className,
      )}
    >
      <div className="flex flex-col gap-4">
        <div className="flex items-start justify-between gap-3">
          <Heading
            id="signal-preview-email-heading"
            className="text-lg font-semibold text-foreground"
          >
            Daily signal recap
          </Heading>
        </div>

        <Text className="text-sm text-muted-foreground">
          {previewSignal.summary}
        </Text>

        <Section className="rounded-xl border border-border/60 bg-muted/40 p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Highlighted signal
          </p>
          <p className="mt-2 text-base font-semibold text-foreground">
            {previewSignal.symbol} · {previewSignal.signalType}
          </p>
          <p className="text-sm text-muted-foreground">
            {formatPrice(previewSignal.price)} · {strengthLabel} confidence
          </p>
          <p className="mt-2 text-xs text-muted-foreground">
            Updated {formatUpdated(previewSignal.updatedAt)}
          </p>
          <ul className="mt-4 space-y-2 text-sm text-muted-foreground/90">
            {previewSignal.points.map((point, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="mt-0.5 text-ring">•</span>
                <span>{point}</span>
              </li>
            ))}
          </ul>
        </Section>

        <Button asChild size="lg" className="text-center">
          <Link
            href="/signals/BTC-USD"
            className="mt-2 w-full justify-center px-5 py-2.5 text-sm font-semibold"
          >
            Open dashboard
          </Link>
        </Button>

        <Text className="text-xs leading-5 text-muted-foreground/80">
          Alerts are powered by Resend. You can manage your notification
          preferences or unsubscribe at any time from your account settings.
        </Text>
      </div>
    </Section>
  );
}

export default function SignalPreviewEmail() {
  return (
    <Html>
      <Head />
      <Preview>{previewText}</Preview>
      <Body className="bg-background px-4 py-8">
        <Container className="bg-transparent">
          <SignalPreviewEmailContent />
        </Container>
      </Body>
    </Html>
  );
}
