import Link from 'next/link';

export interface BarItem { label: string; value: number; hint?: string; href?: string }

interface Props {
  items: BarItem[];
  color?: string;
  max?: number;
  format?: (v: number) => string;
  empty?: string;
}

/** Horizontal bars with the label on the left and the value on the right. */
export default function BarList({ items, color = '#2f664b', max, format = (v) => v.toLocaleString(), empty = 'No data yet' }: Props) {
  if (!items.length) return <p className="py-6 text-center text-sm text-stone-400">{empty}</p>;
  const top = max ?? Math.max(...items.map((i) => i.value), 1);
  return (
    <ul className="space-y-2" dir="ltr">
      {items.map((item) => {
        const label = (
          <span className="truncate text-sm text-stone-700" title={item.label}>
            {item.label}
            {item.hint && <span className="ms-2 text-xs text-stone-400">{item.hint}</span>}
          </span>
        );
        return (
          <li key={item.label} className="grid grid-cols-[minmax(0,12rem)_1fr_auto] items-center gap-3 sm:grid-cols-[minmax(0,14rem)_1fr_auto]">
            {item.href ? <Link href={item.href} className="truncate hover:underline">{label}</Link> : label}
            <span className="h-2 overflow-hidden rounded-full bg-stone-100">
              <span className="block h-full rounded-full" style={{ width: `${Math.max(2, (item.value / top) * 100)}%`, background: color }} />
            </span>
            <span className="w-14 text-end text-sm font-medium tabular-nums text-stone-900">{format(item.value)}</span>
          </li>
        );
      })}
    </ul>
  );
}
