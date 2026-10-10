# OpenBird Mobile

React Native mobile app for the OpenBird Database - a global bird database with 11,000+ species.

## Features

- **Search** - Find species by common or scientific name (multi-language)
- **Taxonomy Browser** - Browse by order, family, genus
- **Species Details** - Comprehensive species profiles with 78 BIRDBASE traits + 32 AVONICHE foraging niches
- **Multi-language** - English, Persian (فارسی), Arabic (العربية)
- **Offline-first** - Cached data for offline access
- **Favorites** - Save species for quick access

## Data Sources

- **BirdNET Taxonomy** - 16,193 species, 434 languages
- **BIRDBASE 2025** - 11,589 species, 78 traits
- **AVONICHE 2025** - 10,981 species, 32 foraging niches
- **BirdFYI API** - 11,251 species, habitat/behavior details

## Getting Started

### Prerequisites

- Node.js 18+
- Expo CLI (`npm install -g expo-cli`)
- iOS Simulator (Mac) or Android Emulator

### Installation

```bash
cd mobile
npm install
```

### Development

```bash
# Start Expo development server
npm start

# Run on iOS
npm run ios

# Run on Android
npm run android

# Run on Web
npm run web
```

## Project Structure

```
mobile/
├── app/                    # Expo Router pages
│   ├── (tabs)/            # Tab navigation screens
│   │   ├── index.tsx      # Search screen
│   │   ├── taxonomy.tsx   # Taxonomy browser
│   │   ├── favorites.tsx  # Favorites
│   │   └── settings.tsx   # Settings
│   ├── species/           # Species detail screens
│   │   └── [scientificName].tsx
│   └── taxonomy/family/   # Family detail screens
│       └── [family].tsx
├── components/            # Reusable components
├── lib/                   # Utilities, API, types
├── store/                 # Zustand stores
├── hooks/                 # Custom hooks
└── assets/                # Images, fonts
```

## API Integration

The app connects to the OpenBird API server (FastAPI + MeiliSearch):
- Local development: `http://localhost:8000`
- Production: `https://api.openbird.org`

## Building for Production

```bash
# Build for iOS
eas build --platform ios

# Build for Android
eas build --platform android
```

## License

Data: CC-BY 4.0 (BirdNET, BIRDBASE, AVONICHE, BirdFYI)
Code: MIT