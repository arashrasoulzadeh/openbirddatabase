import messages from '../messages.json';
import { LOCALES, langFromAcceptLanguage, dirOf } from '../locales';
import values from '../values.json';
import { fieldLabel, iucnLabel, nameFromHit, nameFromNames, nameFromTree, translate, valueLabel } from '../translate';

describe('translations', () => {
  it('every locale has every English key', () => {
    const en = Object.keys((messages as any).en);
    for (const { code } of LOCALES) {
      const missing = en.filter((k) => !(messages as any)[code]?.[k]);
      expect({ code, missing }).toEqual({ code, missing: [] });
    }
  });

  it('keeps placeholders in every language', () => {
    for (const { code } of LOCALES) {
      expect((messages as any)[code].speciesCount).toContain('{count}');
    }
    expect(translate('es', 'speciesCount', { count: 12 })).toBe('12 especies');
  });

  it('falls back to English, then to the key', () => {
    expect(translate('de', 'no-such-key')).toBe('no-such-key');
  });
});

describe('labels', () => {
  it('translates species-file fields, using the path when a name is ambiguous', () => {
    expect(fieldLabel('en', 'habitat.primary')).toBe('Primary Habitat');
    expect(fieldLabel('en', 'diet.primary')).toBe('Primary Diet');
    expect(fieldLabel('es', 'morphology.body_mass_g')).toBe('Masa corporal');
    expect(fieldLabel('en', 'something.unknown_field')).toBe('Unknown field');
  });

  it('translates IUCN status badges', () => {
    expect(iucnLabel('es', 'LC')).toBe('Preocupación menor');
    expect(iucnLabel('en', 'XX')).toBe('XX');
  });
});

describe('names', () => {
  it('picks the selected language and falls back to English', () => {
    const hit = { common_name_en: 'Great Tit', common_name_es: 'Carbonero Común', scientific_name: 'Parus major' };
    expect(nameFromHit(hit, 'es')).toBe('Carbonero Común');
    expect(nameFromHit(hit, 'ja')).toBe('Great Tit');
    expect(nameFromTree({ scientific: 'P', common_en: 'Tit', common_fa: 'تیت', names: { de: 'Meise' } }, 'de')).toBe('Meise');
    expect(nameFromTree({ scientific: 'P', common_en: 'Tit', common_fa: 'تیت' }, 'fa')).toBe('تیت');
    expect(nameFromNames({ en: 'Tit' }, 'fr', 'x')).toBe('Tit');
  });
});

describe('locales', () => {
  it('detects language from Accept-Language and text direction', () => {
    expect(langFromAcceptLanguage('fa-IR,fa;q=0.9,en;q=0.8')).toBe('fa');
    expect(langFromAcceptLanguage('xx')).toBe('en');
    expect(dirOf('ar')).toBe('rtl');
    expect(dirOf('de')).toBe('ltr');
  });
});

describe('data values', () => {
  it('translates categorical values only on the fields that use them', () => {
    expect(valueLabel('es', 'habitat.primary', 'Forest')).toBe('Bosque');
    expect(valueLabel('fa', 'behavior.sociality', 'Small groups')).toBe('گروه‌های کوچک');
    expect(valueLabel('de', 'enrichment.bathing', 'Forest')).toBe('Forest'); // free text untouched
    expect(valueLabel('es', 'diet.primary', 'Something new')).toBe('Something new');
    expect(valueLabel('es', 'conservation.iucn_tag', 'PE')).toBe('Posiblemente extinta');
    expect(fieldLabel('es', 'conservation.iucn_tag')).toBe('Etiqueta UICN');
  });

  it('has every language for every value', () => {
    for (const [value, byLang] of Object.entries(values as Record<string, Record<string, string>>)) {
      for (const { code } of LOCALES) expect({ value, code, text: !!byLang[code] }).toEqual({ value, code, text: true });
    }
  });
});
