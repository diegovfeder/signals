# Product & Tech Backlog (Next.js Frontend)

Captured from the recent diagnostics session. Convert each item into a GitHub issue when ready.

## Key Findings

1. **Dashboard is fully client-side**  
   - File: `frontend/src/app/signals/page.tsx`  
   - Issue: Entire route is a Client Component that fetches `/api/signals` via React Query, so every visit loads all data in the browser and ships the full JS bundle. Next.js recommends fetching in Server Components to cut bundle size and improve FCP (see `/docs/app/building-your-application/rendering/server-components`).  
   - Opportunity: Rebuild as an async Server Component or stream server-fetched sections so bots/crawlers see HTML and cached data.

2. **Symbol detail page blocks on 5 client fetches**  
   - File: `frontend/src/app/signals/[symbol]/page.tsx`  
   - Issue: Client Component calls `use(params)` directly and then fetches signal, market data, indicators, history, and backtests on the client. This leaves a blank screen until all requests finish. Dynamic params should be read with `useParams` in client code, but the heavy lifting belongs in Server Components per the same server component guidance.  
   - Opportunity: Create a Server Component shell that loads symbol data + metadata, then hydrate small client widgets for charts/toggles.

3. **Missing per-route metadata**  
   - Files: `frontend/src/app/signals/page.tsx`, `frontend/src/app/signals/[symbol]/page.tsx`, `frontend/src/app/layout.tsx`  
   - Issue: Only the root layout defines metadata; dynamic pages reuse the generic title/description. The Metadata API should emit canonical URLs, OG images, and symbol-specific titles (docs: `/docs/app/building-your-application/optimizing/metadata`).  
   - Opportunity: Implement `generateMetadata` for `/signals` and `/signals/[symbol]`, optionally generating OG images per symbol.

4. **PostHog initialized aggressively**  
   - File: `frontend/src/lib/posthog.tsx` and runtime log `frontend/.next/dev/logs/next-development.log`  
   - Issue: PostHog starts with `debug: true`, session recording, heatmaps, and dead-click capture on every route—even when `NEXT_PUBLIC_POSTHOG_KEY` is missing. Logs show many subsystems starting per navigation, inflating network requests.  
   - Opportunity: Guard initialization behind the env key, disable debug + session recording by default, and lazy-load analytics to keep Lighthouse/TTFB in check.

5. **Need Lighthouse baseline**  
   - Tooling gap: Could not capture navigation timing metrics via `browser_eval.evaluate` (serialization bug).  
   - Opportunity: Run Lighthouse locally (`Chrome DevTools → Lighthouse` or `npx @lhci/cli`) after implementing the changes above to validate perf gains and catch regressions.

## Suggested Next Steps

1. Convert `/signals` route to an async Server Component that fetches signals server-side (via `fetch` or Supabase) and streams card/table views with `Suspense`, keeping interactive toggles in small `'use client'` components.
2. Refactor `/signals/[symbol]` into a Server Component shell that loads symbol data, metadata, and expensive datasets before handing off to focused Client Components; read dynamic params with `useParams` only where necessary.
3. Implement `generateMetadata` for both dashboard routes so SEO, OG tags, and canonical links are symbol-aware.
4. Add configuration guards for PostHog (skip init without `NEXT_PUBLIC_POSTHOG_KEY`, disable debug/session recording by default, consider a “metrics on/off” env flag for previews).
5. After refactors, re-run Lighthouse (desktop + mobile) and monitor the Next dev log for caching warnings to confirm performance improvements.
