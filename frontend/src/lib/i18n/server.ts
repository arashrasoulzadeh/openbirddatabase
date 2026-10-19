import { headers } from 'next/headers';
import { DEFAULT_LANG, Lang, isLang } from './locales';
import { LANG_HEADER } from './routes';

/** The language of this request, decided by the URL prefix (middleware.ts). Server components only. */
export function requestLang(): Lang {
  const v = headers().get(LANG_HEADER);
  return isLang(v) ? v : DEFAULT_LANG;
}
