import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getSpecies } from '@/lib/api';

type Props = { params: { name: string } };

const isEmpty = (v: any): boolean =>
  v === null ||
  v === undefined ||
  v === '' ||
  v === 'nan' ||
  (Array.isArray(v) && v.length === 0) ||
  (typeof v === 'object' && !Array.isArray(v) && Object.values(v).every(isEmpty));

const label = (k: string) => k.replace(/_/g, ' ').replace(/^\w/, (c) => c.toUpperCase());

function Value({ value }: { value: any }) {
  if (Array.isArray(value)) {
    return (
      <span className="flex flex-wrap gap-1">
        {value.map((v, i) => (
          <span key={i} className="px-2 py-0.5 bg-gray-100 rounded text-xs">
            {typeof v === 'object' ? JSON.stringify(v) : String(v)}
          </span>
        ))}
      </span>
    );
  }
  if (typeof value === 'boolean') return <span>{value ? 'Yes' : 'No'}</span>;
  if (typeof value === 'number') return <span>{Number.isInteger(value) ? value : value.toFixed(2)}</span>;
  return <span>{String(value)}</span>;
}

function Fields({ data }: { data: Record<string, any> }) {
  const entries = Object.entries(data).filter(([, v]) => !isEmpty(v));
  return (
    <dl className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2">
      {entries.map(([k, v]) =>
        v && typeof v === 'object' && !Array.isArray(v) ? (
          <div key={k} className="md:col-span-2 mt-2">
            <dt className="text-sm font-semibold text-gray-700 mb-1">{label(k)}</dt>
            <dd className="pl-3 border-l-2 border-gray-100">
              <Fields data={v} />
            </dd>
          </div>
        ) : (
          <div key={k} className="flex justify-between gap-4 py-1 border-b border-gray-100 text-sm">
            <dt className="text-gray-600">{label(k)}</dt>
            <dd className="text-gray-900 text-right">
              <Value value={v} />
            </dd>
          </div>
        ),
      )}
    </dl>
  );
}

export async function generateMetadata({ params }: Props) {
  const name = decodeURIComponent(params.name);
  try {
    const sp = await getSpecies(name);
    const en = sp?.names?.en;
    return {
      title: `${en ? en + ' — ' : ''}${name} | OpenBird`,
      description: `${name}${en ? ` (${en})` : ''}: taxonomy, habitat, diet, behavior, breeding and conservation data.`,
    };
  } catch {
    return { title: `${name} | OpenBird` };
  }
}

export default async function SpeciesPage({ params }: Props) {
  const name = decodeURIComponent(params.name);
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

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="font-bold text-gray-900">🐦 OpenBird</Link>
          <Link href="/" className="text-sm text-blue-600 hover:underline">← Search</Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        <section className="bg-white rounded-xl border border-gray-200 p-6">
          <h1 className="text-3xl font-bold text-gray-900">{names.en || names.scientific || name}</h1>
          <p className="italic text-gray-500 text-xl">{names.scientific || name}</p>
          {names.fa && <p className="text-xl text-gray-700 mt-1" dir="rtl">{names.fa}</p>}
        </section>

        {nested.map(([key, value]) => (
          <section key={key} className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-3 pb-2 border-b border-gray-200">{label(key)}</h2>
            <Fields data={value as Record<string, any>} />
          </section>
        ))}

        <section className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3 pb-2 border-b border-gray-200">Names in other languages</h2>
          <Fields data={Object.fromEntries(Object.entries(names).filter(([k]) => k !== 'scientific'))} />
        </section>

        <section className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3 pb-2 border-b border-gray-200">Identifiers & sources</h2>
          <Fields data={{ ...topLevel, sources, last_updated }} />
        </section>
      </main>
    </div>
  );
}
