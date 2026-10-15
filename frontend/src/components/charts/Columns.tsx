interface Props {
  values: number[];
  labels: string[];
  color?: string;
  height?: number;
  format?: (v: number) => string;
  label: string;
}

/** Vertical bars (histograms, hour of day, weekday). */
export default function Columns({ values, labels, color = '#2f664b', height = 160, format = (v) => v.toLocaleString(), label }: Props) {
  const max = Math.max(...values, 1);
  const W = 600, pad = 18, bw = (W - pad * 2) / values.length;
  const every = values.length > 14 ? Math.ceil(values.length / 12) : 1;
  return (
    <div dir="ltr">
    <svg viewBox={`0 0 ${W} ${height + 22}`} className="w-full" role="img" aria-label={label}>
      {values.map((v, i) => {
        const h = (v / max) * height;
        return (
          <g key={i}>
            <rect x={pad + i * bw + bw * 0.12} y={height - h} width={bw * 0.76} height={Math.max(h, v ? 1 : 0)} rx={3} fill={color} opacity={0.9}>
              <title>{`${labels[i]}: ${format(v)}`}</title>
            </rect>
            {i % every === 0 && (
              <text x={pad + i * bw + bw / 2} y={height + 15} textAnchor="middle" fontSize="10" fill="#78716c">{labels[i]}</text>
            )}
          </g>
        );
      })}
      <line x1={pad} x2={W - pad} y1={height} y2={height} stroke="#e7e5e4" />
    </svg>
    </div>
  );
}
