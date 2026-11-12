'use client';

import Script from 'next/script';
import { EYE_CONFIG, eye } from '@/lib/eye';
import { replayPending } from '@/lib/analytics';

let initialized = false;

export default function EyeAnalytics() {
  const init = () => {
    if (initialized) return;
    const client = window.Eye;
    if (!client) return;
    initialized = true;
    client.init({
      apiKey: EYE_CONFIG.apiKey,
      tenant: EYE_CONFIG.tenant,
      // Eye's API currently does not expose browser CORS headers. The local
      // proxy keeps the CDN SDK same-origin and forwards to EYE_CONFIG.endpoint.
      endpoint: EYE_CONFIG.browserEndpoint,
      storageKey: 'openbird_eye_session',
      autoTrack: true,
      debug: process.env.NODE_ENV !== 'production',
    });
    // The app can emit domain events before the async session handshake finishes.
    const replay = window.setInterval(() => {
      if (eye()?.getSessionId()) {
        window.clearInterval(replay);
        replayPending();
      }
    }, 50);
    window.setTimeout(() => window.clearInterval(replay), 10000);
  };

  return <Script id="eye-sdk" src={EYE_CONFIG.cdn} strategy="afterInteractive" onLoad={init} />;
}
