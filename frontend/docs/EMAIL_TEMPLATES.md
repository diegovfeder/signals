# Email Templates Management

This document describes how email templates are managed in the Signals frontend and synced to Resend.

## Overview

Email templates are stored as TypeScript files in the frontend codebase and synced to Resend's template system via API. This approach provides:

- **Version control**: Templates are tracked in git alongside code
- **Type safety**: TypeScript ensures template structure is valid
- **Reusability**: Shared theme and HTML builder functions
- **Single source of truth**: Templates live in code, not just in Resend dashboard

## Directory Structure

```
frontend/src/lib/email-templates/
├── index.ts              # Template registry and exports
├── types.ts              # TypeScript type definitions
├── theme.ts              # Signals branded email theme and HTML builder
├── confirmation.ts       # New subscriber confirmation email
└── reactivation.ts       # Returning subscriber reactivation email

frontend/scripts/
└── sync-email-templates.ts   # CLI script to sync templates to Resend
```

## Template Structure

Each template follows this structure:

```typescript
import { buildEmailHTML } from './theme';
import type { EmailTemplate } from './types';
import { TEMPLATE_KEYS } from './types';

export const myTemplate: EmailTemplate = {
  name: TEMPLATE_KEYS.MY_TEMPLATE,  // Unique identifier
  alias: 'my-template',              // Optional short name
  subject: 'Email Subject',
  html: buildEmailHTML({             // Uses Signals branded theme
    eyebrow: 'Signals',
    title: 'Email Title',
    intro: 'Introduction paragraph',
    messageLines: ['Line 1', 'Line 2'],
    buttonLabel: 'Click Me',
    buttonUrl: '{{{DYNAMIC_URL}}}',  // Mustache syntax for variables
    footnote: 'Footer text',
    highlightLabel: 'Optional',
    highlightBody: 'Optional highlight box',
  }),
  text: `Plain text version...`,     // Plain text fallback
  variables: [                        // Template variables
    {
      key: 'DYNAMIC_URL',
      type: 'string',
      fallbackValue: 'https://example.com',
    },
  ],
};
```

## Template Variables

Templates support dynamic variables using Mustache syntax (`{{{VARIABLE_NAME}}}`):

- **Triple braces** (`{{{VAR}}}`) - No HTML escaping (use for URLs)
- **Double braces** (`{{VAR}}`) - HTML escaped (use for user content)

Example:
```html
<a href="{{{CONFIRMATION_URL}}}">Confirm</a>
<p>Hello, {{FIRST_NAME}}!</p>
```

Define variables in the template:
```typescript
variables: [
  {
    key: 'CONFIRMATION_URL',
    type: 'string',
    fallbackValue: 'https://signals-dvf.vercel.app/subscribe/confirm/TOKEN',
  },
  {
    key: 'FIRST_NAME',
    type: 'string',
    // No fallback means the variable is required when sending
  },
]
```

## Syncing Templates to Resend

### Basic Usage (Smart Sync)

```bash
cd frontend
bun run sync-templates
```

To immediately publish the latest drafts (so Resend starts serving them), run:

```bash
cd frontend
bun run sync-templates:publish    # wraps --publish flag
```

**Smart sync automatically**:
1. 🔍 Checks what templates exist in Resend
2. ✅ Creates new templates that don't exist
3. 🔄 Updates existing templates with your latest changes
4. ⚡ Just works - no manual intervention needed!

Perfect for:
- Daily development workflow
- After updating template HTML/styling
- CI/CD pipelines (idempotent)

### Advanced Options

**Sync specific template:**
```bash
bun run scripts/sync-email-templates.ts --only signals-notification
```

**List templates in Resend:**
```bash
bun run sync-templates:list
```

**Create-only mode (skip existing):**
```bash
bun run scripts/sync-email-templates.ts --create-only
```

