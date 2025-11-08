/**
 * API Client
 *
 * Fetch wrapper for making requests to the backend API.
 */

const DEFAULT_API_URL =
  process.env.NODE_ENV === 'production'
    ? 'https://signals-api-dvf.vercel.app'
    : 'http://localhost:8000';

const API_URL = process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_URL;

interface FetchOptions extends RequestInit {
  params?: Record<string, string>;
}

export async function apiClient<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { params, ...fetchOptions } = options;

  // Build URL with query params
  const url = new URL(`${API_URL}${endpoint}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });
  }

  // Make request
  const method = (fetchOptions.method || 'GET').toUpperCase();
  const headers = new Headers(fetchOptions.headers || undefined);

  if ((method !== 'GET' || fetchOptions.body) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(url.toString(), {
    ...fetchOptions,
    method,
    headers,
    credentials: 'omit', // API is stateless - don't send cookies/credentials
  });

  // Handle errors
  if (!response.ok) {
    let errorMessage = `API Error: ${response.status} ${response.statusText}`;
    try {
      const errorBody = await response.json();
      if (typeof errorBody?.detail === 'string') {
        errorMessage = errorBody.detail;
      } else if (typeof errorBody?.message === 'string') {
        errorMessage = errorBody.message;
      }
    } catch {
      // ignore JSON parse errors and keep default message
    }
    throw new Error(errorMessage);
  }

  return response.json();
}

// Convenience methods
export const api = {
  get: <T>(endpoint: string, params?: Record<string, string>) =>
    apiClient<T>(endpoint, { method: 'GET', params }),

  post: <T>(endpoint: string, data: any) =>
    apiClient<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // TODO: Add PUT, DELETE methods if needed
};
