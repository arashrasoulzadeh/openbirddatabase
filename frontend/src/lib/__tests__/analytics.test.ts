import { flush, track, trackingAllowed } from '../analytics';

const sent: any[] = [];

beforeEach(() => {
  sent.length = 0;
  window.history.pushState({}, '', '/');
  window.localStorage.clear();
  window.sessionStorage.clear();
  document.documentElement.lang = 'en';
  Object.defineProperty(navigator, 'doNotTrack', { value: null, configurable: true });
  // jsdom has no sendBeacon: the client falls back to fetch
  (global as any).fetch = jest.fn((url: string, init: any) => {
    sent.push({ url, init, body: JSON.parse(init.body) });
    return Promise.resolve({ ok: true });
  });
});

describe('analytics client', () => {
  it('batches events and posts them as text/plain (no CORS preflight)', () => {
    track('pageview', { path: '/' });
    track('search', { query: 'owl', value: 12 });
    flush();
    expect(sent).toHaveLength(1);
    expect(sent[0].url).toMatch(/\/analytics\/event$/);
    expect(sent[0].init.headers['Content-Type']).toBe('text/plain;charset=UTF-8');
    const events = sent[0].body.events;
    expect(events.map((e: any) => e.type)).toEqual(['pageview', 'search']);
    expect(events[1]).toMatchObject({ query: 'owl', value: 12, lang: 'en', path: '/' });
  });

  it('uses one visitor id across events and keeps it between calls', () => {
    track('pageview');
    track('bird_click', { bird: 'Parus major', source: 'search' });
    flush();
    const [a, b] = sent[0].body.events;
    expect(a.visitor).toBeTruthy();
    expect(a.visitor).toBe(b.visitor);
    expect(a.session).toBe(b.session);
    expect(window.localStorage.getItem('ob_vid')).toBe(a.visitor);
  });

  it('respects Do Not Track and never tracks the dashboard', () => {
    Object.defineProperty(navigator, 'doNotTrack', { value: '1', configurable: true });
    expect(trackingAllowed()).toBe(false);
    track('pageview');
    flush();
    expect(sent).toHaveLength(0);

    Object.defineProperty(navigator, 'doNotTrack', { value: null, configurable: true });
    window.history.pushState({}, '', '/analytics');
    expect(trackingAllowed()).toBe(false);
  });

  it('sends nothing when there is nothing queued', () => {
    flush();
    expect(sent).toHaveLength(0);
  });
});