**Available flags:**
- `--only <template-name>` - Sync only a specific template (by name or alias)
- `--create-only` - Only create new templates, skip existing ones
- `--list` - List all templates currently in Resend
- `--publish` - Publish templates immediately after creation/update (built into `bun run sync-templates:publish`)

### Example Output

**First time sync (creates templates):**
```
🔍 Checking existing templates in Resend...

🚀 Syncing 3 email template(s)...

🔄 Smart mode: Will create new and update existing templates

✅ signals-confirmation
   Created (ID: 49a3999c-0ce1-4ea6-ab68-afcd6dc2e794)
   Subject: Confirm your Signals subscription
   Variables: CONFIRMATION_URL

📣 signals-confirmation
   Published latest draft (ID: 49a3999c-0ce1-4ea6-ab68-afcd6dc2e794)

✅ signals-reactivation
   Created (ID: 8b2f888a-1de2-5fb7-bc79-bfde7ed3f905)
   Subject: Welcome back to Signals
   Variables: CONFIRMATION_URL

📣 signals-reactivation
   Published latest draft (ID: 8b2f888a-1de2-5fb7-bc79-bfde7ed3f905)

✅ signals-notification
   Created (ID: 2e342d42-8e43-45b6-90b9-c2fa6d8ab573)
   Subject: {{{SYMBOL}}} Signal: {{{SIGNAL_TYPE}}}
   Variables: SYMBOL, SIGNAL_TYPE, STRENGTH, PRICE, TIMESTAMP, REASONING_HTML, REASONING_TEXT, UNSUBSCRIBE_URL

📣 signals-notification
   Published latest draft (ID: 2e342d42-8e43-45b6-90b9-c2fa6d8ab573)

────────────────────────────────────────────────────────────
✨ Sync complete: 3 created, 0 updated, 0 skipped, 3 published, 0 error(s)
```

**Subsequent runs (updates existing templates):**
```
🔍 Checking existing templates in Resend...

🚀 Syncing 3 email template(s)...

🔄 Smart mode: Will create new and update existing templates

🔄 signals-confirmation
   Updated (ID: 49a3999c-0ce1-4ea6-ab68-afcd6dc2e794)
   Subject: Confirm your Signals subscription
   Variables: CONFIRMATION_URL

📣 signals-confirmation
   Published latest draft (ID: 49a3999c-0ce1-4ea6-ab68-afcd6dc2e794)

🔄 signals-reactivation
   Updated (ID: 8b2f888a-1de2-5fb7-bc79-bfde7ed3f905)
   Subject: Welcome back to Signals
   Variables: CONFIRMATION_URL

📣 signals-reactivation
   Published latest draft (ID: 8b2f888a-1de2-5fb7-bc79-bfde7ed3f905)

🔄 signals-notification
   Updated (ID: 2e342d42-8e43-45b6-90b9-c2fa6d8ab573)
   Subject: {{{SYMBOL}}} Signal: {{{SIGNAL_TYPE}}}
   Variables: SYMBOL, SIGNAL_TYPE, STRENGTH, PRICE, TIMESTAMP, REASONING_HTML, REASONING_TEXT, UNSUBSCRIBE_URL

────────────────────────────────────────────────────────────
📣 signals-notification
   Published latest draft (ID: 2e342d42-8e43-45b6-90b9-c2fa6d8ab573)

────────────────────────────────────────────────────────────
✨ Sync complete: 0 created, 3 updated, 0 skipped, 3 published, 0 error(s)
```

## Current Templates

### 1. Confirmation Email (`signals-confirmation`)

**Purpose**: Sent to new subscribers to verify their email address

**Variables**:
- `CONFIRMATION_URL` (string) - Link to confirm subscription

**Subject**: "Confirm your Signals subscription"

**Used by**: Backend `send_confirmation_email()` function

### 2. Reactivation Email (`signals-reactivation`)

**Purpose**: Sent to returning subscribers who resubscribe

**Variables**:
- `CONFIRMATION_URL` (string) - Link to reconfirm subscription

