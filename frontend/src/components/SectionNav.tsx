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
  const [active, setActive] = useState(() => {
    if (typeof window === 'undefined') return items[0]?.id ?? '';
    const hash = window.location.hash.replace(/^#/, '');
    return items.some((i) => i.id === hash) ? hash : items[0]?.id ?? '';
  });

  useEffect(() => {
    if (!items.length) return;
    const ids = items.map((i) => i.id);

    const pickFromScroll = () => {
      // Section whose top is closest above ~28% of the viewport is "current"
      const line = window.innerHeight * 0.28;
      let best = ids[0];
      let bestDist = Number.POSITIVE_INFINITY;
      for (const id of ids) {
        const el = document.getElementById(id);
        if (!el) continue;
        const top = el.getBoundingClientRect().top;
        const dist = Math.abs(top - line);
        if (top <= line + 40 && dist < bestDist) {
          bestDist = dist;
          best = id;
        }
      }
      // Near the bottom of the page: force the last visible section
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 80) {
        best = ids[ids.length - 1];
      }
      setActive((prev) => (prev === best ? prev : best));
    };

    const onHash = () => {
      const hash = window.location.hash.replace(/^#/, '');
      if (ids.includes(hash)) setActive(hash);
    };

    pickFromScroll();
    window.addEventListener('scroll', pickFromScroll, { passive: true });
    window.addEventListener('hashchange', onHash);
    return () => {
      window.removeEventListener('scroll', pickFromScroll);
      window.removeEventListener('hashchange', onHash);
    };
  }, [items]);

  return [active, setActive] as const;
}

/** Section timeline: sticky rail on the physical right (desktop), compact chips on mobile. */
export default function SectionNav({ items, label, mode }: Props) {
  const [active, setActive] = useActiveSection(items);
  if (!items.length) return null;

  const activeIndex = Math.max(0, items.findIndex((i) => i.id === active));

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
                  onClick={() => setActive(item.id)}
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

  // Physical-right rail (dir=ltr) so Persian RTL pages do not flip the line/dots.
  // Sticky lives on this nav; the aside must stretch with the page (see species page layout).
  return (
    <nav aria-label={label} className="sticky top-24 hidden lg:block" dir="ltr">
      <ol className="relative border-r-2 border-stone-200 pr-4 text-right">
        {/* Progress fill on the rail up to the active item */}
        <span
          aria-hidden="true"
          className="pointer-events-none absolute right-0 top-0 w-0.5 -translate-x-[0px] bg-brand-600 transition-[height] duration-300"
          style={{
            height: items.length > 1 ? `${(activeIndex / (items.length - 1)) * 100}%` : '0%',
            marginRight: '-1px',
          }}
        />
        {items.map((item, i) => {
          const on = item.id === active;
          const past = i < activeIndex;
          return (
            <li key={item.id} className="relative py-1.5">
              <span
                aria-hidden="true"
                className={`absolute top-1/2 h-2.5 w-2.5 -translate-y-1/2 rounded-full transition-all duration-200 ${
                  on
                    ? '-right-[1.35rem] scale-125 bg-brand-600 ring-4 ring-brand-200'
                    : past
                      ? '-right-[1.3rem] bg-brand-500'
                      : '-right-[1.3rem] bg-stone-300 ring-2 ring-stone-50'
                }`}
              />
              <a
                href={`#${item.id}`}
                dir="auto"
                onClick={() => setActive(item.id)}
                className={`block text-sm leading-snug transition ${
                  on
                    ? 'font-semibold text-brand-800'
                    : past
                      ? 'text-brand-700/80 hover:text-brand-800'
                      : 'text-stone-500 hover:text-brand-700'
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
