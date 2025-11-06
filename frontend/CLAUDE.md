# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Frontend Overview

This is the **Next.js 16 frontend** for the Trading Signals project. It displays live trading signals fetched from the FastAPI backend and allows users to subscribe to email notifications.

**Tech Stack**:
- Next.js 16.0 (App Router)
- React 19.2
- TypeScript 5.6
- TailwindCSS 4.0
- TanStack React Query 5.90 (data fetching & caching)
- Zustand 4.5 (client state management)
- Chart.js 4.4 + react-chartjs-2 (data visualization)
- PostHog (analytics)

**Package Manager**: npm (see `package.json`)

**Node Version**: 22.x (see `engines` in package.json)

## Development Commands

```bash
# Install dependencies
npm install

# Development server (http://localhost:3000)
npm run dev

# Production build
npm run build

# Start production server
npm run start

# Linting
npm run lint

# Type checking
npm run type-check
```

## Environment Variables

Create `.env.local` from `.env.example`:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000  # Local
# NEXT_PUBLIC_API_URL=https://signals-api-dvf.vercel.app  # Production

# PostHog Analytics (optional)
NEXT_PUBLIC_POSTHOG_KEY=phc_xxxxxxxxxxxxx
NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
```

**Important**: All frontend env vars must be prefixed with `NEXT_PUBLIC_` to be exposed to the browser.

## Project Structure

```
src/
├── app/                      # Next.js App Router pages
│   ├── page.tsx             # Landing page (/)
│   ├── dashboard/           # Signal dashboard (/dashboard)
│   ├── signals/             # Signal detail pages (/signals/*)
│   ├── admin/               # Admin pages (/admin/*)
│   ├── layout.tsx           # Root layout with metadata
│   ├── providers.tsx        # React Query + PostHog providers
│   └── globals.css          # TailwindCSS styles + design tokens
├── components/
│   ├── sections/            # Landing page sections (Hero, ValueProps, etc.)
│   ├── dashboard/           # Dashboard-specific components (SignalCard)
│   ├── charts/              # Chart.js chart components
│   ├── forms/               # Form components (SubscribeForm)
│   └── layout/              # Layout components (AppHeader)
├── lib/
│   ├── hooks/               # Custom React hooks
│   │   └── useSignals.ts   # React Query hooks for API data
│   ├── api-client.ts        # Fetch wrapper for backend API
│   ├── posthog.tsx          # PostHog analytics setup
│   └── utils/               # Utility functions
└── stores/
    └── subscription-store.ts # Zustand store for subscription state
```

## Data Fetching Pattern

This project uses **TanStack React Query** for all API data fetching. Do NOT use basic `fetch()` in `useEffect()` hooks.

### React Query Hooks (`lib/hooks/useSignals.ts`)

```typescript
import { useSignals, useSignalBySymbol, useMarketData } from '@/lib/hooks/useSignals'

// In your component:
const { data: signals = [], isLoading, isError, error } = useSignals()
```

**Available hooks**:
- `useSignals()` - Fetch all signals (latest 50)
- `useSignalBySymbol(symbol)` - Fetch latest signal for a symbol
- `useMarketData(symbol, range)` - Fetch OHLCV bars for charting
- `useBacktestSummary(symbol, range)` - Fetch backtest performance
- `useSubscribers(options)` - Fetch subscriber list (admin only)

**React Query Configuration** (`app/providers.tsx`):
- `staleTime: 30_000` (30 seconds) - Data considered fresh for 30s
- `refetchOnWindowFocus: false` - Don't refetch when switching tabs
- `retry: 2` - Retry failed requests twice

### API Client (`lib/api-client.ts`)

Low-level fetch wrapper used by React Query hooks:

```typescript
import { api } from '@/lib/api-client'

// GET request with query params
const data = await api.get<Signal[]>('/api/signals', { limit: '50' })

// POST request with body
const result = await api.post<{ message: string }>('/api/subscribe', { email: 'user@example.com' })
```

**Do not call `api.get()` directly in components** - use React Query hooks instead.

## State Management

### React Query (Server State)

Use for **server data** (signals, market data, subscribers):
- Automatic caching
- Background refetching
- Optimistic updates
- Loading/error states

### Zustand (Client State)

Use for **client-only state** (UI state, form inputs, preferences):

```typescript
// stores/subscription-store.ts
import { create } from 'zustand'

interface SubscriptionState {
  email: string
  setEmail: (email: string) => void
}

export const useSubscriptionStore = create<SubscriptionState>((set) => ({
  email: '',
  setEmail: (email) => set({ email }),
}))
```

## Component Patterns

### Client Components

All interactive components use `'use client'` directive:

```typescript
'use client'

import { useSignals } from '@/lib/hooks/useSignals'

export default function Dashboard() {
  const { data: signals = [], isLoading } = useSignals()

  return (
    <div>
      {isLoading && <LoadingState />}
      {signals.map(signal => <SignalCard key={signal.id} {...signal} />)}
    </div>
  )
}
```

### Loading States

Show skeleton loaders while data is fetching:

```typescript
{isLoading && (
  <div className="card p-6 animate-pulse">
    <div className="h-6 bg-background-tertiary rounded mb-4 w-24" />
    <div className="h-8 bg-background-tertiary rounded mb-4" />
  </div>
)}
```

### Error States

Display user-friendly error messages:

```typescript
{isError && error && (
  <div className="card-premium p-6 mb-8 border-red-500/30">
    <span className="text-danger">⚠</span>
    <p className="text-danger">{error.message}</p>
  </div>
)}
```

## Design System

Custom design tokens defined in `app/globals.css`:

### Colors

```css
/* Background colors */
.bg-background-primary    /* Main background */
.bg-background-secondary  /* Card backgrounds */
.bg-background-tertiary   /* Skeleton loaders */

