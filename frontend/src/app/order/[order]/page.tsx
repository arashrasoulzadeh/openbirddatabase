import type { Metadata } from 'next';
import Link from 'next/link';
import { notFound, permanentRedirect } from 'next/navigation';
import Breadcrumbs from '@/components/Breadcrumbs';
import JsonLd from '@/components/JsonLd';
import SiteHeader from '@/components/SiteHeader';
import { SITE_URL } from '@/lib/config';
import { localePath } from '@/lib/i18n/routes';
import { requestLang } from '@/lib/i18n/server';
import { taxonLabel } from '@/lib/i18n/taxa';
import { absoluteUrl, clip, pageMetadata } from '@/lib/seo';
import { familiesOf, fill, loadTree, matchKey } from '@/lib/taxon-pages';

type Props = { params: { order: string } };
const orderPath = (order: string) => `/order/${encodeURIComponent(order)}`;
const familyPath = (order: string, family: string) => `/family/${encodeURIComponent(order)}/${encodeURIComponent(family)}`;

async function resolve(params: Props['params']) {
  const lang = requestLang();
  const tree = await loadTree(lang);
  const wanted = decodeURIComponent(params.order);
  const order = matchKey(Object.keys(tree), wanted);
  if (!order) notFound();
  if (order !== wanted) permanentRedirect(localePath(lang, orderPath(order))); // one URL per page: canonical capitalisation
  const families = familiesOf(tree, order);
  return { lang, order, families, species: families.reduce((n, f) => n + f.species, 0) };
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  try {
    const { lang, order, families, species } = await resolve(params);
    const name = taxonLabel(lang, order) || order;
    const vars = { name, latin: order, n: species };
    return pageMetadata({
      lang,
      path: orderPath(order),
      title: fill(lang, 'seo.taxonTitle', vars),
      description: clip(fill(lang, 'seo.taxonDescription', vars) + ` ${fill(lang, 'taxon.familiesCount', { n: families.length })}.`),
    });
  } catch {
    return { title: 'OpenBird', robots: { index: false, follow: false } };
  }
}

export default async function OrderPage({ params }: Props) {
  const { lang, order, families, species } = await resolve(params);
  const name = taxonLabel(lang, order) || order;
  const url = absoluteUrl(lang, orderPath(order));
  const crumbs = [{ label: 'OpenBird', href: localePath(lang, '/') }, { label: name }];
  return (
    <div className="min-h-screen bg-stone-50">
      <JsonLd
        data={{
          '@context': 'https://schema.org',
          '@graph': [
            { '@type': 'CollectionPage', '@id': `${url}#webpage`, url, name: `${name} (${order})`, inLanguage: lang, isPartOf: { '@id': `${SITE_URL}/#website` }, breadcrumb: { '@id': `${url}#breadcrumb` } },
            { '@type': 'BreadcrumbList', '@id': `${url}#breadcrumb`, itemListElement: crumbs.map((c, i) => ({ '@type': 'ListItem', position: i + 1, name: c.label, item: c.href ? SITE_URL + c.href : url })) },
            { '@type': 'ItemList', itemListElement: families.map((f, i) => ({ '@type': 'ListItem', position: i + 1, url: absoluteUrl(lang, familyPath(order, f.name)), name: taxonLabel(lang, f.name) || f.name })) },
          ],
        }}
      />
      <SiteHeader />
      <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
        <Breadcrumbs label={fill(lang, 'taxon.breadcrumb') || 'Breadcrumb'} items={crumbs} />
        <h1 className="mt-4 text-3xl font-semibold tracking-tight text-brand-900 sm:text-4xl">{name}</h1>
        <p className="mt-1 text-lg italic text-stone-500" dir="ltr">{order}</p>
        <p className="mt-4 max-w-3xl text-stone-700">{fill(lang, 'taxon.orderIntro', { name, latin: order, families: families.length, species })}</p>
        <ul className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {families.map((f) => (
            <li key={f.name}>
              <Link
                href={localePath(lang, familyPath(order, f.name))}
                className="block h-full rounded-xl border border-stone-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-md"
              >
                <span className="block font-semibold text-brand-800">{taxonLabel(lang, f.name) || f.name}</span>
                <span className="block text-sm italic text-stone-500" dir="ltr">{f.name}</span>
                <span className="mt-1 block text-sm text-stone-600">{fill(lang, 'taxon.speciesCount', { n: f.species })}</span>
              </Link>
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
}

