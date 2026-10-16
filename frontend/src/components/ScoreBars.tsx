interface Item {
  label: string;
  value: number;
}

/** Horizontal bars for scores such as diet shares. `max` is the value that fills the whole bar. */
export default function ScoreBars({ items, max, format }: { items: Item[]; max: number; format: (v: number) => string }) {
  return (
    <ul className="space-y-1.5">
      {items.map((item) => (
        <li key={item.label} className="grid grid-cols-[minmax(0,9rem)_1fr_3rem] items-center gap-3 text-sm sm:grid-cols-[minmax(0,12rem)_1fr_3.5rem]">
          <span className="truncate text-stone-600" title={item.label}>{item.label}</span>
          <span className="h-2 overflow-hidden rounded-full bg-stone-100" aria-hidden="true">
            <span className="block h-full rounded-full bg-brand-500" style={{ width: `${Math.max(3, Math.min(100, (item.value / max) * 100))}%` }} />
          </span>
          <span className="text-end font-medium tabular-nums text-stone-900">{format(item.value)}</span>
        </li>
      ))}
    </ul>
  );
}
