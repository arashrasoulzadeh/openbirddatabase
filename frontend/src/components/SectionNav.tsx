'use client';

import { useEffect, useState } from 'react';

export type SectionNavItem = { id: string; label: string };

type Props = {
  items: SectionNavItem[];
  label: string;
  /** mobile = chip strip; desktop = sticky right rail */
  mode: 'mobile' | 'desktop';
};

function useActiveSection(items: SectionNavItem[]) {
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

  return active;
}

/** Section timeline: sticky rail on the physical right (desktop), compact chips on mobile. */
export default function SectionNav({ items, label, mode }: Props) {
  const active = useActiveSection(items);
  if (!items.length) return null;

  if (mode === 'mobile') {
    return (
      <nav
        aria-label={label}
        className="sticky top-0 z-20 -mx-4 mb-4 border-b border-stone-200/80 bg-stone-50/95 px-4 py-2.5 backdrop-blur lg:hidden"
      >
        <ol className="flex gap-2 overflow-x-auto pb-0.5 scrollbar-hide">
          {items.map((item) => {
            const on = item.id === active;
            return (
              <li key={item.id} className="shrink-0">
                <a
                  href={`#${item.id}`}
                  className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs transition ${
                    on
                      ? 'bg-brand-700 font-medium text-white shadow-sm'
                      : 'bg-white text-stone-600 ring-1 ring-inset ring-stone-200'
                  }`}
                >
                  <span
                    aria-hidden="true"
                    className={`h-1.5 w-1.5 rounded-full ${on ? 'bg-teal-200' : 'bg-brand-500/70'}`}
                  />
                  {item.label}
                </a>
              </li>
            );
          })}
        </ol>
      </nav>
    );
  }

  // Physical-right rail (dir=ltr on the list) so Persian RTL pages do not flip the line/dots.
  return (
    <nav aria-label={label} className="hidden lg:block" dir="ltr">
      <ol className="sticky top-28 border-r-2 border-stone-200 pr-4 text-right">
        {items.map((item) => {
          const on = item.id === active;
          return (
            <li key={item.id} className="relative py-1.5">
              <span
                aria-hidden="true"
                className={`absolute top-1/2 h-2.5 w-2.5 -translate-y-1/2 rounded-full ring-2 ring-stone-50 transition ${
                  on ? '-right-[1.35rem] scale-110 bg-brand-600' : '-right-[1.3rem] bg-stone-300'
                }`}
              />
              <a
                href={`#${item.id}`}
                dir="auto"
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
  );
}
