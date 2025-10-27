"use client";

import { useState, type FormEvent } from "react";
import { useMutation } from "@tanstack/react-query";
import { usePostHog } from "posthog-js/react";
import { z } from "zod";
import { api } from "@/lib/api-client";
import { useSubscriptionStore } from "@/stores/subscription-store";

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
  successTitle = "You are on the list!",
  className,
}: SubscribeFormProps) {
  const [email, setEmail] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const subscribedEmail = useSubscriptionStore((state) => state.email);
  const setSubscribedEmail = useSubscriptionStore((state) => state.setEmail);
  const posthog = usePostHog();

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
      setFormError(null);
    },
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const parsed = emailSchema.safeParse(email);
    if (!parsed.success) {
      setFormError(
        parsed.error.issues[0]?.message ?? "Enter a valid email address"
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
      }
    );
  };

  const showCardChrome = variant === "card";
  const showSubscribedState = Boolean(subscribedEmail);
  const normalizedApiBase = apiBase.replace(/\/$/, "");
  const unsubscribeExample = `${normalizedApiBase}/api/subscribe/unsubscribe/{token}`;

  return (
    <div
      className={cx(
        showCardChrome
          ? "card p-6 flex flex-col gap-4 text-left"
          : "flex flex-col gap-3",
        className
      )}
    >
      {!showSubscribedState && (
        <div>
          <p className="text-sm text-foreground-muted">
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
          <input
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder={placeholder}
            className="flex-1 px-4 py-3 text-base bg-black/40 border border-white/10 rounded-xl focus:border-white/30 focus:bg-black/60 transition-colors"
            aria-invalid={Boolean(formError)}
          />
          <button
            type="submit"
            className="btn-primary whitespace-nowrap disabled:opacity-70 disabled:cursor-not-allowed cursor-pointer"
            disabled={isPending}
          >
            {isPending ? "Joining…" : buttonLabel}
          </button>
        </form>
      )}

      {showSubscribedState && (
        <div className="space-y-3">
          <div className="rounded-xl border border-success/30 bg-success/5 px-4 py-3 text-sm text-success">
            <p className="font-medium">{successTitle}</p>
            <p className="text-foreground-muted mt-1">
              Subscribed as{" "}
              <span className="font-mono text-foreground">
                {subscribedEmail}
              </span>
              .
            </p>
          </div>
          <p className="text-xs text-foreground-muted">
            Every alert email will include a one-click unsubscribe link:
            <br />
            <code className="code-block mt-2 block text-xs">
              {unsubscribeExample}
            </code>
            Keep this for reference until automated emails roll out.
          </p>
          <button
            type="button"
            className="text-xs text-foreground-muted underline hover:text-foreground transition-colors"
            onClick={() => {
              setSubscribedEmail(null);
              reset();
              setFormError(null);
            }}
          >
            Use a different email
          </button>
        </div>
      )}

      {!showSubscribedState && !formError && (
        <p className="text-xs text-foreground-muted">{helperText}</p>
      )}

      {!showSubscribedState && formError && (
        <p className="text-xs text-danger">{formError}</p>
      )}
    </div>
  );
}
