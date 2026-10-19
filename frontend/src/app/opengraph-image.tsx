import { ImageResponse } from 'next/og';

// The default link preview (1200x630) for pages without their own photo.
export const alt = 'OpenBird Database – 11,000+ bird species in 13 languages';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

export default function Image() {
  return new ImageResponse(
    (
      <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: 90, background: 'linear-gradient(135deg, #214133 0%, #3f8160 100%)', color: '#fff' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 28 }}>
          <svg width="120" height="120" viewBox="0 0 32 32">
            <circle cx="16" cy="16" r="16" fill="#fff" />
            <path d="M9 20c2-6 7-9 13-8-1 5-4 9-10 9-1 0-2 0-3-1z" fill="#27523d" />
            <circle cx="20.5" cy="14" r="1.1" fill="#fff" />
          </svg>
          <div style={{ fontSize: 96, fontWeight: 700, letterSpacing: -2 }}>OpenBird</div>
        </div>
        <div style={{ marginTop: 40, fontSize: 48, lineHeight: 1.25, color: '#dcebe1' }}>11,000+ bird species in 13 languages</div>
        <div style={{ marginTop: 18, fontSize: 32, color: '#b9d7c4' }}>Names · Photos · Range · Habitat · Diet · Conservation</div>
      </div>
    ),
    size,
  );
}
