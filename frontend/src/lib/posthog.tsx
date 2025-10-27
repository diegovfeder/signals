"use client";

import { useEffect } from "react";
import posthog from "posthog-js";
import { PostHogProvider as PHProvider } from "posthog-js/react";

export function PostHogProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY as string, {
      api_host:
        process.env.NEXT_PUBLIC_POSTHOG_HOST || "https://app.posthog.com",
      person_profiles: "identified_only", // Only create profiles for identified users
      defaults: "2025-05-24", // Use latest defaults
      capture_pageview: true, // Automatic pageview tracking
      capture_pageleave: true, // Track when users leave
      debug: true, // Enable debug logs to see events being sent
      loaded: (posthog) => {
        // Temporarily ENABLED in development for testing
        // if (process.env.NODE_ENV === 'development') {
        //   posthog.opt_out_capturing()
        //   console.log('PostHog disabled in development')
        // }
        console.log(
          "PostHog initialized and ready to capture events",
          posthog._isIdentified()
        );
      },
    });
  }, []);

  return <PHProvider client={posthog}>{children}</PHProvider>;
}
