import { countryLabel, sortCountryCodes } from '../countries';

describe('countryLabel', () => {
  it('returns a Persian name for Iran', () => {
    expect(countryLabel('fa', 'IR')).toMatch(/ایران/);
  });

  it('returns an English name for Iran', () => {
    expect(countryLabel('en', 'IR')).toBe('Iran');
  });

  it('uppercases codes', () => {
    expect(countryLabel('en', 'ir')).toBe('Iran');
  });
});

describe('sortCountryCodes', () => {
  it('sorts by localised English name', () => {
    expect(sortCountryCodes('en', ['ZA', 'BW', 'KE'])).toEqual(['BW', 'KE', 'ZA']);
  });
});
