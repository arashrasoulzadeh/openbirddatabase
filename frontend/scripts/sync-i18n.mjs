// Builds src/lib/i18n/messages.json from the Flutter app's ARB files so the website
// and the mobile app share one set of translations.
// Run after editing flutter_app/lib/l10n/*.arb:  npm run i18n
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const arbDir = join(root, '../../flutter_app/lib/l10n');
const out = join(root, '../src/lib/i18n/messages.json');

const messages = {};
for (const file of readdirSync(arbDir).filter((f) => /^app_\w+\.arb$/.test(f)).sort()) {
  const lang = file.slice(4, -4);
  const arb = JSON.parse(readFileSync(join(arbDir, file), 'utf8'));
  messages[lang] = Object.fromEntries(Object.entries(arb).filter(([k]) => !k.startsWith('@')));
}
writeFileSync(out, JSON.stringify(messages, null, 1) + '\n');
console.log(`Wrote ${Object.keys(messages).length} languages to src/lib/i18n/messages.json`);
