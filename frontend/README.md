# OpenBird Frontend

Next.js 14 frontend for the OpenBird Database.

## Features

- 🔍 **Full-text search** across 11,149 bird species
- 🌍 **Multilingual support** - English, Persian (RTL), and 430+ languages
- 📚 **Taxonomy browser** - Navigate orders → families → genera → species
- 📋 **Species detail pages** - Complete data from BIRDBASE, BirdNET, AVONICHE
- 🎨 **Modern UI** - Tailwind CSS, Persian font support (Vazirmatn)
- 🔄 **Real-time search** - MeiliSearch integration with JSON fallback

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- OpenBird API running on `http://localhost:8000`
- MeiliSearch (optional) on `http://localhost:7700`

### Installation

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENBIRD_API_URL` | Backend API URL | `http://localhost:8000` |
| `MEILISEARCH_HOST` | MeiliSearch host | `http://localhost:7700` |
| `MEILI_MASTER_KEY` | MeiliSearch master key | - |

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── api/           # API routes (proxy to backend)
│   │   ├── globals.css    # Global styles + Tailwind
│   │   ├── layout.tsx     # Root layout
│   │   └── page.tsx       # Main page
│   ├── components/
│   │   ├── SearchBar.tsx
│   │   ├── SpeciesList.tsx
│   │   ├── SpeciesDetail.tsx
│   │   └── TaxonomyTree.tsx
│   ├── lib/
│   │   └── types.ts       # TypeScript types
│   └── globals.css
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## Features

### Search
- Full-text search across scientific names, English names, Persian names
- Filters: order, family, IUCN status, habitat, diet, migration
- Persian (RTL) search support
- Debounced search with MeiliSearch backend

### Species Detail
- Complete species profile with all 78 BIRDBASE traits
- Persian/English names with RTL support
- Morphology, distribution, habitat, diet, behavior, reproduction, demography
- Conservation status with IUCN badges
- Veterinary care & enrichment data
- Source citations and data quality indicators

### Taxonomy Browser
- Hierarchical navigation: Orders → Families → Genera → Species
- Expandable/collapsible tree view
- Species counts at each level
- Quick navigation to species detail

## Data Sources

- **BirdNET Taxonomy** - 16,193 species, 434 languages
- **BIRDBASE 2025** - 78 traits for 11,589 species
- **AVONICHE 2025** - 32 foraging niches
- **BirdFYI API** - Habitat, behavior, regional presence
- **GBIF/eBird** - Taxonomy crosswalks, occurrence data

## Development

```bash
# Development server
npm run dev

# Production build
npm run build
npm start

# Linting
npm run lint
```

## Deployment

### Docker
```bash
docker build -t openbird-frontend .
docker run -p 3000:3000 openbird-frontend
```

### Vercel (Recommended)
1. Connect GitHub repo to Vercel
2. Add environment variables
3. Deploy

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit PR

## License

MIT License - see LICENSE file for details.