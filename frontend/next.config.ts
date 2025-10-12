import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,

  // Environment variables exposed to browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // Image optimization
  images: {
    formats: ['image/webp', 'image/avif'],
  },

  // Experimental features
  experimental: {
    optimizePackageImports: ['chart.js', 'react-chartjs-2'],
  },
};

export default nextConfig;