**Subject**: "Welcome back to Signals"

**Used by**: Backend `send_reactivation_email()` function

## Adding a New Template

1. **Create the template file**:

```typescript
// src/lib/email-templates/signal-notification.ts
import { buildEmailHTML } from './theme';
import type { EmailTemplate } from './types';
import { TEMPLATE_KEYS } from './types';

export const signalNotificationTemplate: EmailTemplate = {
  name: TEMPLATE_KEYS.SIGNAL_NOTIFICATION,
  alias: 'signal-notification',
  subject: 'New signal detected: {{{SYMBOL}}}',
  html: buildEmailHTML({
    eyebrow: 'Signal Alert',
    title: '{{{SIGNAL_TYPE}}} signal for {{{SYMBOL}}}',
    intro: 'Our analysis identified a high-confidence trading opportunity.',
    messageLines: [
      'Signal strength: {{{STRENGTH}}}%',
      'Timeframe: {{{TIMEFRAME}}}',
      '{{{REASONING}}}',
    ],
    buttonLabel: 'View signal details',
    buttonUrl: '{{{SIGNAL_URL}}}',
    footnote: 'Manage your signal preferences in the dashboard.',
  }),
  variables: [
    { key: 'SYMBOL', type: 'string', fallbackValue: 'UNKNOWN' },
    { key: 'SIGNAL_TYPE', type: 'string', fallbackValue: 'BUY' },
    { key: 'STRENGTH', type: 'number', fallbackValue: 75 },
    { key: 'TIMEFRAME', type: 'string', fallbackValue: '1d' },
    { key: 'REASONING', type: 'string', fallbackValue: 'No reason provided' },
    { key: 'SIGNAL_URL', type: 'string' },
  ],
};
```

2. **Add to template keys**:

```typescript
// src/lib/email-templates/types.ts
export const TEMPLATE_KEYS = {
  CONFIRMATION: 'signals-confirmation',
  REACTIVATION: 'signals-reactivation',
  SIGNAL_NOTIFICATION: 'signals-notification', // Add this
} as const;
```

3. **Export from index**:

```typescript
// src/lib/email-templates/index.ts
import { signalNotificationTemplate } from './signal-notification';

export const EMAIL_TEMPLATES: EmailTemplate[] = [
  confirmationEmailTemplate,
  reactivationEmailTemplate,
  signalNotificationTemplate, // Add this
];

export { signalNotificationTemplate } from './signal-notification';
```

4. **Sync to Resend**:

```bash
bun run sync-templates
```

## Email Theme

All templates use the Signals brand theme defined in `theme.ts`:

```typescript
export const EMAIL_THEME = {
  background: '#05090a',      // Dark background
  card: '#0f1512',            // Card background
  cardBorder: '#1b2b23',      // Card border
  divider: '#1f3128',         // Divider lines
  badgeBg: '#13231b',         // Badge background
  badgeText: '#7ef2bf',       // Badge text (accent green)
  textPrimary: '#e2e8f0',     // Primary text (light)
  textSecondary: '#9da7b3',   // Secondary text (muted)
  muted: '#7b8a83',           // Muted text
  primary: '#0c8f58',         // Primary brand color
  buttonShadow: '0 12px 30px rgba(20, 184, 124, 0.25)', // Button glow
};
```

The `buildEmailHTML()` function creates a consistent layout:
- Branded header badge
- Responsive card design
- Gradient button with shadow
- Optional highlight box
- Footer with fallback URL
- Mobile-friendly table layout

## Testing Templates Locally

### Preview in Browser

Create a simple test page:

```typescript
// src/app/test-email/page.tsx
import { confirmationEmailTemplate } from '@/lib/email-templates';

export default function TestEmailPage() {
  const html = confirmationEmailTemplate.html.replace(
    '{{{CONFIRMATION_URL}}}',
    'http://localhost:3000/subscribe/confirm/TEST_TOKEN'
  );

  return <div dangerouslySetInnerHTML={{ __html: html }} />;
}
```

