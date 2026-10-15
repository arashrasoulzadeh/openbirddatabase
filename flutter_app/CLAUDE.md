# Flutter app

Material 3 app, 13 languages, light/dark/system themes. Code in `lib/`.

- Test: `flutter test` (unit/widget in `test/`, integration in `integration_test/`)
- API address is set at build time:
  `flutter build apk --dart-define=API_BASE_URL=https://api.example.org --dart-define=SITE_URL=https://example.org`
  (CI reads the `API_DOMAIN` / `SITE_DOMAIN` repository variables; default is `http://localhost:8000`)
- `lib/services/api_service.dart` calls the real API; `api_mapper.dart` turns its JSON (nested species file, flat search
  hits, taxonomy tree) into the models. Model parsing is deliberately tolerant (`_asInt`/`_asDouble` in `species.dart`).
- `test/unit/real_data_test.dart` parses real species files from `../birds`; run it after touching `models/`.
- Analytics: `lib/services/analytics_service.dart` sends anonymous events (page views and time per screen, searches,
  bird clicks, language changes) to the same API as the website (`POST /analytics/event`); `analytics_observer.dart`
  reports screens. It stays disabled until `init()` (so tests create no timers or requests) and users can switch it off
  in Settings (`usageStats`). Track new interactions with `AnalyticsService.instance.track(...)`.
- UI strings: `lib/l10n/*.arb` with `l10n.yaml`. These files are also the source for the website
  (`cd ../frontend && npm run i18n`), so keep all 13 files on the same keys.
- The repo tracks only `lib/`, `test/`, `pubspec.yaml`, `l10n.yaml`; CI runs `flutter create` to generate `android/` and
  adds the INTERNET permission (see `.github/workflows/build-debug-app.yml`).
