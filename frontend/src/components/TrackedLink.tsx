'use client';

import Link from 'next/link';
import { track } from '@/lib/analytics';
import { useI18n } from '@/lib/i18n/I18nProvider';
import { localePath } from '@/lib/i18n/routes';

interface Props {
  href: string;
  bird: string;
  source: 'search' | 'taxonomy' | 'related' | 'random';
  query?: string;
  className?: string;
  children: React.ReactNode;
}

/** A link to a bird page that records which part of the site the click came from. */
export default function TrackedLink({ href, bird, source, query, className, children }: Props) {
  const { lang } = useI18n();
  return (
    <Link href={localePath(lang, href)} className={className} onClick={() => track('bird_click', { bird, source, query: query || undefined })}>
      {children}
    </Link>
  );
}
