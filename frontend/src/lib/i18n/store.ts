/**
 * Translation tables, filled at runtime instead of being imported as JSON.
 *
 * Importing the JSON files from code that runs in the browser would ship all 13 languages (~400 kB) in the JS bundle.
 * Instead the server (layout.tsx -> bundle.ts) registers everything once, and sends the browser only the current
 * language plus English (`sliceFor`), which I18nProvider registers here before rendering.
 */
export type Tables = {
  messages: Record<string, Record<string, string>>; // { lang: { key: text } }
  values: Record<string, Record<string, string>>; //   { value: { lang: text } }
  help: Record<string, Record<string, string>>; //     { key: { lang: text } }
  taxa: Record<string, Record<string, string>>; //     { name: { lang: text } }
};

export const tables: Tables = { messages: {}, values: {}, help: {}, taxa: {} };

/** Merge a (partial) set of tables in; safe to call repeatedly with the same data. */
export function register(slice: Partial<Tables>): void {
  for (const name of Object.keys(slice) as (keyof Tables)[]) {
    const source = slice[name] || {};
    const target = tables[name];
    for (const key of Object.keys(source)) target[key] = { ...target[key], ...source[key] };
  }
}
