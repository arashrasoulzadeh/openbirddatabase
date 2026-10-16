'use client';

import { useEffect, useRef, useState } from 'react';
import { useI18n } from '@/lib/i18n/I18nProvider';
import { helpText } from '@/lib/i18n/help';

interface Props {
  text: string;
  /** Where the popover lines up with the trigger; use "end" for things on the right edge of a row. */
  align?: 'start' | 'end';
  /** A custom trigger (for example a coloured tag). Without it a small "?" button is shown. */
  children?: React.ReactNode;
  className?: string;
}

/** A plain-language explanation that opens on hover, focus or tap and closes on Escape or an outside click. */
export default function HelpTip({ text, align = 'start', children, className = '' }: Props) {
  const { lang } = useI18n();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent | TouchEvent) => {
      if (!ref.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setOpen(false);
    document.addEventListener('mousedown', onDown);
    document.addEventListener('touchstart', onDown);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onDown);
      document.removeEventListener('touchstart', onDown);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  return (
    <span
      ref={ref}
      className={`relative inline-flex align-middle ${className}`}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <button
        type="button"
        aria-label={children ? text : helpText(lang, 'ui.helpLabel')}
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        className={
          children
            ? 'cursor-help rounded-full focus:outline-none focus:ring-2 focus:ring-brand-500'
            : 'ms-1.5 inline-flex h-4 w-4 items-center justify-center rounded-full border border-stone-300 bg-white text-[10px] font-semibold leading-none text-stone-500 hover:border-brand-500 hover:text-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-500'
        }
      >
        {children ?? '?'}
      </button>
      {open && (
        <span
          role="tooltip"
          className={`absolute top-full z-30 mt-1.5 w-64 max-w-[78vw] rounded-lg border border-stone-200 bg-white p-3 text-start text-xs font-normal leading-relaxed text-stone-700 shadow-lg ${
            align === 'end' ? 'end-0' : 'start-0'
          }`}
        >
          {text}
        </span>
      )}
    </span>
  );
}
