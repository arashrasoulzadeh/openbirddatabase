import { splitLang } from './i18n/routes';
// First-party analytics client. Sends small events to the API (POST /analytics/event).
// No cookies, no IP/user-agent storage: the visitor and session ids are random strings kept in the browser.
// Visitors with Do-Not-Track / Global Privacy Control are not tracked, and the dashboard itself is never counted.
import { eye } from './eye';

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

const pending: Array<[EventType, TrackData]> = [];

export function trackingAllowed(): boolean {
  if (typeof window === 'undefined') return false;
  const nav = navigator as Navigator & { globalPrivacyControl?: boolean };
  if (nav.doNotTrack === '1' || nav.globalPrivacyControl) return false;
  return !splitLang(window.location.pathname).path.startsWith('/analytics');
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
  eye()?.flush().catch(() => {});
}

export function replayPending(): void {
  const queued = pending.splice(0);
  for (const [type, data] of queued) track(type, data);
}

export function track(type: EventType, data: TrackData = {}): void {
  if (!trackingAllowed()) return;
  const props = {
    path: data.path ?? splitLang(window.location.pathname).path,
    lang: document.documentElement.lang || undefined,
    bird: data.bird,
    query: data.query,
    source: data.source,
    value: data.value,
    referrer: data.referrer ?? referrerHost(),
    ...data.props,
  };
  const client = eye();
  if (!client?.getSessionId()) {
    pending.push([type, data]);
    return;
  }
  client.track(type, props);
}
