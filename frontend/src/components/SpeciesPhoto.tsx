'use client';

import { useState } from 'react';
import { photoUrl } from '@/lib/photos';

export interface PhotoInfo {
  file?: string;
  author?: string;
  license?: string;
  source?: string;
  page?: string;
}

const LICENSE_URL: Record<string, string> = {
  'CC0-1.0': 'https://creativecommons.org/publicdomain/zero/1.0/',
  'CC-BY-4.0': 'https://creativecommons.org/licenses/by/4.0/',
};

const srcOf = photoUrl;

/**
 * The species photo (served by the API from images/) with its credit; when the species has more photos, small
 * thumbnails below switch the large one. Renders nothing for species without a photo.
 */
export default function SpeciesPhoto({
  image,
  images,
  alt,
  label,
}: {
  image?: PhotoInfo | null;
  images?: PhotoInfo[] | null;
  alt: string;
  label: string;
}) {
  const all = (images && images.length ? images : image ? [image] : []).filter((p) => p?.file);
  const [index, setIndex] = useState(0);
  if (!all.length) return null;
  const current = all[Math.min(index, all.length - 1)];
  const licence = current.license || '';
  return (
    <figure className="mt-6 max-w-sm overflow-hidden rounded-2xl bg-white/10 ring-1 ring-white/20">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={srcOf(current.file as string)} alt={alt} className="max-h-72 w-full bg-brand-900/30 object-cover" loading="eager" fetchPriority="high" />
      {all.length > 1 && (
        <ul className="flex gap-1.5 overflow-x-auto px-2 pt-2" dir="ltr">
          {all.map((photo, i) => (
            <li key={photo.file} className="shrink-0">
              <button
                type="button"
                onClick={() => setIndex(i)}
                aria-label={`${alt} ${i + 1}/${all.length}`}
                aria-current={i === index ? 'true' : undefined}
                className={`block overflow-hidden rounded-lg ring-2 transition ${i === index ? 'ring-white' : 'opacity-70 ring-transparent hover:opacity-100'}`}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={srcOf(photo.file as string)} alt="" className="h-12 w-16 object-cover" loading="lazy" />
              </button>
            </li>
          ))}
        </ul>
      )}
      <figcaption className="px-3 py-2 text-xs text-brand-100" dir="ltr">
        {label}: {current.author || '—'}
        {licence && (
          <>
            {' · '}
            {LICENSE_URL[licence] ? <a href={LICENSE_URL[licence]} target="_blank" rel="noopener noreferrer" className="underline">{licence}</a> : licence}
          </>
        )}
        {current.page && (
          <>
            {' · '}
            <a href={current.page} target="_blank" rel="noopener noreferrer" className="underline">{current.source || 'source'}</a>
          </>
        )}
      </figcaption>
    </figure>
  );
}