/* Foreground colors */
.text-foreground          /* Primary text */
.text-foreground-muted    /* Secondary text */

/* Signal-specific colors */
.text-success             /* BUY signals */
.text-danger              /* SELL signals */
.text-warning             /* HOLD signals */
```

### Components

```css
/* Card variants */
.card                     /* Standard card */
.card-premium             /* Premium card with glow */

/* Buttons */
.btn-primary              /* Primary CTA button */
.btn-secondary            /* Secondary button */

/* Animations */
.animate-fade-in          /* Fade in on mount */
.animate-slide-up         /* Slide up on mount */
.animate-pulse            /* Loading skeleton */
```

### Layout

```css
.container-app            /* Max-width container with padding */
```

## TypeScript Types

### Signal Types (`lib/hooks/useSignals.ts`)

```typescript
interface Signal {
  id: string
  symbol: string
  timestamp: string
  signal_type: 'BUY' | 'SELL' | 'HOLD'
  strength: number           // 0-100
  reasoning: string[]
  price_at_signal: number
}

interface MarketBar {
  symbol: string
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}
```

Types are co-located with hooks for easy discovery.

## Common Tasks

### Adding a New API Endpoint

1. **Add hook to `lib/hooks/useSignals.ts`**:
   ```typescript
   export function useNewEndpoint() {
     return useQuery({
       queryKey: ['new-endpoint'],
       queryFn: async () => api.get<ResponseType>('/api/new-endpoint'),
       staleTime: 60_000,
     })
   }
   ```

2. **Use in component**:
   ```typescript
   const { data, isLoading } = useNewEndpoint()
   ```

### Adding a New Page

1. **Create `app/new-page/page.tsx`**:
   ```typescript
   export default function NewPage() {
     return <div>New Page</div>
   }
   ```

2. **Add to navigation** in `components/layout/AppHeader.tsx`:
   ```typescript
   const navItems = [
     { href: '/new-page', label: 'New Page' },
   ]
   ```

### Creating a New Component

1. **Create component file** in appropriate directory:
   ```typescript
   // components/sections/NewSection.tsx
   export function NewSection() {
     return <section className="container-app py-12">...</section>
   }
   ```

2. **Export from barrel file** if using barrel exports:
   ```typescript
   // components/sections/index.ts
   export { NewSection } from './NewSection'
   ```

## Chart.js Integration

Use Chart.js for data visualization with `react-chartjs-2` wrapper:

```typescript
import { Line } from 'react-chartjs-2'
import { Chart, registerables } from 'chart.js'
import 'chartjs-adapter-date-fns' // For time-series charts

Chart.register(...registerables)

const data = {
  labels: timestamps,
  datasets: [{
    label: 'Price',
    data: prices,
    borderColor: 'rgb(75, 192, 192)',
  }]
}

<Line data={data} options={options} />
```

**Time-series charts**: Use `chartjs-adapter-date-fns` for date/time x-axes.

## PostHog Analytics

Analytics are configured in `lib/posthog.tsx` and wrapped in `app/providers.tsx`.

**Track events**:
```typescript
import posthog from 'posthog-js'

posthog.capture('signal_clicked', { symbol: 'BTC-USD' })
```

**Conditional tracking**: PostHog only initializes if `NEXT_PUBLIC_POSTHOG_KEY` is set.

## Performance Optimizations

1. **React Query caching**: Data cached for 24 hours (`gcTime`)
2. **Image optimization**: WebP/AVIF formats enabled in `next.config.ts`
3. **Package optimization**: Chart.js packages optimized in `experimental.optimizePackageImports`
4. **Static metadata**: SEO metadata in `app/layout.tsx`

## Path Aliases

TypeScript path alias `@/*` maps to `./src/*`:

```typescript
import { useSignals } from '@/lib/hooks/useSignals'  // Instead of '../../../lib/hooks/useSignals'
```

Configured in `tsconfig.json`.

## Deployment (Vercel)

**Production URL**: https://signals-dvf.vercel.app

**Auto-deploy**: Every push to `main` branch triggers deployment

**Environment Variables** (set in Vercel dashboard):
- `NEXT_PUBLIC_API_URL=https://signals-api-dvf.vercel.app`
- `NEXT_PUBLIC_POSTHOG_KEY=phc_xxxxxxxxxxxxx` (optional)
- `NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com` (optional)

**Preview Deployments**: Every PR gets a preview URL

**Manual Deployment**:
```bash
vercel deploy --prod
```

## Key Architecture Decisions

1. **Client-Side Rendering**: All data fetching happens client-side (no SSR/SSG) for real-time updates
2. **React Query over SWR**: Chosen for better TypeScript support and advanced caching
3. **Zustand over Redux**: Lighter weight for simple client state needs
4. **TailwindCSS 4.0**: Uses new CSS-first architecture (no PostCSS plugins needed)
5. **No authentication**: MVP is public-facing, auth planned for Phase 2

## Related Documentation

**Project Root**: See `/Users/diegovfeder/workspace/jobs/signals/CLAUDE.md` for:
- Backend API endpoints
- Database schema
- Prefect pipeline architecture
- Overall system design

**Backend Repository**: `../backend/` contains FastAPI source code

**Important**: The root CLAUDE.md describes an older hook pattern (`useSignals()` with basic fetch). This frontend uses **React Query** - always refer to `lib/hooks/useSignals.ts` for current implementation.
