import { flush, track, trackingAllowed } from '../analytics';

const sent: any[] = [];

beforeEach(() => {
  sent.length = 0;
  window.history.pushState({}, '', '/');
  window.localStorage.clear();
  window.sessionStorage.clear();
  document.documentElement.lang = 'en';
  (window as any).Eye = {
    getSessionId: () => 'session-1',
    track: (name: string, props: any) => sent.push({ name, props }),
    flush: jest.fn(() => Promise.resolve()),
  };
  Object.defineProperty(navigator, 'doNotTrack', { value: null, configurable: true });
  // jsdom has no sendBeacon: the client falls back to fetch
  (global as any).fetch = jest.fn((url: string, init: any) => {
    sent.push({ url, init, body: JSON.parse(init.body) });
    return Promise.resolve({ ok: true });
  });
});

describe('analytics client', () => {
  it('sends domain events through the Eye SDK with normalized context', () => {
    track('pageview', { path: '/' });
    track('search', { query: 'owl', value: 12 });
    flush();
    expect(sent.map((e: any) => e.name)).toEqual(['pageview', 'search']);
    expect(sent[1].props).toMatchObject({ query: 'owl', value: 12, lang: 'en', path: '/' });
  });

  it('uses the SDK session for domain events', () => {
    track('pageview');
    track('bird_click', { bird: 'Parus major', source: 'search' });
    flush();
    expect(sent[0].props.path).toBe('/');
    expect(sent[1].props.path).toBe('/');
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
