import type { Metadata } from 'next';
import Link from 'next/link';
import SiteHeader from '@/components/SiteHeader';
import { localePath } from '@/lib/i18n/routes';
import { requestLang } from '@/lib/i18n/server';

export const metadata: Metadata = { title: '404 | OpenBird', robots: { index: false, follow: false } };

export default function NotFound() {
  const lang = requestLang();
  return (
    <div className="min-h-screen bg-stone-50">
      <SiteHeader />
      <main className="mx-auto max-w-xl px-4 py-24 text-center">
        <p className="text-6xl font-semibold text-brand-700">404</p>
        <h1 className="mt-4 text-2xl font-semibold text-brand-900">Page not found</h1>
        <p className="mt-2 text-stone-600">This bird has flown away. Try the search instead.</p>
        <Link href={localePath(lang, '/')} className="mt-6 inline-block rounded-full bg-brand-700 px-6 py-2 text-sm font-medium text-white hover:bg-brand-800">OpenBird</Link>
      </main>
    </div>
  );
}
