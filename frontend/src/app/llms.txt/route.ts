import { NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const revalidate = 3600;

export async function GET() {
  const body = `# OpenBird

OpenBird is a global, open bird species database (~11,000 species) stored as Markdown files with YAML frontmatter. Persian (fa) is the priority language; English (en) is used for keys.

## Data structure
- Species files: birds/{order}/{family}/{species}.md
- Per-language overrides: translations/{lang}/{order}/{family}/{species}.md
- Indexes: _index/species-index.json, taxonomy-tree.json, field-stats.json

## Languages
ar, de, en, es, fa, fr, ja, nl, pl, pt, ru, tr, zh

## Taxonomy and species pages
- /{lang}/order/{order}
- /{lang}/family/{order}/{family}
- /{lang}/species/{slug}
- Markdown export: /{lang}/species/{slug}.md

## Important sections
- Home: /
- Analytics: /analytics
- Sitemap: /sitemap.xml

## Documentation
- README: https://github.com/arashrasoulzadeh/openbirddatabase/blob/main/README.md
- Schema guide: https://github.com/arashrasoulzadeh/openbirddatabase/blob/main/docs/SCHEMA_GUIDE.md
- Data sources: https://github.com/arashrasoulzadeh/openbirddatabase/blob/main/docs/DATA_SOURCES.md
- AI context: https://github.com/arashrasoulzadeh/openbirddatabase/blob/main/docs/AI_CONTEXT.md

## API
- Base: see NEXT_PUBLIC_API_URL
- GET /species/{scientific_name}?lang=fa
- GET /search, POST /search
- GET /taxonomy, GET /filters, GET /stats, GET /random

## Markdown exports
- /fa/species/{slug}.md
- /en/species/{slug}.md

## Scientific data sources and attribution
Data is CC-BY 4.0. Sources and attribution are kept in each species file's \`sources\` frontmatter. See docs/DATA_SOURCES.md.
`;
  return new NextResponse(body, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
}
