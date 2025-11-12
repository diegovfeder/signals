/**
 * Reactivation email template for returning Signals subscribers
 */

import { buildEmailHTML } from './theme';
import type { EmailTemplate } from './types';
import { TEMPLATE_KEYS } from './types';

export const reactivationEmailTemplate: EmailTemplate = {
  name: TEMPLATE_KEYS.REACTIVATION,
  alias: 'reactivation',
  subject: 'Welcome back to Signals',
  html: buildEmailHTML({
    eyebrow: 'Signals',
    title: 'Welcome back to Signals',
    intro:
      'We saved your signal preferences. Reactivate to resume curated alerts with zero onboarding friction.',
    messageLines: [
      'Reconfirming verifies that we can resume delivery of the watchlists and guardrails you configured.',
      'Loved something in the dashboard recently? Reactivation keeps your notifications in sync.',
    ],
    buttonLabel: 'Confirm reactivation',
    buttonUrl: '{{{CONFIRMATION_URL}}}',
    footnote:
      "If you didn't request this, you can safely ignore this email.",
    highlightLabel: 'Status',
    highlightBody: 'Reactivation pending — link valid for 48 hours',
  }),
  text: `Welcome back to Signals!

You're resubscribing to automated trading signals. We'll send you notifications when our analysis identifies high-confidence opportunities.

Click this link to confirm your email address:
{{{CONFIRMATION_URL}}}

If you didn't request this, you can safely ignore this email.

---
Signals - Automated market signals you can actually read`,
  variables: [
    {
      key: 'CONFIRMATION_URL',
      type: 'string',
      fallbackValue: 'https://signals-dvf.vercel.app/subscribe/confirm/TOKEN',
    },
  ],
};
