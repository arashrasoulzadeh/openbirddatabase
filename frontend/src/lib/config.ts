// Public URLs come from the repo-root .env (see ../.env.example):
//   API_DOMAIN  -> NEXT_PUBLIC_API_URL  (e.g. https://api.example.org)
//   SITE_DOMAIN -> NEXT_PUBLIC_SITE_URL (e.g. https://example.org)
const trim = (u: string) => u.replace(/\/+$/, '');

export const API_URL = trim(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');
export const SITE_URL = trim(process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000');

// Server-side rendering may reach the API over the internal docker network instead.
export const API_SERVER_URL = trim(process.env.API_INTERNAL_URL || API_URL);
