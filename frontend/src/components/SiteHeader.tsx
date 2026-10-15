'use client';

import Link from 'next/link';
import LanguageSwitcher from './LanguageSwitcher';

/** Sticky header: brand and language switcher on the first row; `children` (tabs/links) wrap to a second row on phones. */
export default function SiteHeader({ children }: { children?: React.ReactNode }) {
  return (
    <header className="sticky top-0 z-40 border-b border-stone-200 bg-white/90 backdrop-blur">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 py-2.5 sm:h-14 sm:flex-nowrap sm:py-0">
          <Link href="/" className="flex items-center gap-2 text-brand-800">
            <svg className="h-7 w-7" viewBox="0 0 32 32" fill="none" aria-hidden="true">
              <circle cx="16" cy="16" r="16" className="fill-brand-700" />
              <path d="M9 20c2-6 7-9 13-8-1 5-4 9-10 9-1 0-2 0-3-1z" fill="#fff" />
              <circle cx="20.5" cy="14" r="1.1" className="fill-brand-700" />
            </svg>
            <span className="text-lg font-semibold tracking-tight">OpenBird</span>
          </Link>
          <div className="order-last w-full sm:order-none sm:ms-auto sm:w-auto">{children}</div>
          <LanguageSwitcher />
        </div>
      </div>
    </header>
  );
}
