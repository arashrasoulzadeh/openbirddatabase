import { NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const revalidate = 3600;

export async function GET() {
  const body = `# OpenBird — Full AI Discovery

OpenBird is an open, global bird species database (~11,000 species). Each species is stored as a Markdown file with YAML frontmatter containing 78 BIRDBASE traits and 32 AVONICHE niches.

## Machine-readable species data
- JSON API: GET /species/{scientific_name}?lang={lang}
- Markdown export: /{lang}/species/{slug}.md
- Search: GET /search?q=...&lang=...
- Taxonomy: GET /taxonomy, GET /taxonomy/{order}, GET /taxonomy/{order}/{family}
- Filters: GET /filters
- Stats: GET /stats
- Random: GET /random

## Taxonomy documentation
- Schema: _schemas/bird-attributes.schema.json
- Template: _templates/species-template.md.j2
- Guide: docs/SCHEMA_GUIDE.md

## External identifiers
Species files include gbif_key, ebird_code, taxon_id, and xeno_canto_ids where available.

## Data provenance
Data is CC-BY 4.0. Every scientific fact carries source attribution in the \`sources\` field of each species file. See docs/DATA_SOURCES.md and docs/CONTRIBUTING.md.

## API usage examples
- curl "$API/species/Parus%20major?lang=en"
- curl "$API/search?q=great%20tit&limit=5"
- curl "$API/taxonomy"

## Languages
ar, de, en, es, fa, fr, ja, nl, pl, pt, ru, tr, zh

## Links
- GitHub: https://github.com/arashrasoulzadeh/openbirddatabase
- Website: https://birds.meetarash.ir
`;
  return new NextResponse(body, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
}
