# OpenBird — remaining work

Foundation, ingestion (~11k species), API, website, Flutter app, analytics, deploy, and enrichment tooling are done. What’s left:

---

## Data

1. **Finish enrichment apply** — GBIF countries partially applied (~3k species); finish `fetch gbif` / `apply gbif`, then AVONET, AnAge/Amniote, Xeno-canto, photos as needed
2. **Species photos** — pipeline exists (`enrich.py fetch photos`); download licensed images into `images/` at scale
3. **Vet / enrichment curation** — expand beyond the current ~45 curated species
4. **Fill completeness gaps** (~40% average) — morphology lengths, demography, Arabic/Chinese names where missing; each source needs taxonomy match + licence check

## Apps

5. **Website** — dark mode, species comparison tool, checklist export (range maps + `/analytics` stats are done)
6. **Flutter** — offline sync, audio playback (Xeno-canto)
7. **Expo app** (`mobile/`) — still on old `/api/...` paths; adapt to the real API like `flutter_app` (`api_mapper.dart`)
8. **More UI languages** — Hebrew, Hindi, Indonesian, Korean, Italian, etc. (ARB + `values.json`)

## Release / ops

9. **Signed release APK + iOS build** in CI (today: unsigned debug APK only)
10. **Verify MeiliSearch + vector search** on the server after deploy (`/health` → `"meilisearch": true`, `"vector_search": true`; if Meili is unhealthy wipe `meili_data/` and re-run the indexer)
