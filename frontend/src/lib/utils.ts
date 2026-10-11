export function formatNumber(num: number | null | undefined): string {
  if (num === null || num === undefined) return '—';
  return typeof num === 'number' ? num.toLocaleString() : num;
}

export function formatRange(
  min: number | null | undefined,
  max: number | null | undefined
): string {
  if (min !== null && min !== undefined && max !== null && max !== undefined) {
    return `${min.toLocaleString()}–${max.toLocaleString()}`;
  }
  if (min !== null && min !== undefined) {
    return `${min.toLocaleString()}–—`;
  }
  if (max !== null && max !== undefined) {
    return `—–${max.toLocaleString()}`;
  }
  return '—–—';
}

export function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}