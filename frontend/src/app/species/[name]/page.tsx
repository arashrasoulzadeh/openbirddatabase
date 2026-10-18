import Link from 'next/link';
import { Suspense } from 'react';
import { cookies, headers } from 'next/headers';
import { notFound } from 'next/navigation';
import { getFamily, getSpecies } from '@/lib/api';
import SiteHeader from '@/components/SiteHeader';
import TrackedLink from '@/components/TrackedLink';
import IucnBadge from '@/components/IucnBadge';
import HelpTip from '@/components/HelpTip';
import RealmChips from '@/components/RealmChips';
import ScoreBars from '@/components/ScoreBars';
import { taxonLabel } from '@/lib/i18n/taxa';
import SpeciesPhoto from '@/components/SpeciesPhoto';
import { ID_LINKS, fieldHelp, formatMeasurement, helpText, valueHelp, xenoCantoUrl } from '@/lib/i18n/help';
import { LANG_COOKIE, Lang, LOCALES, isLang, langFromAcceptLanguage, nativeName } from '@/lib/i18n/locales';
import { usableName, displayName, fieldLabel, iucnLabel, isCategoricalPath, nameFromNames, nameFromTree, translate, valueLabel } from '@/lib/i18n/translate';

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

const niceLabel = (key: string) => key.replace(/_/g, ' ').replace(/^\w/, (c) => c.toUpperCase());

function Value({ lang, path, value }: { lang: Lang; path: string; value: any }) {
  const name = path.split('.').pop() as string;
  const unit = (k: string) => helpText(lang, `unit.${k}`) ?? k;

  if (path === 'distribution.biogeographic_realms') return <RealmChips values={Array.isArray(value) ? value : [value]} />;

  if (Array.isArray(value)) {
    return (
      <span className="flex flex-wrap justify-end gap-1">
        {value.map((v, i) => {
          if (typeof v === 'object') return <span key={i} className="rounded-md bg-stone-100 px-2 py-0.5 text-xs text-stone-700">{JSON.stringify(v)}</span>;
          if (name === 'xeno_canto_ids') {
            return (
              <a key={i} href={xenoCantoUrl(String(v))} target="_blank" rel="noopener noreferrer" className="rounded-md bg-brand-50 px-2 py-0.5 text-xs text-brand-800 hover:underline">
                XC{String(v).replace(/^XC/i, '')} <span aria-hidden="true" className="inline-block rtl:-scale-x-100">↗</span>
              </a>
            );
          }
          const explanation = isCategoricalPath(path) ? valueHelp(lang, String(v)) : undefined;
          return (
            <span key={i} title={explanation} className={`rounded-md bg-stone-100 px-2 py-0.5 text-xs text-stone-700 ${explanation ? 'cursor-help border-b border-dotted border-stone-400' : ''}`}>
              {valueLabel(lang, path, String(v))}
            </span>
          );
        })}
      </span>
    );
  }
  if (typeof value === 'boolean') return <span>{translate(lang, value ? 'yes' : 'no')}</span>;
  if (typeof value === 'number') {
    const link = ID_LINKS[path];
    if (link) {
      return (
        <a href={link.url(String(value))} target="_blank" rel="noopener noreferrer" className="text-brand-700 hover:underline" title={helpText(lang, 'ui.seeOn')?.replace('{site}', link.site)}>
          {value} <span aria-hidden="true" className="inline-block rtl:-scale-x-100">↗</span>
        </a>
      );
    }
    return <span>{formatMeasurement(lang, path, value, unit)}</span>;
  }
  if (path.endsWith('iucn_status')) {
    const explanation = helpText(lang, `iucn.${value}`);
    return (
      <span className="inline-flex items-center">
        {iucnLabel(lang, String(value))}
        {explanation && <HelpTip text={explanation} align="end" />}
      </span>
    );
  }
  const link = ID_LINKS[path];
  if (link && value) {
    return (
      <a href={link.url(String(value))} target="_blank" rel="noopener noreferrer" className="text-brand-700 hover:underline" title={helpText(lang, 'ui.seeOn')?.replace('{site}', link.site)}>
        {String(value)} <span aria-hidden="true" className="inline-block rtl:-scale-x-100">↗</span>
      </a>
    );
  }
  if (path === 'taxonomy.order' || path === 'taxonomy.family') {
    const local = taxonLabel(lang, String(value));
    return (
      <span>
        {String(value)}
        {local && <span className="ms-2 text-xs font-normal text-stone-400">{local}</span>}
      </span>
    );
  }
  const explanation = isCategoricalPath(path) ? valueHelp(lang, String(value)) : undefined;
  return (
    <span className="inline-flex items-center">
      {valueLabel(lang, path, String(value))}
      {explanation && <HelpTip text={explanation} align="end" />}
    </span>
  );
}

