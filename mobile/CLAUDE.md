# Mobile (Expo / React Native)

Expo Router app (Expo ~51). Routes in `app/`, shared code in `lib/` and `store/`.

- Dev: `npm start` (`npm run ios` / `android` / `web`); lint: `npm run lint`
- Config: `app.config.ts`, `babel.config.js`, `metro.config.js`
- Data comes from the API in `../_scripts/api.py`.

Known gap: `lib/api.ts` still calls the old `/api/search`, `/api/taxonomy` endpoints, which the FastAPI server does not
have. Adapt it like `flutter_app/lib/services/api_mapper.dart` before using it against the public API.
