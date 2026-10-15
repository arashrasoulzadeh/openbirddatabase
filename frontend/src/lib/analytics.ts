// First-party analytics client. Sends small events to the API (POST /analytics/event).
// No cookies, no IP/user-agent storage: the visitor and session ids are random strings kept in the browser.
// Visitors with Do-Not-Track / Global Privacy Control are not tracked, and the dashboard itself is never counted.
import { API_URL } from './config';

export type EventType =
  | 'pageview' | 'page_leave' | 'bird_click' | 'search' | 'filter'
  | 'language_change' | 'tab_view' | 'load_more' | 'random_bird';

export interface TrackData {
  path?: string;
  bird?: string;
  query?: string;
  source?: string;
  value?: number;
  referrer?: string;
  props?: Record<string, unknown>;
}

const VISITOR_KEY = 'ob_vid';
const SESSION_KEY = 'ob_sid';

let queue: Record<string, unknown>[] = [];
let timer: ReturnType<typeof setTimeout> | null = null;

function randomId(): string {
  const c = typeof crypto !== 'undefined' ? crypto : undefined;
  if (c?.randomUUID) return c.randomUUID();
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

function stored(storage: Storage | undefined, key: string): string {
  try {
    let id = storage?.getItem(key);
    if (!id) {
      id = randomId();
      storage?.setItem(key, id);
    }
    return id;
  } catch {
    return randomId(); // storage blocked: still count, just without continuity
  }
}

export function trackingAllowed(): boolean {
  if (typeof window === 'undefined') return false;
  const nav = navigator as Navigator & { globalPrivacyControl?: boolean };
  if (nav.doNotTrack === '1' || nav.globalPrivacyControl) return false;
  return !window.location.pathname.startsWith('/analytics');
}

function referrerHost(): string | undefined {
  try {
    const host = document.referrer ? new URL(document.referrer).host : '';
    return host && host !== window.location.host ? host : undefined;
  } catch {
    return undefined;
  }
}

/** Send everything queued. text/plain keeps the request "simple" so browsers skip the CORS preflight. */
export function flush(): void {
  if (timer) {
    clearTimeout(timer);
    timer = null;
  }
  if (!queue.length) return;
  const body = JSON.stringify({ events: queue });
  queue = [];
  const url = `${API_URL}/analytics/event`;
  try {
    if (navigator.sendBeacon?.(url, new Blob([body], { type: 'text/plain;charset=UTF-8' }))) return;
  } catch {
    /* fall through to fetch */
  }
  fetch(url, { method: 'POST', body, headers: { 'Content-Type': 'text/plain;charset=UTF-8' }, keepalive: true }).catch(() => {});
}

export function track(type: EventType, data: TrackData = {}): void {
  if (!trackingAllowed()) return;
  const isFirstPage = type === 'pageview' && !sessionStorageHas();
  queue.push({
    type,
    path: data.path ?? window.location.pathname,
    visitor: stored(window.localStorage, VISITOR_KEY),
    session: stored(window.sessionStorage, SESSION_KEY),
    lang: document.documentElement.lang || undefined,
    bird: data.bird,
    query: data.query,
    source: data.source,
    value: data.value,
    props: data.props,
    referrer: data.referrer ?? (isFirstPage ? referrerHost() : undefined),
  });
  if (queue.length >= 20) flush();
  else if (!timer) timer = setTimeout(flush, 800);
}

// The referrer only matters for the first page of a session
function sessionStorageHas(): boolean {
  try {
    const seen = window.sessionStorage.getItem('ob_seen') === '1';
    window.sessionStorage.setItem('ob_seen', '1');
    return seen;
  } catch {
    return true;
  }
}
