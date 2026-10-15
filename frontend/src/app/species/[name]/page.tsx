import Link from 'next/link';
import { cookies, headers } from 'next/headers';
import { notFound } from 'next/navigation';
import { getSpecies } from '@/lib/api';
import SiteHeader from '@/components/SiteHeader';
import IucnBadge from '@/components/IucnBadge';
import { LANG_COOKIE, Lang, LOCALES, isLang, langFromAcceptLanguage, nativeName } from '@/lib/i18n/locales';
import { fieldLabel, iucnLabel, nameFromNames, translate, valueLabel } from '@/lib/i18n/translate';

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
          <span key={i} className="rounded-md bg-stone-100 px-2 py-0.5 text-xs text-stone-700">
            {typeof v === 'object' ? JSON.stringify(v) : valueLabel(lang, path, String(v))}
          </span>
        ))}
      </span>
    );
  }
  if (typeof value === 'boolean') return <span>{translate(lang, value ? 'yes' : 'no')}</span>;
  if (typeof value === 'number') return <span>{Number.isInteger(value) ? value : value.toFixed(2)}</span>;
  if (path.endsWith('iucn_status')) return <span>{iucnLabel(lang, String(value))}</span>;
  return <span>{valueLabel(lang, path, String(value))}</span>;
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
            <dt className="mb-1 text-sm font-semibold text-brand-800">{fieldLabel(lang, p)}</dt>
            <dd className="border-s-2 border-brand-100 ps-3">
              <Fields lang={lang} data={v} path={p} />
            </dd>
          </div>
        ) : (
          <div key={k} className="flex justify-between gap-4 border-b border-stone-100 py-1.5 text-sm">
            <dt className="text-stone-500">{fieldLabel(lang, p)}</dt>
            <dd className="text-end font-medium text-stone-900"><Value lang={lang} path={p} value={v} /></dd>
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
      alternates: { canonical: `/species/${encodeURIComponent(name)}` },
      openGraph: { type: 'article', title: `${local || name} — ${name}` },
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

  const card = 'scroll-mt-24 rounded-2xl border border-stone-200 bg-white p-5 shadow-sm sm:p-6';
  const h2 = 'mb-3 border-b border-stone-100 pb-2 text-lg font-semibold text-brand-900';

  // Quick facts shown as tiles under the title
  const facts: [string, string][] = [];
  const mass = sp.morphology?.body_mass_g;
  if (typeof mass === 'number') facts.push([fieldLabel(lang, 'morphology.body_mass_g'), `${mass >= 100 ? Math.round(mass) : mass.toFixed(1)} g`]);
  if (sp.habitat?.primary) facts.push([fieldLabel(lang, 'habitat.primary'), valueLabel(lang, 'habitat.primary', sp.habitat.primary)]);
  if (sp.diet?.primary) facts.push([fieldLabel(lang, 'diet.primary'), valueLabel(lang, 'diet.primary', sp.diet.primary)]);
  if (sp.behavior?.migration_status) facts.push([fieldLabel(lang, 'behavior.migration_status'), valueLabel(lang, 'behavior.migration_status', sp.behavior.migration_status)]);
  const status = sp.iucn_status || sp.conservation?.iucn_status;

  return (
    <div className="min-h-screen bg-stone-50">
      <SiteHeader>
        <Link href="/" className="inline-flex items-center gap-1 text-sm font-medium text-brand-700 hover:underline">
          <span aria-hidden="true" className="rtl:rotate-180">←</span> {t('backToSearch')}
        </Link>
      </SiteHeader>

      <section className="bg-gradient-to-b from-brand-800 to-brand-700 text-white">
        <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 sm:py-10">
          <IucnBadge status={status} large />
          <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">{localName}</h1>
          {/* original English and scientific names stay visible in every language */}
          {lang !== 'en' && english && english !== localName && (
            <p className="mt-1 text-lg text-brand-100" dir="ltr">{t('englishName')}: {english}</p>
          )}
          <p className="mt-1 text-xl italic text-brand-200" dir="ltr">{names.scientific || name}</p>
          {facts.length > 0 && (
            <dl className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
              {facts.map(([label, value]) => (
                <div key={label} className="rounded-xl bg-white/10 px-3 py-2 ring-1 ring-white/15">
                  <dt className="text-xs text-brand-100">{label}</dt>
                  <dd className="truncate text-base font-semibold">{value}</dd>
                </div>
              ))}
            </dl>
          )}
        </div>
      </section>

      <main className="mx-auto max-w-4xl space-y-5 px-4 py-6 sm:px-6">
        <nav aria-label="Sections" className="-mx-4 flex gap-2 overflow-x-auto px-4 pb-1 scrollbar-hide sm:mx-0 sm:flex-wrap sm:px-0">
          {nested.map(([key]) => (
            <a
              key={key}
              href={`#${key}`}
              className="shrink-0 rounded-full border border-stone-200 bg-white px-3 py-1 text-sm text-stone-600 hover:border-brand-300 hover:text-brand-800"
            >
              {fieldLabel(lang, key)}
            </a>
          ))}
        </nav>

        {nested.map(([key, value]) => (
          <section key={key} id={key} className={card}>
            <h2 className={h2}>{fieldLabel(lang, key)}</h2>
            <Fields lang={lang} data={value as Record<string, any>} path={key} />
          </section>
        ))}

        <section className={card}>
          <h2 className={h2}>{t('namesInOtherLanguages')}</h2>
          <dl className="grid grid-cols-1 gap-x-6 gap-y-1 sm:grid-cols-2">
            {LOCALES.filter((l) => names[l.code]).map((l) => (
              <div key={l.code} className="flex justify-between gap-4 border-b border-stone-100 py-1.5 text-sm">
                <dt className="text-stone-500">{nativeName(l.code)}</dt>
                <dd className="text-end font-medium text-stone-900">{names[l.code]}</dd>
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
