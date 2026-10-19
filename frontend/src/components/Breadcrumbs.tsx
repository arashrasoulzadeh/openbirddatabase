import Link from 'next/link';

export interface Crumb {
  label: string;
  href?: string; // the last crumb (the current page) has none
}

/** Visible breadcrumb trail; the separator mirrors in right-to-left languages. Pairs with the BreadcrumbList JSON-LD. */
export default function Breadcrumbs({ items, label, light }: { items: Crumb[]; label: string; light?: boolean }) {
  return (
    <nav aria-label={label}>
      <ol className={`flex flex-wrap items-center gap-x-1.5 gap-y-1 text-sm ${light ? 'text-brand-100' : 'text-stone-500'}`}>
        {items.map((c, i) => (
          <li key={i} className="flex items-center gap-1.5">
            {i > 0 && <span aria-hidden="true" className="inline-block rtl:-scale-x-100">›</span>}
            {c.href ? (
              <Link href={c.href} className="hover:underline">{c.label}</Link>
            ) : (
              <span aria-current="page" className="font-medium">{c.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
