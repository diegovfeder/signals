# Email Templates

All Signals email templates stored as TypeScript files.

## Quick Start

### Sync templates to Resend

```bash
# Smart sync (creates new, updates existing drafts)
bun run sync-templates

# Sync + publish latest drafts (ready for Resend sends)
bun run sync-templates:publish

# List all templates in Resend
bun run sync-templates:list

# Sync only a specific template
bun run scripts/sync-email-templates.ts --only your-template-name
```

**The sync is smart**: It automatically creates new templates and updates existing ones. No flags needed!

### Add a new template

1. Create `my-template.ts` in this directory
2. Use `buildEmailHTML()` from `theme.ts` for consistent branding
3. Define variables using Mustache syntax: `{{{VARIABLE_NAME}}}`
4. Add template key to `types.ts` TEMPLATE_KEYS
5. Export from `index.ts`
6. Run `bun run sync-templates` (or `bun run scripts/sync-email-templates.ts --only my-template`) to create/update the draft
7. Run `bun run sync-templates:publish` to publish the latest draft so Resend uses it

## Template Files

- `types.ts` - TypeScript definitions
- `theme.ts` - Signals brand colors and HTML builder
- `confirmation.ts` - New subscriber confirmation
- `reactivation.ts` - Returning subscriber reactivation
- `index.ts` - Template registry

## Variables

Use **triple braces** for URLs (no escaping):
```html
<a href="{{{CONFIRMATION_URL}}}">Click here</a>
```

Use **double braces** for text (HTML escaped):
```html
<p>Hello, {{FIRST_NAME}}!</p>
```

Define in template:
```typescript
variables: [
  { key: 'CONFIRMATION_URL', type: 'string', fallbackValue: 'https://...' },
  { key: 'FIRST_NAME', type: 'string' }, // Required if no fallback
]
```

## Full Documentation

See `/frontend/EMAIL_TEMPLATES.md` for complete guide.
