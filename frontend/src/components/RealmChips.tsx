'use client';

import { useI18n } from '@/lib/i18n/I18nProvider';
import { REALMS, helpText, splitRealms } from '@/lib/i18n/help';
import HelpTip from './HelpTip';

/** Biogeographic realms as coloured tags with their real names; tap one to see where it is. */
export default function RealmChips({ values }: { values: unknown[] }) {
  const { lang } = useI18n();
  const codes = splitRealms(values);
  if (!codes.length) return <span className="text-sm text-stone-500">{helpText(lang, 'realm.none')}</span>;

  return (
    <div className="flex flex-col items-end gap-2 sm:items-end">
      <ul className="flex flex-wrap justify-end gap-1.5">
        {codes.map((code) => {
          const realm = REALMS[code];
          return (
            <li key={code}>
              <HelpTip text={helpText(lang, `realm.${code}.about`) ?? ''} align="end">
                <span
                  className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium"
                  style={{ borderColor: `${realm.color}55`, background: `${realm.color}12`, color: realm.color }}
                >
                  <span aria-hidden="true">{realm.emoji}</span>
                  {helpText(lang, `realm.${code}.name`)}
                </span>
              </HelpTip>
            </li>
          );
        })}
      </ul>
      <p className="max-w-xs text-end text-xs text-stone-400">{helpText(lang, 'realm.intro')}</p>
    </div>
  );
}
