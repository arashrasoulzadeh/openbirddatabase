'use client';

import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';
import { API_URL } from '@/lib/config';
import { nativeName } from '@/lib/i18n/locales';
import { fieldLabel } from '@/lib/i18n/translate';
import BarList from '@/components/charts/BarList';
import { Card, Kpi } from '@/components/charts/Card';
import Columns from '@/components/charts/Columns';
import Donut from '@/components/charts/Donut';
import LineChart, { Series } from '@/components/charts/LineChart';
import { PALETTE } from '@/components/charts/palette';

const RANGES = [
  { days: 1, label: '24 hours' },
  { days: 7, label: '7 days' },
  { days: 30, label: '30 days' },
  { days: 90, label: '90 days' },
];
const TOKEN_KEY = 'ob_analytics_token';
const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const EVENT_NAMES: Record<string, string> = {
  pageview: 'Page views', page_leave: 'Page leaves', bird_click: 'Bird clicks', search: 'Searches', filter: 'Filter uses',
  language_change: 'Language changes', tab_view: 'Taxonomy tab opens', load_more: 'Load more', random_bird: 'Random bird',
};

const fmt = (n: number | null | undefined) => (n === null || n === undefined ? '–' : n.toLocaleString());
const pct = (v: number) => `${(v * 100).toFixed(v >= 0.995 || v === 0 ? 0 : 1)}%`;
const lang = (code: string) => (code && code !== 'unknown' ? `${nativeName(code)} (${code})` : 'unknown');
const decodeName = (path: string) => { try { return decodeURIComponent(path); } catch { return path; } };

function duration(sec: number | null | undefined): string {
  if (sec === null || sec === undefined) return '–';
  const s = Math.round(sec);
  return s >= 60 ? `${Math.floor(s / 60)}m ${s % 60}s` : `${s}s`;
}

function formatT(t: number, step: number): string {
  const d = new Date(t * 1000);
  const day = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' });
  return step < 86400 ? `${day} ${String(d.getUTCHours()).padStart(2, '0')}:00` : day;
}

function ago(ts: number): string {
  const s = Math.max(0, Math.round(Date.now() / 1000 - ts));
  return s < 60 ? `${s}s ago` : s < 3600 ? `${Math.floor(s / 60)}m ago` : `${Math.floor(s / 3600)}h ago`;
}

