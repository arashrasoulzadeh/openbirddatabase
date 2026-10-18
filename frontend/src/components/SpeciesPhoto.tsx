import { API_URL } from '@/lib/config';

interface PhotoInfo {
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

/** The species photo (served by the API from images/) with its credit. Renders nothing for species without a photo. */
export default function SpeciesPhoto({ image, alt, label }: { image?: PhotoInfo | null; alt: string; label: string }) {
  if (!image?.file) return null;
  const src = `${API_URL}/images/${encodeURIComponent(image.file.split('/').pop() as string)}`;
  const licence = image.license || '';
  return (
    <figure className="mt-6 max-w-sm overflow-hidden rounded-2xl bg-white/10 ring-1 ring-white/20">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={src} alt={alt} className="max-h-72 w-full bg-brand-900/30 object-cover" loading="eager" fetchPriority="high" />
      <figcaption className="px-3 py-2 text-xs text-brand-100" dir="ltr">
        {label}: {image.author || '—'}
        {licence && (
          <>
            {' · '}
            {LICENSE_URL[licence] ? <a href={LICENSE_URL[licence]} target="_blank" rel="noopener noreferrer" className="underline">{licence}</a> : licence}
          </>
        )}
        {image.page && (
          <>
            {' · '}
            <a href={image.page} target="_blank" rel="noopener noreferrer" className="underline">{image.source || 'source'}</a>
          </>
        )}
      </figcaption>
    </figure>
  );
}
