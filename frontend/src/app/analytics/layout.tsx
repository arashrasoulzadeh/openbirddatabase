import type { Metadata } from 'next';

// The statistics dashboard is for the site owner: keep it out of search results.
export const metadata: Metadata = { title: 'Statistics | OpenBird', robots: { index: false, follow: false } };

export default function AnalyticsLayout({ children }: { children: React.ReactNode }) {
  return children;
}
