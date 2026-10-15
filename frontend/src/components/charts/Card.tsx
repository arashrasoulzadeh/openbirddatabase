export function Card({ title, subtitle, children, className = '' }: { title: string; subtitle?: string; children: React.ReactNode; className?: string }) {
  return (
    <section className={`rounded-2xl border border-stone-200 bg-white p-4 shadow-sm sm:p-5 ${className}`}>
      <h3 className="text-sm font-semibold text-stone-900">{title}</h3>
      {subtitle && <p className="mb-3 text-xs text-stone-500">{subtitle}</p>}
      {!subtitle && <div className="mb-3" />}
      {children}
    </section>
  );
}

export function Kpi({ label, value, change, invert = false, hint }: { label: string; value: string; change?: number | null; invert?: boolean; hint?: string }) {
  const good = change === null || change === undefined ? null : invert ? change <= 0 : change >= 0;
  return (
    <div className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
      <p className="text-xs font-medium text-stone-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold tabular-nums text-stone-900">{value}</p>
      <p className="mt-1 h-4 text-xs">
        {change !== null && change !== undefined ? (
          <span className={good ? 'text-emerald-600' : 'text-red-600'}>
            {change >= 0 ? '▲' : '▼'} {Math.abs(change) > 999 ? '>999' : Math.abs(change).toLocaleString()}% <span className="text-stone-400">vs previous</span>
          </span>
        ) : (
          <span className="text-stone-400">{hint ?? ''}</span>
        )}
      </p>
    </div>
  );
}