async function api(path: string, token: string) {
  const res = await fetch(`${API_URL}/analytics/${path}`, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
  if (res.status === 401) throw new Error('401');
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}

export default function AnalyticsPage() {
  const [days, setDays] = useState(30);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState('');
  const [token, setToken] = useState('');
  const [needsToken, setNeedsToken] = useState(false);
  const [auto, setAuto] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);
  const [detail, setDetail] = useState<any>(null);
  const [addedBy, setAddedBy] = useState<'by_day' | 'by_hour'>('by_day');

  useEffect(() => {
    try { setToken(sessionStorage.getItem(TOKEN_KEY) || ''); } catch { /* storage blocked */ }
  }, []);

  const load = useCallback(async () => {
    try {
      setData(await api(`dashboard?days=${days}`, token));
      setError('');
      setNeedsToken(false);
    } catch (e: any) {
      if (e.message === '401') setNeedsToken(true);
      else setError('Could not load analytics. Is the API reachable?');
    }
  }, [days, token]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    if (!auto) return;
    const id = setInterval(load, 60000);
    return () => clearInterval(id);
  }, [auto, load]);

  // Detail for the selected page (bird pages also get click sources and the searches that led to them)
  useEffect(() => {
    if (!selected) { setDetail(null); return; }
    const isBird = selected.startsWith('/species/');
    const path = isBird
      ? `birds/${encodeURIComponent(decodeName(selected.slice(9)))}?days=${days}`
      : `page?path=${encodeURIComponent(selected)}&days=${days}`;
    api(path, token).then(setDetail).catch(() => setDetail(null));
  }, [selected, days, token]);

  if (needsToken) {
    return (
      <main className="mx-auto flex min-h-screen max-w-sm flex-col justify-center gap-4 p-6">
        <h1 className="text-xl font-semibold text-stone-900">Analytics</h1>
        <p className="text-sm text-stone-600">Enter the analytics token (<code>ANALYTICS_TOKEN</code> in the server's .env).</p>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const value = (new FormData(e.currentTarget).get('token') as string).trim();
            try { sessionStorage.setItem(TOKEN_KEY, value); } catch { /* ignore */ }
            setToken(value);
          }}
          className="flex gap-2"
        >
          <input name="token" type="password" autoFocus className="min-w-0 flex-1 rounded-lg border border-stone-300 px-3 py-2" placeholder="Token" />
          <button className="rounded-lg bg-brand-700 px-4 py-2 text-white hover:bg-brand-800">Open</button>
        </form>
        {token && <p className="text-sm text-red-600">That token was not accepted.</p>}
      </main>
    );
  }

  if (!data) {
    return <main className="p-10 text-center text-stone-500">{error || 'Loading analytics...'}</main>;
  }

  const { summary: s, series, top, content } = data;
  const step: number = data.step;
  const fx = (t: number) => formatT(t, step);
  const seriesOf = (names: [string, string, boolean?][]): Series[] =>
    names.map(([key, name, area], i) => ({ name, color: PALETTE[i], points: series[key], area: area ?? i === 0 }));

  return (
    <div className="min-h-screen bg-stone-50">
      <header className="sticky top-0 z-30 border-b border-stone-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-3 px-4 py-3 sm:px-6">
          <Link href="/" className="text-sm text-brand-700 hover:underline"><span aria-hidden="true" className="inline-block rtl:rotate-180">←</span> OpenBird</Link>
          <h1 className="text-lg font-semibold text-stone-900">Analytics</h1>
          <div className="ms-auto flex flex-wrap items-center gap-2">
            <div className="flex rounded-lg bg-stone-100 p-0.5">
              {RANGES.map((r) => (
                <button
                  key={r.days}
                  onClick={() => setDays(r.days)}
                  className={`rounded-md px-3 py-1 text-sm ${days === r.days ? 'bg-white font-medium text-stone-900 shadow-sm' : 'text-stone-600'}`}
                >
                  {r.label}
                </button>
              ))}
            </div>
            <label className="flex items-center gap-1.5 text-xs text-stone-500">
              <input type="checkbox" checked={auto} onChange={(e) => setAuto(e.target.checked)} /> Auto-refresh
            </label>
            <button onClick={load} className="rounded-lg border border-stone-300 px-3 py-1 text-sm hover:bg-stone-50">Refresh</button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-6 px-4 py-6 sm:px-6">
        {/* Live */}
        <section className="rounded-2xl bg-brand-800 p-4 text-white sm:p-5">
          <div className="flex flex-wrap items-center gap-3">
            <span className="relative flex h-3 w-3"><span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-300 opacity-75" /><span className="relative inline-flex h-3 w-3 rounded-full bg-emerald-400" /></span>
            <p className="text-lg font-semibold">{fmt(data.live.active_visitors)} visitor{data.live.active_visitors === 1 ? '' : 's'} in the last 5 minutes</p>
          </div>
          {data.live.latest.length > 0 && (
            <ul className="mt-3 grid gap-x-6 gap-y-1 text-xs text-brand-100 sm:grid-cols-2" dir="ltr">
              {data.live.latest.slice(0, 8).map((e: any, i: number) => (
                <li key={i} className="truncate">
                  <span className="text-brand-300">{ago(e.ts)}</span>{' '}
                  {EVENT_NAMES[e.type] || e.type}
                  {e.bird ? ` · ${e.bird}` : e.query ? ` · “${e.query}”` : e.path ? ` · ${decodeName(e.path)}` : ''}
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* KPIs */}
        <section className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-5">
          <Kpi label="Page views" value={fmt(s.pageviews.value)} change={s.pageviews.change} />
          <Kpi label="Visitors" value={fmt(s.visitors.value)} change={s.visitors.change} />
          <Kpi label="Sessions" value={fmt(s.sessions.value)} change={s.sessions.change} />
          <Kpi label="Searches" value={fmt(s.searches.value)} change={s.searches.change} />
          <Kpi label="Bird clicks" value={fmt(s.bird_clicks.value)} change={s.bird_clicks.change} />
          <Kpi label="Bird page views" value={fmt(s.bird_views.value)} change={s.bird_views.change} />
          <Kpi label="Avg. time on page" value={duration(s.avg_time_on_page)} hint="visible time, idle capped" />
          <Kpi label="Bounce rate" value={s.bounce_rate === null ? '–' : `${s.bounce_rate}%`} hint="sessions with 1 page" />
          <Kpi label="Searches with no result" value={fmt(s.zero_result_searches)} hint={s.searches.value ? `${((s.zero_result_searches / s.searches.value) * 100).toFixed(1)}% of searches` : ''} />
          <Kpi label="Language changes" value={fmt(s.language_changes)} />
        </section>

        {/* Traffic */}
        <Card title="Traffic over time" subtitle={`Page views and unique visitors per ${step < 86400 ? 'hour' : 'day'} (UTC)`}>
          <LineChart series={seriesOf([['pageviews', 'Page views'], ['visitors', 'Visitors', true]])} formatX={fx} label="Page views and visitors over time" />
        </Card>
        <div className="grid gap-6 lg:grid-cols-2">
          <Card title="Home page views" subtitle="Views of the search/home page over time">
            <LineChart series={seriesOf([['home_views', 'Home views']])} formatX={fx} height={180} label="Home page views over time" />
          </Card>
          <Card title="Bird page views" subtitle="Views of individual bird pages over time">
            <LineChart series={seriesOf([['bird_views', 'Bird page views']])} formatX={fx} height={180} label="Bird page views over time" />
          </Card>
          <Card title="Searches" subtitle="Searches with text, per period">
            <LineChart series={seriesOf([['searches', 'Searches']])} formatX={fx} height={180} label="Searches over time" />
          </Card>
          <Card title="Bird clicks" subtitle="Clicks on a bird from search, taxonomy, related species or the random button">
            <LineChart series={seriesOf([['bird_clicks', 'Bird clicks']])} formatX={fx} height={180} label="Bird clicks over time" />
          </Card>
        </div>

        {/* Birds & searches */}
        <div className="grid gap-6 lg:grid-cols-2">
          <Card title="Most viewed birds" subtitle="Bird page views in the period">
            <BarList items={top.birds.map((b: any) => ({ label: b.name, value: b.views, hint: `${b.visitors} visitors`, href: `/species/${encodeURIComponent(b.name)}` }))} />
          </Card>
          <Card title="Most clicked birds" subtitle="Clicks on a bird, wherever it was listed">
            <BarList color="#d97706" items={top.bird_clicks.map((b: any) => ({ label: b.name, value: b.clicks, href: `/species/${encodeURIComponent(b.name)}` }))} />
          </Card>
          <Card title="Top searches" subtitle="What people look for (average number of results in brackets)">
            <BarList color="#0284c7" items={top.searches.map((q: any) => ({ label: q.query, value: q.count, hint: `~${q.avg_results} results` }))} />
          </Card>
          <Card title="Searches with no result" subtitle="Content gaps: people searched for these and found nothing">
            <BarList color="#e11d48" items={top.zero_result_searches.map((q: any) => ({ label: q.query, value: q.count }))} empty="Every search found something" />
          </Card>
          <Card title="Where bird clicks come from">
            <Donut label="Bird click sources" items={top.bird_click_sources.map((x: any) => ({ label: x.name, value: x.count }))} />
          </Card>
          <Card title="Filters used" subtitle="Most used filter values">
            <BarList color="#7c3aed" items={top.filters.map((f: any) => ({ label: `${f.field.replace(/_/g, ' ')}: ${f.value}`, value: f.count }))} empty="No filters used yet" />
          </Card>
        </div>

        {/* Pages */}
        <Card title="Pages" subtitle="Views per page. Click a row to see its history.">
          <div className="overflow-x-auto" dir="ltr">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-stone-200 text-start text-xs text-stone-500">
                  <th className="py-2 pe-3 text-start font-medium">Page</th>
                  <th className="px-3 text-end font-medium">Views</th>
                  <th className="px-3 text-end font-medium">Visitors</th>
                  <th className="ps-3 text-end font-medium">Avg. time</th>
                </tr>
              </thead>
              <tbody>
                {top.pages.map((p: any) => (
                  <tr
                    key={p.path}
                    onClick={() => setSelected(selected === p.path ? null : p.path)}
                    className={`cursor-pointer border-b border-stone-100 hover:bg-brand-50 ${selected === p.path ? 'bg-brand-50' : ''}`}
                  >
                    <td className="max-w-xs truncate py-2 pe-3 text-stone-800" title={decodeName(p.path)}>{decodeName(p.path)}</td>
                    <td className="px-3 text-end tabular-nums">{fmt(p.views)}</td>
                    <td className="px-3 text-end tabular-nums">{fmt(p.visitors)}</td>
                    <td className="ps-3 text-end tabular-nums">{duration(p.avg_time)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {detail && selected && (
            <div className="mt-5 rounded-xl border border-stone-200 p-4">
              <div className="mb-3 flex flex-wrap items-baseline gap-x-6 gap-y-1">
                <h4 className="font-semibold text-stone-900">{decodeName(selected)}</h4>
                <span className="text-sm text-stone-500">{fmt(detail.views)} views · {fmt(detail.visitors)} visitors · {duration(detail.avg_time_on_page)} average</span>
                {detail.clicks !== undefined && <span className="text-sm text-stone-500">{fmt(detail.clicks)} clicks</span>}
              </div>
              <LineChart
                series={[
                  { name: 'Views', color: PALETTE[0], points: detail.views_series || detail.series, area: true },
                  ...(detail.clicks_series ? [{ name: 'Clicks', color: PALETTE[1], points: detail.clicks_series }] : []),
                ]}
                formatX={fx}
                height={170}
                label="History of the selected page"
              />
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                {(detail.click_sources?.length > 0) && (
                  <div><p className="mb-2 text-xs font-medium text-stone-500">Clicks came from</p><BarList items={detail.click_sources.map((x: any) => ({ label: x.name, value: x.count }))} /></div>
                )}
                {(detail.found_by_searches?.length > 0) && (
                  <div><p className="mb-2 text-xs font-medium text-stone-500">Found by searching</p><BarList color="#0284c7" items={detail.found_by_searches.map((x: any) => ({ label: x.query, value: x.count }))} /></div>
                )}
                {(detail.referrers?.length > 0) && (
                  <div><p className="mb-2 text-xs font-medium text-stone-500">Referrers</p><BarList color="#7c3aed" items={detail.referrers.map((x: any) => ({ label: x.name, value: x.views }))} /></div>
                )}
              </div>
            </div>
          )}
        </Card>

        {/* Audience */}
        <div className="grid gap-6 lg:grid-cols-2">
          <Card title="Languages" subtitle="Interface language of visitors (share of unique visitors)">
            <Donut label="Visitor languages" items={top.languages.map((x: any) => ({ label: lang(x.name), value: x.visitors }))} />
          </Card>
          <Card title="Language switches" subtitle="From language > to language">
            <BarList color="#0d9488" items={top.language_switches.map((x: any) => ({ label: x.name, value: x.count }))} empty="Nobody switched language yet" />
          </Card>
          <Card title="Devices">
            <Donut label="Devices" items={top.devices.map((x: any) => ({ label: x.name, value: x.views }))} />
          </Card>
          <Card title="Referrers" subtitle="Sites that sent visitors">
            <BarList color="#ca8a04" items={top.referrers.map((x: any) => ({ label: x.name, value: x.views }))} empty="No referrers yet (direct visits only)" />
          </Card>
          <Card title="Busiest hours (UTC)" subtitle="Page views by hour of day">
            <Columns values={data.by_hour_of_day} labels={data.by_hour_of_day.map((_: number, h: number) => String(h).padStart(2, '0'))} label="Page views by hour of day" />
          </Card>
          <Card title="Busiest weekdays" subtitle="Page views by day of the week">
            <Columns values={data.by_weekday} labels={WEEKDAYS} color="#d97706" label="Page views by weekday" />
          </Card>
          <Card title="Everything recorded" subtitle="Events by type" className="lg:col-span-2">
            <BarList color="#64748b" items={top.events.map((x: any) => ({ label: EVENT_NAMES[x.name] || x.name, value: x.count }))} />
          </Card>
        </div>

        {/* Content */}
        {content ? (
          <>
            <h2 className="pt-2 text-lg font-semibold text-stone-900">Content</h2>
            <p className="-mt-4 text-xs text-stone-500">
              From the species data, regenerated with <code>python _scripts/content_stats.py</code> (last run {content.generated_at.slice(0, 10)}).
            </p>
            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              <Kpi label="Species" value={fmt(content.total_species)} />
              <Kpi label="Average data completeness" value={pct(content.completeness.average)} hint={`of ${content.completeness.fields_per_species} schema fields`} />
              <Kpi label="Expert-verified veterinary" value={fmt(content.completeness.expert_verified.veterinary)} hint="species" />
              <Kpi label="Expert-verified enrichment" value={fmt(content.completeness.expert_verified.enrichment)} hint="species" />
            </div>
            <Card
              title="Birds added over time"
              subtitle="Cumulative number of species, from the first git commit of each species file"
            >
              <div className="mb-2 flex gap-1 text-xs">
                {(['by_day', 'by_hour'] as const).map((k) => (
                  <button key={k} onClick={() => setAddedBy(k)} className={`rounded-md px-2 py-1 ${addedBy === k ? 'bg-brand-700 text-white' : 'bg-stone-100 text-stone-600'}`}>
                    {k === 'by_day' ? 'By day' : 'By hour'}
                  </button>
                ))}
              </div>
              <LineChart
                series={[
                  { name: 'Total species', color: PALETTE[0], area: true, points: content.added[addedBy].map((p: any) => ({ t: Date.parse(addedBy === 'by_day' ? `${p.t}T00:00:00Z` : `${p.t}:00:00Z`) / 1000, v: p.total })) },
                  { name: 'Added', color: PALETTE[1], points: content.added[addedBy].map((p: any) => ({ t: Date.parse(addedBy === 'by_day' ? `${p.t}T00:00:00Z` : `${p.t}:00:00Z`) / 1000, v: p.added })) },
                ]}
                formatX={(t) => formatT(t, addedBy === 'by_day' ? 86400 : 3600)}
                label="Species added over time"
              />
            </Card>
            <div className="grid gap-6 lg:grid-cols-2">
              <Card title="Species names per language" subtitle="Share of species that have a name in each language">
                <BarList
                  max={1}
                  format={pct}
                  items={Object.entries(content.languages.names as Record<string, number>)
                    .map(([code, n]) => ({ label: lang(code), value: n / content.total_species, hint: `${n.toLocaleString()}` }))
                    .sort((a, b) => b.value - a.value)}
                />
              </Card>
              <Card title="Interface translations" subtitle="Share of UI strings translated (not identical to English)">
                <BarList
                  max={1}
                  color="#0284c7"
                  format={pct}
                  items={Object.entries(content.languages.ui as Record<string, { total: number; translated: number }>)
                    .map(([code, v]) => ({ label: lang(code), value: v.translated / v.total }))
                    .sort((a, b) => b.value - a.value)}
                />
              </Card>
              <Card title="How complete is each bird?" subtitle="Number of species by share of filled data fields">
                <Columns values={content.completeness.histogram.map((b: any) => b.count)} labels={content.completeness.histogram.map((b: any) => b.bucket.replace('%', ''))} label="Species by completeness" />
              </Card>
              <Card title="Data quality">
                <Donut label="Data quality" items={Object.entries(content.completeness.data_quality as Record<string, number>).map(([label, value]) => ({ label, value }))} />
              </Card>
              <Card title="Completeness by section" subtitle="Average share of each section's fields that have data">
                <BarList
                  max={1}
                  format={pct}
                  color="#7c3aed"
                  items={Object.entries(content.completeness.by_section as Record<string, number>).map(([label, value]) => ({ label: fieldLabel('en', label), value })).sort((a, b) => a.value - b.value)}
                />
              </Card>
              <Card title="Biggest data gaps" subtitle="Share of species that have data in the field (lowest first)" className="lg:col-span-2">
                <BarList
                  max={1}
                  format={pct}
                  color="#e11d48"
                  items={content.completeness.by_field.slice(0, 24).map((f: any) => ({
                    label: fieldLabel('en', f.field),
                    hint: f.field.split('.')[0],
                    value: f.filled,
                  }))}
                />
              </Card>
              <Card title="Least complete birds" subtitle="Lowest share of fields with data">
                <BarList
                  max={1}
                  format={pct}
                  color="#d97706"
                  items={content.completeness.least_complete.map((b: any) => ({
                    label: b.scientific,
                    hint: b.english,
                    value: b.score,
                    href: `/species/${encodeURIComponent(b.scientific)}`,
                  }))}
                />
              </Card>
              <Card title="Completeness by order" subtitle="Average share of filled fields, largest orders first">
                <BarList
                  max={1}
                  format={pct}
                  color="#0d9488"
                  items={content.completeness.by_order.slice(0, 12).map((o: any) => ({ label: o.order, value: o.average, hint: `${o.species} species` }))}
                />
              </Card>
            </div>
          </>
        ) : (
          <Card title="Content statistics">
            <p className="text-sm text-stone-500">Not generated yet. Run <code>python _scripts/content_stats.py</code> and rebuild.</p>
          </Card>
        )}

        <p className="pb-8 text-center text-xs text-stone-400">
          Times are UTC. Bots and visitors with Do-Not-Track are not counted, no IP addresses are stored, and this dashboard is not tracked.
        </p>
      </main>
    </div>
  );
}
