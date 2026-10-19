import Link from 'next/link';
import { Lang } from '@/lib/i18n/locales';
import { localePath } from '@/lib/i18n/routes';
import { requestLang } from '@/lib/i18n/server';

/** Server-side link to a species page in the request's language (the client-side one is TrackedLink). */
export default function SpeciesLink({ scientific, className, children, lang = requestLang() }: { scientific: string; className?: string; children: React.ReactNode; lang?: Lang }) {
  return (
    <Link href={localePath(lang, `/species/${encodeURIComponent(scientific)}`)} className={className}>
      {children}
    </Link>
  );
}
