/**
 * Confirmation email template for new Signals subscribers
 */

import { buildEmailHTML } from './theme';
import type { EmailTemplate } from './types';
import { TEMPLATE_KEYS } from './types';

export const confirmationEmailTemplate: EmailTemplate = {
  name: TEMPLATE_KEYS.CONFIRMATION,
  alias: 'confirmation',
  subject: 'Confirm your Signals subscription',
  html: buildEmailHTML({
    eyebrow: 'Signals',
    title: 'Welcome to Signals',
    intro:
      "You're almost ready to receive automated trading intelligence the moment it ships.",
    messageLines: [
      'Confirming your email tells us we can securely deliver market-ready signals straight to your inbox.',
      "Hit confirm and we'll activate notifications aligned with your dashboard preferences.",
    ],
    buttonLabel: 'Confirm email',
    buttonUrl: '{{{CONFIRMATION_URL}}}',
    footnote:
      "If you didn't sign up for Signals, you can safely ignore this email.",
    highlightLabel: 'Status',
    highlightBody: 'Awaiting confirmation — link valid for 48 hours',
  }),
  text: `Welcome to Signals!

Thanks for subscribing to automated trading signals. We'll send you notifications when our analysis identifies high-confidence opportunities.

Click this link to confirm your email address:
{{{CONFIRMATION_URL}}}

If you didn't sign up for Signals, you can safely ignore this email.

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
