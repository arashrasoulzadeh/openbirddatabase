'use client';

import { useRef, useState } from 'react';
import { AXIS, GRID } from './palette';

export interface Point { t: number; v: number }
export interface Series { name: string; color: string; points: Point[]; area?: boolean }

interface Props {
  series: Series[];
  height?: number;
  formatX: (t: number) => string;
  formatY?: (v: number) => string;
  label: string;
}

/** 1, 2, 5 x 10^k above the data maximum, so axis ticks are round numbers. */
function niceMax(max: number): number {
  const exp = Math.pow(10, Math.floor(Math.log10(max)));
  const f = max / exp;
  return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * exp;
}

export default function LineChart({ series, height = 220, formatX, formatY = (v) => v.toLocaleString(), label }: Props) {
  const W = 800, H = height;
  const m = { l: 46, r: 12, t: 10, b: 26 };
  const iw = W - m.l - m.r, ih = H - m.t - m.b;
  const ref = useRef<SVGSVGElement>(null);
  const [hover, setHover] = useState<number | null>(null);

  const n = series[0]?.points.length ?? 0;
  const max = niceMax(Math.max(1, ...series.flatMap((s) => s.points.map((p) => p.v))));
  const x = (i: number) => m.l + (n <= 1 ? iw / 2 : (i * iw) / (n - 1));
  const y = (v: number) => m.t + ih - (v / max) * ih;
  const line = (s: Series) => s.points.map((p, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(p.v).toFixed(1)}`).join(' ');
  const area = (s: Series) => `${line(s)} L${x(n - 1).toFixed(1)},${y(0)} L${x(0).toFixed(1)},${y(0)} Z`;
  const labelIdx = n ? Array.from(new Set([0, 1, 2, 3, 4, 5].map((k) => Math.round((k * (n - 1)) / 5)))) : [];

  const onMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const rect = ref.current?.getBoundingClientRect();
    if (!rect || n < 1) return;
    const px = ((e.clientX - rect.left) / rect.width) * W;
    setHover(Math.max(0, Math.min(n - 1, Math.round(((px - m.l) / iw) * (n - 1)))));
  };

  return (
    <div className="relative" dir="ltr">
      <svg
        ref={ref}
        viewBox={`0 0 ${W} ${H}`}
        className="w-full"
        role="img"
        aria-label={label}
        onMouseMove={onMove}
        onMouseLeave={() => setHover(null)}
      >
        {[0, 1, 2, 3, 4].map((k) => {
          const v = (max * k) / 4;
          return (
            <g key={k}>
              <line x1={m.l} x2={W - m.r} y1={y(v)} y2={y(v)} stroke={GRID} />
              <text x={m.l - 6} y={y(v) + 4} textAnchor="end" fontSize="11" fill={AXIS}>{formatY(Math.round(v))}</text>
            </g>
          );
        })}
        {labelIdx.map((i) => (
          <text key={i} x={x(i)} y={H - 6} textAnchor={i === 0 ? 'start' : i === n - 1 ? 'end' : 'middle'} fontSize="11" fill={AXIS}>
            {formatX(series[0].points[i].t)}
          </text>
        ))}
        {series.map((s) => (
          <g key={s.name}>
            {s.area && <path d={area(s)} fill={s.color} opacity={0.12} />}
            <path d={line(s)} fill="none" stroke={s.color} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
          </g>
        ))}
        {hover !== null && (
          <g>
            <line x1={x(hover)} x2={x(hover)} y1={m.t} y2={m.t + ih} stroke={AXIS} strokeDasharray="3 3" />
            {series.map((s) => <circle key={s.name} cx={x(hover)} cy={y(s.points[hover].v)} r={4} fill={s.color} />)}
          </g>
        )}
      </svg>
      {hover !== null && (
        <div
          className="pointer-events-none absolute top-1 z-10 rounded-lg border border-stone-200 bg-white px-3 py-2 text-xs shadow-lg"
          style={{ left: `${Math.min(80, Math.max(2, (x(hover) / W) * 100 - 8))}%` }}
        >
          <div className="mb-1 font-medium text-stone-700">{formatX(series[0].points[hover].t)}</div>
          {series.map((s) => (
            <div key={s.name} className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full" style={{ background: s.color }} />
              <span className="text-stone-500">{s.name}</span>
              <span className="ms-auto font-semibold text-stone-900">{formatY(s.points[hover].v)}</span>
            </div>
          ))}
        </div>
      )}
      {series.length > 1 && (
        <div className="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-xs text-stone-500">
          {series.map((s) => (
            <span key={s.name} className="inline-flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full" style={{ background: s.color }} />{s.name}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
