'use client';

import { useI18n } from '@/lib/i18n/I18nProvider';
import { iucnLabel } from '@/lib/i18n/translate';

const STYLE: Record<string, { chip: string; dot: string }> = {
  LC: { chip: 'bg-emerald-50 text-emerald-800 ring-emerald-200', dot: 'bg-emerald-500' },
  NT: { chip: 'bg-lime-50 text-lime-800 ring-lime-200', dot: 'bg-lime-500' },
  VU: { chip: 'bg-amber-50 text-amber-800 ring-amber-200', dot: 'bg-amber-500' },
  EN: { chip: 'bg-orange-50 text-orange-800 ring-orange-200', dot: 'bg-orange-500' },
  CR: { chip: 'bg-red-50 text-red-800 ring-red-200', dot: 'bg-red-500' },
  EW: { chip: 'bg-purple-50 text-purple-800 ring-purple-200', dot: 'bg-purple-500' },
  EX: { chip: 'bg-stone-100 text-stone-700 ring-stone-300', dot: 'bg-stone-700' },
  DD: { chip: 'bg-slate-50 text-slate-600 ring-slate-200', dot: 'bg-slate-400' },
};

export default function IucnBadge({ status, large = false }: { status?: string | null; large?: boolean }) {
  const { lang } = useI18n();
  if (!status) return null;
  const style = STYLE[status] ?? STYLE.DD;
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full ring-1 ring-inset font-medium whitespace-nowrap ${style.chip} ${
        large ? 'px-3 py-1 text-sm' : 'px-2 py-0.5 text-xs'
      }`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} aria-hidden="true" />
      {iucnLabel(lang, status)}
    </span>
  );
}
