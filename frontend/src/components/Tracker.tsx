'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { flush, track } from '@/lib/analytics';

/** Records a page view for every route and the time the page was actually visible. Renders nothing. */
export default function Tracker() {
  const pathname = usePathname();

  useEffect(() => {
    let start = Date.now();
    track('pageview', { path: pathname });

    const sendLeave = () => {
      if (!start) return;
      track('page_leave', { path: pathname, value: Date.now() - start });
      start = 0;
      flush();
    };
    const onVisibility = () => {
      if (document.visibilityState === 'hidden') sendLeave();
      else start = Date.now(); // back on the tab: count visible time again
    };

    document.addEventListener('visibilitychange', onVisibility);
    window.addEventListener('pagehide', sendLeave);
    return () => {
      document.removeEventListener('visibilitychange', onVisibility);
      window.removeEventListener('pagehide', sendLeave);
      sendLeave(); // navigating to another route
    };
  }, [pathname]);

  return null;
}
