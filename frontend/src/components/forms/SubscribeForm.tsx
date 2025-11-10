"use client";

import { useState, type FormEvent } from "react";
import { useMutation } from "@tanstack/react-query";
import { usePostHog } from "posthog-js/react";
import { z } from "zod";
import { X, Maximize2, CheckCircle2, Mail } from "lucide-react";
import { api } from "@/lib/api-client";
import { useSubscriptionStore } from "@/stores/subscription-store";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

type SubscribeResponse = {
  message: string;
  email: string;
};

type SubscribeFormProps = {
  variant?: "card" | "inline";
  helperText?: string;
  buttonLabel?: string;
  placeholder?: string;
  successTitle?: string;
  className?: string;
};

const cx = (...classes: Array<string | undefined | false>) =>
  classes.filter(Boolean).join(" ");

const emailSchema = z
  .string()
  .trim()
  .min(1, "Email is required")
  .email("Enter a valid email address")
  .transform((value) => value.toLowerCase());

export function SubscribeForm({
  variant = "card",
  helperText = "Free during MVP. Unsubscribe anytime.",
  buttonLabel = "Get email alerts",
  placeholder = "you@email.com",
  successTitle = "Check your email!",
  className,
}: SubscribeFormProps) {
  const [email, setEmail] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const subscribedEmail = useSubscriptionStore((state) => state.email);
  const setSubscribedEmail = useSubscriptionStore((state) => state.setEmail);
  const isMinimized = useSubscriptionStore((state) => state.isMinimized);
  const setIsMinimized = useSubscriptionStore((state) => state.setIsMinimized);
  const posthog = usePostHog();

  const handleMinimize = () => {
    if (showSubscribedState) {
      // Only animate when user has subscribed
      setIsAnimating(true);
      setTimeout(() => {
        setIsMinimized(true);
        setIsAnimating(false);
      }, 500); // Match animation duration
    } else {
      setIsMinimized(true);
    }
  };

  const apiBase =
    typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL
      ? process.env.NEXT_PUBLIC_API_URL
      : "http://localhost:8000";

  const { mutate, isPending, reset } = useMutation({
    mutationFn: async (payload: { email: string }) =>
      api.post<SubscribeResponse>("/api/subscribe", payload),
    onSuccess: (response) => {
      setEmail("");
      setSubscribedEmail(response.email);
      setSuccessMessage(response.message);
      setFormError(null);
    },
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const parsed = emailSchema.safeParse(email);
    if (!parsed.success) {
      setFormError(
        parsed.error.issues[0]?.message ?? "Enter a valid email address",
      );
      return;
    }

    const normalizedEmail = parsed.data;
    setFormError(null);

    // Track subscription attempt with PostHog
    posthog.capture("subscribe_clicked", {
      email_domain: normalizedEmail.split("@")[1],
      variant,
    });

    mutate(
      { email: normalizedEmail },
      {
        onError: (mutationError) => {
          if (mutationError instanceof Error) {
            setFormError(mutationError.message);
          } else {
            setFormError("Failed to subscribe. Please try again.");
          }
        },
      },
    );
  };

  const showCardChrome = variant === "card";
  const showSubscribedState = Boolean(subscribedEmail);
  const normalizedApiBase = apiBase.replace(/\/$/, "");
  // const unsubscribeExample = `${normalizedApiBase}/api/subscribe/unsubscribe/{token}`;

  // Show minimized state
  if (isMinimized) {
    return (
      <div className={cx("flex justify-center", className)}>
        <Button
          onClick={() => setIsMinimized(false)}
          variant="outline"
          size="lg"
          className="gap-2 px-6 cursor-pointer"
        >
          <Maximize2 className="h-5 w-5" />
          Email alerts
        </Button>
      </div>
    );
  }

  return (
    <div
      className={cx(
        showCardChrome
          ? "card p-8 flex flex-col gap-4 text-left relative max-w-2xl mx-auto"
          : "flex flex-col gap-3 relative max-w-2xl mx-auto",
        className,
      )}
      style={
        isAnimating
          ? {
              animation: "slideDown 0.5s ease-in-out forwards",
            }
          : undefined
      }
    >
      {/* Close/Minimize button */}
      <Button
        onClick={handleMinimize}
        variant="ghost"
        size="sm"
        className="absolute top-2 right-2 size-6 p-0 transition-colors hover:bg-accent cursor-pointer"
        aria-label="Minimize"
      >
        <X className="h-4 w-4" />
      </Button>

      {!showSubscribedState && (
        <div>
          <p className="text-base text-foreground-muted">
            Get the next BUY/SELL signal in your inbox.
          </p>
        </div>
      )}

      {!showSubscribedState && (
        <form
          onSubmit={handleSubmit}
          className="flex flex-col sm:flex-row gap-3"
          noValidate
        >
          <Input
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder={placeholder}
            aria-invalid={Boolean(formError)}
            className="flex-1"
          />
          <Button
            type="submit"
            loading={isPending}
            className="whitespace-nowrap cursor-pointer"
          >
            {buttonLabel}
          </Button>
        </form>
      )}

      {showSubscribedState && (
        <div className="space-y-4 animate-slide-up">
          <div className="rounded-xl border border-success/30 bg-success/5 px-4 py-3 text-sm text-success">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle2 className="h-5 w-5" />
              <p className="font-medium">{successTitle}</p>
            </div>
            <p className="text-foreground mt-2">
              {successMessage ||
                "Subscription pending confirmation. Please check your email."}
            </p>
            <p className="text-foreground-muted mt-2 text-sm">
              Subscribed as&nbsp;
              <span className="font-mono text-foreground">
                {subscribedEmail}
              </span>
            </p>
          </div>
          <div className="rounded-lg border border-blue-500/30 bg-blue-500/5 px-4 py-3 text-sm text-foreground-muted">
            <div className="flex items-center gap-2 mb-2">
              <Mail className="h-5 w-5 text-foreground" />
              <p className="font-medium text-foreground">Next steps:</p>
            </div>
            <ol className="list-decimal list-inside space-y-1">
              <li>Check your inbox for a confirmation email</li>
              <li>Click the confirmation link to activate your subscription</li>
              <li>
                Check spam folder if you don&apos;t see it within a few minutes
              </li>
            </ol>
          </div>
          <div className="flex justify-center">
            <Button
              type="button"
              variant="link"
              size="sm"
              className="text-sm text-foreground hover:text-white p-0 h-auto cursor-pointer"
              onClick={() => {
                setSubscribedEmail(null);
                setSuccessMessage(null);
                reset();
                setFormError(null);
              }}
            >
              Use a different email
            </Button>
          </div>
        </div>
      )}

      {!showSubscribedState && !formError && (
        <p className="text-sm text-foreground-muted">{helperText}</p>
      )}

      {!showSubscribedState && formError && (
        <p className="text-sm text-red-400 font-medium">{formError}</p>
      )}
    </div>
  );
}