Visit: `http://localhost:3000/test-email`

### Send Test Email via Resend Dashboard

1. Sync templates: `bun run sync-templates` (and `bun run sync-templates:publish` if you want to send tests right away)
2. Go to Resend dashboard → Templates
3. Find your template
4. Click "Send test email"
5. Fill in variable values
6. Send to your test email

## Environment Variables

Required in `.env.local`:

```bash
RESEND_API_KEY=re_xxxxxxxxx
```

Optional (for template defaults):
```bash
RESEND_FROM_EMAIL=onboarding@resend.dev
APP_BASE_URL=https://signals-dvf.vercel.app
```

## Backend Integration

Both the FastAPI backend and Prefect pipeline now send emails exclusively via
Resend templates. To keep things in sync:

1. Create/update drafts with `bun run sync-templates`, then publish via `bun run sync-templates:publish`.
2. Store the template IDs (confirmation, reactivation, notification) in code or environment variables.
3. Make sure the backend/pipeline use `resend>=2.19.0`, which supports template payloads, and send emails like this:

```python
params = {
    "from": from_email,
    "to": [to_email],
    "template": {
        "id": "eabb6a15-2d95-4c1d-afa7-944d63cd5b46",  # example
        "variables": {
            "CONFIRMATION_URL": confirmation_url,
        },
    },
}
resend.Emails.send(params)
```

No inline HTML helpers remain—everything routes through the shared template registry.

## Troubleshooting

### Template sync fails with "RESEND_API_KEY not found"

Ensure `.env.local` contains the API key:
```bash
echo "RESEND_API_KEY=re_xxxxxxxxx" >> frontend/.env.local
```

### Updating an existing template

**Just run the sync command!** The script automatically detects and updates existing templates:

```bash
# Edit your template in src/lib/email-templates/
# Then sync:
bun run sync-templates

# Or update just one:
bun run scripts/sync-email-templates.ts --only signals-confirmation

# Publish the updated draft so emails pick it up
bun run sync-templates:publish
```

**No need to delete!** The script uses Resend's update API to modify templates in-place, preserving template IDs.

### Adding a new template

After creating a new template in the codebase:

```bash
# Sync just the new template
bun run scripts/sync-email-templates.ts --only your-new-template-name

# Or sync all (will create new, update existing)
bun run sync-templates

# Publish the new template
bun run sync-templates:publish
```

The script is **fully idempotent** - safe to run anytime!

### Template sync succeeds but email doesn't send

1. Confirm you ran `bun run sync-templates:publish` (or published via Resend dashboard)
2. Verify sender email is verified in Resend
3. Check backend logs for Resend API errors
4. Verify you're using the correct `template_id` in Python code

### Variables not rendering in emails

- Use triple braces `{{{VAR}}}` for URLs (no escaping)
- Use double braces `{{VAR}}` for text content (HTML escaped)
- Ensure variable keys match exactly (case-sensitive)
- Check that Python code passes all required variables

### Email looks broken in Outlook

- Test in [Litmus](https://litmus.com) or [Email on Acid](https://www.emailonacid.com)
- Email clients have inconsistent CSS support
- Current templates use table-based layout for maximum compatibility

## Future Improvements

- [ ] Add signal notification template (#TODO)
- [ ] Support React components via `@react-email/components`
- [ ] Add email preview route for all templates
- [ ] Create GitHub Action to auto-sync on template changes
- [ ] Add visual regression testing for email rendering
- [ ] Support A/B testing different template variants

## Resources

- [Resend Templates Documentation](https://resend.com/docs/send-with-templates)
- [Resend API Reference](https://resend.com/docs/api-reference/templates/create-template)
- [Resend MCP Server](https://resend.com/docs/knowledge-base/mcp-server)
- [Email Template Best Practices](https://www.campaignmonitor.com/blog/email-marketing/best-practices-for-email-templates/)
