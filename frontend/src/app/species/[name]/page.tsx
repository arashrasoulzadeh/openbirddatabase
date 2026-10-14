import Link from 'next/link';
import { cookies, headers } from 'next/headers';
import { notFound } from 'next/navigation';
import { getSpecies } from '@/lib/api';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import { LANG_COOKIE, Lang, LOCALES, isLang, langFromAcceptLanguage, nativeName } from '@/lib/i18n/locales';
import { fieldLabel, iucnLabel, nameFromNames, translate } from '@/lib/i18n/translate';

type Props = { params: { name: string } };

const currentLang = (): Lang => {
  const c = cookies().get(LANG_COOKIE)?.value;
  return isLang(c) ? c : langFromAcceptLanguage(headers().get('accept-language'));
};

const isEmpty = (v: any): boolean =>
  v === null ||
  v === undefined ||
  v === '' ||
  v === 'nan' ||
  (Array.isArray(v) && v.length === 0) ||
  (typeof v === 'object' && !Array.isArray(v) && Object.values(v).every(isEmpty));

function Value({ lang, path, value }: { lang: Lang; path: string; value: any }) {
  if (Array.isArray(value)) {
    return (
      <span className="flex flex-wrap gap-1 justify-end">
        {value.map((v, i) => (
          <span key={i} className="px-2 py-0.5 bg-gray-100 rounded text-xs">
            {typeof v === 'object' ? JSON.stringify(v) : String(v)}
          </span>
        ))}
      </span>
    );
  }
  if (typeof value === 'boolean') return <span>{translate(lang, value ? 'yes' : 'no')}</span>;
  if (typeof value === 'number') return <span>{Number.isInteger(value) ? value : value.toFixed(2)}</span>;
  if (path.endsWith('iucn_status')) return <span>{iucnLabel(lang, String(value))}</span>;
  return <span>{String(value)}</span>;
}

function Fields({ lang, data, path = '' }: { lang: Lang; data: Record<string, any>; path?: string }) {
  const entries = Object.entries(data).filter(([k, v]) => {
    // foraging niche scores are mostly 0; only show the ones that apply
    if (path === 'diet.foraging_niches' && v === 0) return false;
    return !isEmpty(v);
  });
  return (
    <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2">
      {entries.map(([k, v]) => {
        const p = path ? `${path}.${k}` : k;
        return v && typeof v === 'object' && !Array.isArray(v) ? (
          <div key={k} className="md:col-span-2 mt-2">
            <dt className="text-sm font-semibold text-gray-700 mb-1">{fieldLabel(lang, p)}</dt>
            <dd className="ps-3 border-s-2 border-gray-100">
              <Fields lang={lang} data={v} path={p} />
            </dd>
          </div>
        ) : (
          <div key={k} className="flex justify-between gap-4 py-1 border-b border-gray-100 text-sm">
            <dt className="text-gray-600">{fieldLabel(lang, p)}</dt>
            <dd className="text-gray-900 text-end"><Value lang={lang} path={p} value={v} /></dd>
          </div>
        );
      })}
    </dl>
  );
}

export async function generateMetadata({ params }: Props) {
  const name = decodeURIComponent(params.name);
  const lang = currentLang();
  try {
    const sp = await getSpecies(name);
    const local = nameFromNames(sp?.names, lang);
    return {
      title: `${local ? local + ' — ' : ''}${name} | OpenBird`,
      description: `${name}${sp?.names?.en ? ` (${sp.names.en})` : ''}`,
    };
  } catch {
    return { title: `${name} | OpenBird` };
  }
}

export default async function SpeciesPage({ params }: Props) {
  const name = decodeURIComponent(params.name);
  const lang = currentLang();
  const t = (key: string) => translate(lang, key);

  let sp: any;
  try {
    sp = await getSpecies(name);
  } catch {
    notFound();
  }

  const { names = {}, sources, last_updated, ...sections } = sp;
  const topLevel = Object.fromEntries(
    Object.entries(sections).filter(([, v]) => !v || typeof v !== 'object' || Array.isArray(v)),
  );
  const nested = Object.entries(sections).filter(
    ([, v]) => v && typeof v === 'object' && !Array.isArray(v) && !isEmpty(v),
  );
  const localName = nameFromNames(names, lang, names.scientific || name);
  const english = names.en;

  const card = 'bg-white rounded-xl border border-gray-200 p-6';
  const h2 = 'text-lg font-semibold text-gray-900 mb-3 pb-2 border-b border-gray-200';

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between gap-3">
          <Link href="/" className="font-bold text-gray-900">🐦 OpenBird</Link>
          <div className="flex items-center gap-4">
            <LanguageSwitcher />
            <Link href="/" className="text-sm text-blue-600 hover:underline">← {t('backToSearch')}</Link>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        <section className={card}>
          <h1 className="text-3xl font-bold text-gray-900">{localName}</h1>
          {/* original English and scientific names stay visible in every language */}
          {lang !== 'en' && english && english !== localName && (
            <p className="text-lg text-gray-600 mt-1" dir="ltr">{t('englishName')}: {english}</p>
          )}
          <p className="italic text-gray-500 text-xl mt-1" dir="ltr">{names.scientific || name}</p>
          <p className="mt-3 text-xs text-gray-400">{iucnLabel(lang, sp.iucn_status || sp.conservation?.iucn_status)}</p>
        </section>

        {nested.map(([key, value]) => (
          <section key={key} className={card}>
            <h2 className={h2}>{fieldLabel(lang, key)}</h2>
            <Fields lang={lang} data={value as Record<string, any>} path={key} />
          </section>
        ))}

        <section className={card}>
          <h2 className={h2}>{t('namesInOtherLanguages')}</h2>
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2">
            {LOCALES.filter((l) => names[l.code]).map((l) => (
              <div key={l.code} className="flex justify-between gap-4 py-1 border-b border-gray-100 text-sm">
                <dt className="text-gray-600">{nativeName(l.code)}</dt>
                <dd className="text-gray-900 text-end">{names[l.code]}</dd>
              </div>
            ))}
          </dl>
        </section>

        <section className={card}>
          <h2 className={h2}>{t('identifiersSources')}</h2>
          <Fields lang={lang} data={{ ...topLevel, sources, last_updated }} />
        </section>
      </main>
    </div>
  );
}
