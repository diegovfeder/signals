# Production Deployment Guide

Deploy Trading Signals MVP to production using free/low-cost services.

## Architecture Overview

```mermaid
flowchart LR

  FE["Frontend (Vercel)"] --> API["Backend API (Vercel)"] --> DB["Database (Neon)"]
  PF["Flows (Prefect Cloud)"] --> API
  PF --> EM["Email (Resend)"]
```

## 1. Database Setup (Neon)

### Create Neon Project

1. Go to [neon.tech](https://neon.tech)
2. Sign up for free tier (0.5GB storage)
3. Create new project: "trading-signals"
4. Copy connection string

### Run Migrations

```bash
export DATABASE_URL="postgresql://user:pass@host/dbname"
python scripts/setup_db.py
python scripts/seed_historical_data.py
```

## 2. Backend Deployment (Vercel)

### Prerequisites

- Vercel account ([vercel.com](https://vercel.com))
- GitHub repository

### Deploy Steps

1. **Connect GitHub Repository**
   - Go to Vercel dashboard
   - Click "New Project"
   - Import your repository
   - Set root directory: `backend`

2. **Configure Build Settings**
   - Framework Preset: Other
   - Build Command: (leave empty)
   - Output Directory: (leave empty)

3. **Set Environment Variables**

   ```env
   DATABASE_URL=postgresql://...  (from Neon)
   RESEND_API_KEY=re_...          (from Resend)
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Copy API URL: `https://your-api.vercel.app`

### Verify Deployment

```bash
curl https://your-api.vercel.app/health
```

## 3. Frontend Deployment (Vercel)

- Deploy Steps:

1. **New Project**
   - Import same repository
   - Set root directory: `frontend`

2. **Configure Build Settings**
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`

3. **Set Environment Variables**

   ```env
   NEXT_PUBLIC_API_URL=https://your-api.vercel.app
   NEXT_PUBLIC_POSTHOG_KEY=phc_...  (from PostHog)
   ```

4. **Deploy**
   - Click "Deploy"
   - Your site will be live at: `https://your-site.vercel.app`

### Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed

## 4. Prefect Cloud Setup

### Create Account

1. Go to [prefect.io](https://prefect.io)
2. Sign up for free tier (20k task runs/month)
3. Create workspace: "trading-signals"

### Deploy Flows

```bash
# Install Prefect
pip install prefect

# Login to Prefect Cloud
prefect cloud login

# Deploy flows
cd prefect
python schedules.py
```

### Start Agent

Option 1: Run on your local machine (for testing)

```bash
prefect agent start -q default
```

Option 2: Deploy to cloud (recommended)

- Use Railway, Render, or Fly.io
- Run: `prefect agent start -q default`
- Keep running 24/7

## 5. Email Service (Resend)

### Setup

1. Go to [resend.com](https://resend.com)
2. Sign up for free tier (3,000 emails/month)
3. Get API key from dashboard
4. Add to environment variables:
   - Vercel backend: `RESEND_API_KEY`
   - Prefect: `RESEND_API_KEY`

### Verify Email Domain (Optional)

1. Add your domain in Resend dashboard
2. Add DNS records (MX, TXT, DKIM)
3. Verify domain
4. Send from: `signals@yourdomain.com`

## 6. Analytics (PostHog)

- Setup:

1. Go to [posthog.com](https://posthog.com)
2. Sign up for free tier (1M events/month)
3. Create project: "trading-signals"
4. Copy API key
5. Add to Vercel frontend: `NEXT_PUBLIC_POSTHOG_KEY`

## 7. Monitoring (Sentry - Optional)

- Setup:

1. Go to [sentry.io](https://sentry.io)
2. Sign up for free tier (5k errors/month)
3. Create project: "trading-signals-frontend"
4. Create project: "trading-signals-backend"
5. Add Sentry SDK to code
6. Deploy

## Environment Variables Summary

### Vercel Backend

```env
DATABASE_URL=postgresql://...
RESEND_API_KEY=re_...
```

### Vercel Frontend

```env
NEXT_PUBLIC_API_URL=https://your-api.vercel.app
NEXT_PUBLIC_POSTHOG_KEY=phc_...
```

### Prefect Cloud

```env
DATABASE_URL=postgresql://...
RESEND_API_KEY=re_...
PREFECT_API_KEY=pnu_...
```

## Post-Deployment Checklist

- [ ] Database schema created
- [ ] Historical data seeded
- [ ] Backend API responding
- [ ] Frontend loading
- [ ] Prefect flows scheduled
- [ ] Email sending working
- [ ] Analytics tracking
- [ ] Custom domain configured (if applicable)

## Monitoring

### Check API Health

```bash
curl https://your-api.vercel.app/health
```

### Check Prefect Flows

1. Go to [app.prefect.cloud](https://app.prefect.cloud)
2. View flow runs
3. Check for errors

### Check Analytics

1. Go to PostHog dashboard
2. View events
3. Track user behavior

## Costs

All services have generous free tiers:

- **Neon**: 0.5GB free
- **Vercel**: Unlimited deployments
- **Prefect Cloud**: 20k task runs/month
- **Resend**: 3,000 emails/month
- **PostHog**: 1M events/month

**Total Monthly Cost: $0** (for MVP scale)

## Scaling

If you exceed free tiers:

- **Neon**: Upgrade to Pro ($19/mo for 10GB)
- **Vercel**: Pro plan ($20/mo per member)
- **Prefect**: Standard plan ($450/mo for 150k runs)
- **Resend**: Pro plan ($20/mo for 50k emails)

But you shouldn't hit these limits during MVP validation.
