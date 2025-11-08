# Frontend (Next.js 16 + Bun)

Public marketing site + dashboard for Signals.

## Quick Start

```bash
cd frontend
bun install            # Install deps
cp .env.example .env.local
# edit NEXT_PUBLIC_API_URL=http://localhost:8000

bun run dev            # http://localhost:3000
```

## Available Scripts

- `bun run dev` – Start local dev server (App Router, hot reload).
- `bun run build` – Production build.
- `bun run start` – Serve the production build.
- `bun run lint` – ESLint (Next.js config).
- `bun run type-check` – TypeScript only.

## Structure

```
frontend/
├── src/app/            # App Router pages (/, /dashboard, /signals/[symbol], /admin/*)
├── src/components/     # Shared UI (forms, cards, layout)
├── src/lib/            # Data hooks, API helpers, constants
├── public/             # Static assets
└── README.md           # This file
```

## Environment Variables

Create `.env.local` from `.env.example` and set:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_POSTHOG_KEY=phc_...    # optional analytics
```

All vars prefixed with `NEXT_PUBLIC_` are exposed to the browser.

## Data Fetching

- Uses lightweight hooks in `src/lib/hooks`. Task seed exists to migrate to TanStack Query for caching/polling.
- `NEXT_PUBLIC_API_URL` controls which backend the hooks call.

## Styling & Tooling

- TailwindCSS 4 for design tokens.
- Shared form components (`src/components/forms/SubscribeForm.tsx`).
- Chart.js + `react-chartjs-2` for signal detail charts.

## Manual Validation

After changes:
1. `bun run lint && bun run type-check`.
2. Load `/`, `/dashboard`, `/signals/BTC-USD`, `/admin/subscribers` to confirm data loads and styles render.

For deployment, push to `main` (Vercel auto-builds via GitHub).
