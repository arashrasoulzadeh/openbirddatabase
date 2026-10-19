import type { Metadata } from 'next';
import { notFound, permanentRedirect } from 'next/navigation';
import Breadcrumbs from '@/components/Breadcrumbs';
import JsonLd from '@/components/JsonLd';
import SiteHeader from '@/components/SiteHeader';
import SpeciesLink from '@/components/SpeciesLink';
import { SITE_URL } from '@/lib/config';
import { localePath } from '@/lib/i18n/routes';
import { requestLang } from '@/lib/i18n/server';
import { taxonLabel } from '@/lib/i18n/taxa';
import { displayName, nameFromTree } from '@/lib/i18n/translate';
import { absoluteUrl, clip, pageMetadata } from '@/lib/seo';
import { SpeciesEntry, fill, loadTree, matchKey } from '@/lib/taxon-pages';

type Props = { params: { order: string; family: string } };
const orderPath = (order: string) => `/order/${encodeURIComponent(order)}`;
const familyPath = (order: string, family: string) => `/family/${encodeURIComponent(order)}/${encodeURIComponent(family)}`;

async function resolve(params: Props['params']) {
  const lang = requestLang();
  const tree = await loadTree(lang);
  const wantedOrder = decodeURIComponent(params.order);
  const wantedFamily = decodeURIComponent(params.family);
  const order = matchKey(Object.keys(tree), wantedOrder);
  const family = order ? matchKey(Object.keys(tree[order]), wantedFamily) : undefined;
  if (!order || !family) notFound();
  if (order !== wantedOrder || family !== wantedFamily) permanentRedirect(localePath(lang, familyPath(order, family)));
  const species: (SpeciesEntry & { genus: string })[] = Object.entries(tree[order][family]).flatMap(([genus, list]) => list.map((e) => ({ ...e, genus })));
  species.sort((a, b) => a.scientific.localeCompare(b.scientific));
  return { lang, order, family, species };
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  try {
    const { lang, order, family, species } = await resolve(params);
    const vars = { name: taxonLabel(lang, family) || family, latin: family, n: species.length };
    return pageMetadata({
      lang,
      path: familyPath(order, family),
      title: fill(lang, 'seo.taxonTitle', vars),
      description: clip(fill(lang, 'seo.taxonDescription', vars)),
    });
  } catch {
    return { title: 'OpenBird', robots: { index: false, follow: false } };
  }
}

export default async function FamilyPage({ params }: Props) {
  const { lang, order, family, species } = await resolve(params);
  const name = taxonLabel(lang, family) || family;
  const orderName = taxonLabel(lang, order) || order;
  const url = absoluteUrl(lang, familyPath(order, family));
  const crumbs = [
    { label: 'OpenBird', href: localePath(lang, '/') },
    { label: orderName, href: localePath(lang, orderPath(order)) },
    { label: name },
  ];
  const label = (e: SpeciesEntry) => displayName(lang, nameFromTree(e, lang));
  return (
    <div className="min-h-screen bg-stone-50">
      <JsonLd
        data={{
          '@context': 'https://schema.org',
          '@graph': [
            { '@type': 'CollectionPage', '@id': `${url}#webpage`, url, name: `${name} (${family})`, inLanguage: lang, isPartOf: { '@id': `${SITE_URL}/#website` }, breadcrumb: { '@id': `${url}#breadcrumb` } },
            { '@type': 'BreadcrumbList', '@id': `${url}#breadcrumb`, itemListElement: crumbs.map((c, i) => ({ '@type': 'ListItem', position: i + 1, name: c.label, item: c.href ? SITE_URL + c.href : url })) },
            {
              '@type': 'ItemList',
              numberOfItems: species.length,
              itemListElement: species.slice(0, 200).map((s, i) => ({ '@type': 'ListItem', position: i + 1, url: absoluteUrl(lang, `/species/${encodeURIComponent(s.scientific)}`), name: s.scientific })),
            },
          ],
        }}
      />
      <SiteHeader />
      <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
        <Breadcrumbs label={fill(lang, 'taxon.breadcrumb') || 'Breadcrumb'} items={crumbs} />
        <h1 className="mt-4 text-3xl font-semibold tracking-tight text-brand-900 sm:text-4xl">{name}</h1>
        <p className="mt-1 text-lg italic text-stone-500" dir="ltr">{family}</p>
        <p className="mt-4 max-w-3xl text-stone-700">{fill(lang, 'taxon.familyIntro', { name, latin: family, order: orderName, species: species.length })}</p>
        <ul className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {species.map((s) => (
            <li key={s.scientific}>
              <SpeciesLink scientific={s.scientific} className="block h-full rounded-xl border border-stone-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-md">
                <span className="block font-semibold text-brand-800">{label(s) || s.scientific}</span>
                <span className="block text-sm italic text-stone-500" dir="ltr">{s.scientific}</span>
              </SpeciesLink>
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
}
