import { PALETTE } from './palette';

export interface Slice { label: string; value: number; color?: string }

/** Donut with a legend showing each slice's share. */
export default function Donut({ items, label, empty = 'No data yet' }: { items: Slice[]; label: string; empty?: string }) {
  const total = items.reduce((s, i) => s + i.value, 0);
  if (!total) return <p className="py-6 text-center text-sm text-stone-400">{empty}</p>;
  const r = 38, c = 2 * Math.PI * r;
  let offset = 0;
  return (
    <div className="flex flex-wrap items-center gap-5" dir="ltr">
      <svg viewBox="0 0 100 100" className="h-32 w-32 shrink-0 -rotate-90" role="img" aria-label={label}>
        <circle cx="50" cy="50" r={r} fill="none" stroke="#f5f5f4" strokeWidth="14" />
        {items.map((item, i) => {
          const len = (item.value / total) * c;
          const el = (
            <circle
              key={item.label}
              cx="50" cy="50" r={r} fill="none" strokeWidth="14"
              stroke={item.color ?? PALETTE[i % PALETTE.length]}
              strokeDasharray={`${len} ${c - len}`}
              strokeDashoffset={-offset}
            >
              <title>{`${item.label}: ${item.value.toLocaleString()}`}</title>
            </circle>
          );
          offset += len;
          return el;
        })}
      </svg>
      <ul className="min-w-0 flex-1 space-y-1.5 text-sm">
        {items.map((item, i) => (
          <li key={item.label} className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ background: item.color ?? PALETTE[i % PALETTE.length] }} />
            <span className="truncate text-stone-700">{item.label}</span>
            <span className="ms-auto tabular-nums text-stone-500">{((item.value / total) * 100).toFixed(0)}%</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
