/** All translations. Import this ONLY from server code (layout.tsx, tests): it pulls the JSON files in. */
import messages from './messages.json';
import values from './values.json';
import help from './help.json';
import taxa from './taxa.json';
import { DEFAULT_LANG, Lang } from './locales';
import { Tables, register } from './store';

const full: Tables = { messages, values, help, taxa } as unknown as Tables;
register(full); // the server (and tests) can translate into every language

/** What the browser needs for `lang`: that language plus English, nothing else. */
export function sliceFor(lang: Lang): Tables {
  const keep: string[] = lang === DEFAULT_LANG ? [DEFAULT_LANG] : [lang, DEFAULT_LANG];
  const slice: Tables = { messages: {}, values: {}, help: {}, taxa: {} };
  for (const l of keep) if (full.messages[l]) slice.messages[l] = full.messages[l];
  for (const name of ['values', 'help', 'taxa'] as const) {
    for (const [key, texts] of Object.entries(full[name])) {
      const picked: Record<string, string> = {};
      for (const l of keep) if (texts[l] !== undefined) picked[l] = texts[l];
      slice[name][key] = picked;
    }
  }
  return slice;
}