function Label({ lang, path, className = '' }: { lang: Lang; path: string; className?: string }) {
  const help = fieldHelp(lang, path);
  return (
    <span className={className}>
      {fieldLabel(lang, path)}
      {help && <HelpTip text={help} />}
    </span>
  );
}

function Fields({ lang, data, path = '' }: { lang: Lang; data: Record<string, any>; path?: string }) {
  const entries = Object.entries(data).filter(([, v]) => !isEmpty(v));
  return (
    <dl className="grid grid-cols-1 gap-x-6 gap-y-2 md:grid-cols-2">
      {entries.map(([k, v]) => {
        const p = path ? `${path}.${k}` : k;
        const isObject = v && typeof v === 'object' && !Array.isArray(v);

        // Scores become bars: diet importance (0-10) and foraging style shares (0-1)
        if (isObject && (p === 'diet.categories' || p === 'diet.foraging_niches')) {
          const isShare = p === 'diet.foraging_niches';
          const items = Object.entries(v as Record<string, number>)
            .filter(([, n]) => typeof n === 'number' && n > 0)
            .sort(([, x], [, y]) => y - x)
            .map(([key, n]) => ({ label: isShare ? (helpText(lang, `niche.${key}`) ?? niceLabel(key)) : fieldLabel(lang, `${p}.${key}`), value: n }));
          if (!items.length) return null;
          return (
            <div key={k} className="mt-2 md:col-span-2">
              <dt className="mb-2 text-sm font-semibold text-brand-800"><Label lang={lang} path={p} /></dt>
              <dd><ScoreBars items={items} max={isShare ? 1 : 10} format={(n) => (isShare ? `${Math.round(n * 100)}%` : String(n))} /></dd>
            </div>
          );
        }

        return isObject ? (
          <div key={k} className="mt-2 md:col-span-2">
            <dt className="mb-1 text-sm font-semibold text-brand-800"><Label lang={lang} path={p} /></dt>
            <dd className="border-s-2 border-brand-100 ps-3">
              <Fields lang={lang} data={v} path={p} />
            </dd>
          </div>
        ) : (
          <div key={k} className="flex justify-between gap-4 border-b border-stone-100 py-1.5 text-sm">
            <dt className="text-stone-500"><Label lang={lang} path={p} /></dt>
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
    const scientific = sp?.names?.scientific || name;
    const local = displayName(lang, nameFromNames(sp?.names, lang, ''));
    // "Carbonero Común (Parus major) | OpenBird"; just the scientific name when there is no usable common name
    const title = local && local.toLowerCase() !== scientific.toLowerCase() ? `${local} (${scientific}) | OpenBird` : `${scientific} | OpenBird`;
    const description = (helpText(lang, 'ui.speciesDescription') ?? '')
      .replace('{name}', local || scientific)
      .replace('{scientific}', scientific);
    return {
      title,
      description,
      alternates: { canonical: `/species/${encodeURIComponent(name)}` },
      openGraph: { type: 'article', title, description },
    };
  } catch {
    return { title: `${name} | OpenBird` };
  }
}

/** Same-genus species first, then the rest of the family. Streams in after the page; the page works without it. */
async function RelatedSpecies({ taxonomy, scientific, lang, card, h2 }: { taxonomy: any; scientific: string; lang: Lang; card: string; h2: string }) {
  let related: any[] = [];
  try {
    const { order, family, genus } = taxonomy || {};
    if (order && family) {
      const genera = await getFamily(order, family);
      const all = Object.entries(genera).flatMap(([g, list]) => list.map((e: any) => ({ ...e, genus: g })));
      related = all
        .filter((e) => e.scientific !== scientific)
        .sort((a, b) => Number(b.genus === genus) - Number(a.genus === genus))
        .slice(0, 12);
    }
  } catch {
    related = [];
  }
  if (!related.length) return null;
  return (
    <section className={card}>
      <h2 className={h2}>{translate(lang, 'relatedSpecies')}</h2>
      <ul className="grid gap-2 sm:grid-cols-2">
        {related.map((r) => (
          <li key={r.scientific}>
            <TrackedLink
              href={`/species/${encodeURIComponent(r.scientific)}`}
              bird={r.scientific}
              source="related"
              className="block rounded-lg border border-stone-200 px-3 py-2 transition hover:border-brand-300 hover:bg-brand-50"
            >
              <span className="block text-sm font-medium text-stone-900">{displayName(lang, nameFromTree(r, lang))}</span>
              <span className="block text-xs italic text-stone-400" dir="ltr">{r.scientific}</span>
            </TrackedLink>
          </li>
        ))}
      </ul>
    </section>
  );
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

  const { names = {}, sources, last_updated, completeness, ...sections } = sp;
  const topLevel = Object.fromEntries(
    Object.entries(sections).filter(([, v]) => !v || typeof v !== 'object' || Array.isArray(v)),
  );
  const nested = Object.entries(sections).filter(
    ([, v]) => v && typeof v === 'object' && !Array.isArray(v) && !isEmpty(v),
  );
  const localName = displayName(lang, nameFromNames(names, lang, names.scientific || name));

  const english = usableName(names.en);

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
          <div className="flex flex-wrap items-center gap-2">
            <IucnBadge status={status} large />
            {status && helpText(lang, `iucn.${status}`) && <HelpTip text={helpText(lang, `iucn.${status}`) as string} />}
            {sp.conservation?.iucn_tag && (
              <span className="rounded-full bg-white/15 px-3 py-1 text-sm text-white ring-1 ring-inset ring-white/25">
                {valueLabel(lang, 'conservation.iucn_tag', sp.conservation.iucn_tag)}
              </span>
            )}
          </div>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">{localName}</h1>
          {/* original English and scientific names stay visible in every language */}
          {lang !== 'en' && english && english !== localName && (
            <p className="mt-1 text-lg text-brand-100" dir="ltr">{t('englishName')}: {english}</p>
          )}
          <p className="mt-1 text-xl italic text-brand-200" dir="ltr">{names.scientific || name}</p>
          {completeness && (
            <a href="#completeness" className="mt-2 inline-block text-sm text-brand-100 underline-offset-2 hover:underline">
              {t('dataCompleteness')}: {Math.round(completeness.core.score * 100)}%
            </a>
          )}
          <SpeciesPhoto image={sp.image} alt={localName} label={t('photoBy')} />
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

        {completeness && (
          <section id="completeness" className={card}>
            <h2 className={h2}>{t('dataCompleteness')}</h2>
            <div className="flex items-baseline gap-3">
              <span className="text-3xl font-semibold tabular-nums text-brand-800">{Math.round(completeness.core.score * 100)}%</span>
              <span className="text-sm text-stone-500">
                {translate(lang, 'fieldsFilled', { filled: completeness.core.filled, total: completeness.core.total })}
              </span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-stone-100" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(completeness.core.score * 100)}>
              <div className="h-full rounded-full bg-brand-600" style={{ width: `${Math.max(2, completeness.core.score * 100)}%` }} />
            </div>
            {Object.keys(completeness.core.missing).length > 0 && (
              <div className="mt-5">
                <h3 className="text-sm font-semibold text-stone-900">{t('missingInformation')}</h3>
                <p className="mb-3 text-xs text-stone-500">{t('missingInformationHint')}</p>
                <div className="space-y-2">
                  {Object.entries(completeness.core.missing as Record<string, string[]>).map(([section, fields]) => (
                    <details key={section} className="rounded-lg border border-stone-200 px-3 py-2">
                      <summary className="cursor-pointer text-sm font-medium text-stone-700">
                        {fieldLabel(lang, section)}{' '}
                        <span className="text-xs font-normal text-stone-400">({fields.length})</span>
                      </summary>
                      <ul className="mt-2 flex flex-wrap gap-1.5">
                        {fields.map((f) => (
                          <li key={f} className="rounded-md bg-stone-100 px-2 py-0.5 text-xs text-stone-600">
                            {fieldLabel(lang, `${section}.${f}`)}
                          </li>
                        ))}
                      </ul>
                    </details>
                  ))}
                </div>
              </div>
            )}
            {!completeness.expert_verified && <p className="mt-4 text-xs text-stone-500">{t('expertCuratedNote')}</p>}
          </section>
        )}

        <Suspense fallback={null}>
          <RelatedSpecies taxonomy={sp.taxonomy} scientific={names.scientific || name} lang={lang} card={card} h2={h2} />
        </Suspense>

        <section className={card}>
          <h2 className={h2}>{t('identifiersSources')}</h2>
          <Fields lang={lang} data={{ ...topLevel, sources, last_updated }} />
        </section>
      </main>
    </div>
  );
}
