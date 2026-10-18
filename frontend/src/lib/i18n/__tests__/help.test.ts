import help from '../help.json';
import values from '../values.json';
import { LOCALES } from '../locales';
import { REALMS, formatMeasurement, helpText, splitRealms, valueHelp, xenoCantoUrl, ID_LINKS } from '../help';

const table = help as Record<string, Record<string, string>>;

describe('help texts', () => {
  it('every explanation exists in all 13 languages', () => {
    const missing: string[] = [];
    for (const [key, byLang] of Object.entries(table)) {
      for (const { code } of LOCALES) if (!byLang[code]?.trim()) missing.push(`${key}:${code}`);
    }
    expect(missing).toEqual([]);
  });

  it('keeps the {site} placeholder in the "open on" text of every language', () => {
    for (const { code } of LOCALES) expect(table['ui.seeOn'][code]).toContain('{site}');
  });

  it('explains every categorical value and every realm code', () => {
    for (const value of Object.keys(values)) expect({ value, text: !!valueHelp('en', value) }).toEqual({ value, text: true });
    for (const code of Object.keys(REALMS)) {
      expect(helpText('en', `realm.${code}.name`)).toBeTruthy();
      expect(helpText('en', `realm.${code}.about`)).toBeTruthy();
    }
  });

  it('falls back to English for unknown languages', () => {
    expect(helpText('es', 'realm.F.name')).toBe('Afrotropical');
    expect(helpText('fa', 'realm.F.name')).toContain('آفروگرمسیری');
  });
});

describe('foraging styles', () => {
  it('has a plain-language description for all 32 styles', () => {
    const niches = Object.keys(table).filter((k) => k.startsWith('niche.'));
    expect(niches).toHaveLength(32);
    expect(helpText('es', 'niche.fruit_aerial')).toBe('Fruta tomada mientras vuela suspendida');
  });
});

describe('realms', () => {
  it('splits combined codes, ignores case, duplicates and unknown letters', () => {
    expect(splitRealms(['LN', 'p', 'L', '?', 'x'])).toEqual(['L', 'N', 'P']);
    expect(splitRealms([])).toEqual([]);
  });
});

describe('measurements and links', () => {
  const unit = (k: string) => ({ days: 'days', years: 'years', months: 'months' } as Record<string, string>)[k];
  it('adds units and formats numbers', () => {
    expect(formatMeasurement('en', 'morphology.body_mass_g', 18.37, unit)).toBe('18.4 g');
    expect(formatMeasurement('en', 'habitat.elevational_max_m', 2000, unit)).toBe('2,000 m');
    expect(formatMeasurement('en', 'reproduction.incubation_days', 14, unit)).toBe('14 days');
    expect(formatMeasurement('en', 'demography.generation_length_years', 5.4, unit)).toBe('5.4 years');
    expect(formatMeasurement('en', 'demography.annual_survival_adult', 0.62, unit)).toBe('62%');
    expect(formatMeasurement('en', 'demography.density_individuals_per_km2', 3, unit)).toBe('3 / km²');
    expect(formatMeasurement('en', 'habitat.habitat_breadth', 4, unit)).toBe('4');
  });

  it('builds links to the external sites', () => {
    expect(ID_LINKS.ebird_code.url('gretit1')).toBe('https://ebird.org/species/gretit1');
    expect(ID_LINKS.gbif_key.url('2480498')).toBe('https://www.gbif.org/species/2480498');
    expect(xenoCantoUrl('XC123456')).toBe('https://xeno-canto.org/123456');
    expect(xenoCantoUrl('987')).toBe('https://xeno-canto.org/987');
  });
});
