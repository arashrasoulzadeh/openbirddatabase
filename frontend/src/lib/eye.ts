export const EYE_CONFIG = {
  apiKey: '5456fde259d040d0a34d69d8900fe44b',
  tenant: 'e7f629db42c5a105a67c9c5e7c844f42',
  endpoint: 'https://eye-api.meetarash.ir',
  browserEndpoint: '/api/eye',
  cdn: 'https://cdn.jsdelivr.net/gh/arashrasoulzadeh/eye@cdn/eye.min.js',
} as const;

export interface EyeGlobal {
  init(options: Record<string, unknown>): unknown;
  track(name: string, props?: Record<string, unknown>, payload?: Record<string, unknown>): void;
  flush(): Promise<void>;
  getSessionId(): string | null;
}

declare global {
  interface Window {
    Eye?: EyeGlobal;
  }
}

export function eye(): EyeGlobal | undefined {
  return typeof window !== 'undefined' ? window.Eye : undefined;
}
