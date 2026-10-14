import './globals.css';
import { cookies, headers } from 'next/headers';
import { I18nProvider } from '@/lib/i18n/I18nProvider';
import { DEFAULT_LANG, LANG_COOKIE, dirOf, isLang, langFromAcceptLanguage } from '@/lib/i18n/locales';

export const metadata = {
  title: 'OpenBird Database',
  description: 'Global bird species database with multilingual support',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  // Language: cookie (user choice) > browser Accept-Language > English
  const cookie = cookies().get(LANG_COOKIE)?.value;
  const lang = isLang(cookie) ? cookie : langFromAcceptLanguage(headers().get('accept-language')) || DEFAULT_LANG;

  return (
    <html lang={lang} dir={dirOf(lang)}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Vazirmatn:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="min-h-screen bg-gray-50 font-sans antialiased">
        <I18nProvider initialLang={lang}>{children}</I18nProvider>
      </body>
    </html>
  );
}
