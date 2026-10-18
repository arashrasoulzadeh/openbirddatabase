'use client';

import { useEffect, useState } from 'react';

export type SectionNavItem = { id: string; label: string };

/** Sticky timeline of page sections: vertical on the right (desktop), compact horizontal on mobile. */
export default function SectionNav({ items, label }: { items: SectionNavItem[]; label: string }) {
  const [active, setActive] = useState(items[0]?.id ?? '');

  useEffect(() => {
    if (!items.length) return;
    const nodes = items
      .map((item) => document.getElementById(item.id))
      .filter((el): el is HTMLElement => !!el);
    if (!nodes.length) return;

    const ratios = new Map<string, number>();
    const obs = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          ratios.set(entry.target.id, entry.isIntersecting ? entry.intersectionRatio : 0);
        }
        let best = items[0].id;
        let bestRatio = -1;
        for (const item of items) {
          const r = ratios.get(item.id) ?? 0;
          if (r > bestRatio) {
            bestRatio = r;
            best = item.id;
          }
        }
        if (bestRatio > 0) setActive(best);
      },
      { rootMargin: '-20% 0px -55% 0px', threshold: [0, 0.15, 0.35, 0.55, 0.75] },
    );
    nodes.forEach((n) => obs.observe(n));
    return () => obs.disconnect();
  }, [items]);

  if (!items.length) return null;

  return (
    <>
      {/* Mobile / tablet: horizontal timeline under the hero */}
      <nav
        aria-label={label}
        className="sticky top-0 z-20 -mx-4 border-b border-stone-200/80 bg-stone-50/95 px-4 py-2 backdrop-blur lg:hidden"
      >
        <ol className="flex gap-0 overflow-x-auto pb-0.5 scrollbar-hide">
          {items.map((item, i) => {
            const on = item.id === active;
            return (
              <li key={item.id} className="flex shrink-0 items-center">
                {i > 0 && (
                  <span
                    aria-hidden="true"
                    className={`mx-0.5 h-px w-3 ${on || items[i - 1]?.id === active ? 'bg-brand-400' : 'bg-stone-200'}`}
                  />
                )}
                <a
                  href={`#${item.id}`}
                  className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs transition ${
                    on
                      ? 'bg-brand-700 font-medium text-white'
                      : 'bg-white text-stone-600 ring-1 ring-inset ring-stone-200'
                  }`}
                >
                  <span
                    aria-hidden="true"
                    className={`h-1.5 w-1.5 rounded-full ${on ? 'bg-white' : 'bg-stone-300'}`}
                  />
                  {item.label}
                </a>
              </li>
            );
          })}
        </ol>
      </nav>

      {/* Desktop: vertical timeline pinned to the physical right */}
      <nav
        aria-label={label}
        className="pointer-events-none fixed end-auto right-4 top-28 z-20 hidden w-44 lg:block xl:right-8 xl:w-48"
      >
        <ol className="pointer-events-auto relative ms-2 space-y-0 border-s-2 border-stone-200 ps-4">
          {items.map((item) => {
            const on = item.id === active;
            return (
              <li key={item.id} className="relative py-1.5">
                <span
                  aria-hidden="true"
                  className={`absolute -start-[1.3rem] top-1/2 h-2.5 w-2.5 -translate-y-1/2 rounded-full ring-2 ring-stone-50 transition ${
                    on ? 'bg-brand-600 scale-110' : 'bg-stone-300'
                  }`}
                />
                <a
                  href={`#${item.id}`}
                  className={`block text-sm leading-snug transition ${
                    on ? 'font-semibold text-brand-800' : 'text-stone-500 hover:text-brand-700'
                  }`}
                >
                  {item.label}
                </a>
              </li>
            );
          })}
        </ol>
      </nav>
    </>
  );
}
