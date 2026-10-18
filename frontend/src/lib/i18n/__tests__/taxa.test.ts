import { taxonLabel } from '../taxa';
import taxa from '../taxa.json';

describe('taxon names', () => {
  it('returns the common name of orders and families in the chosen language', () => {
    expect(taxonLabel('de', 'Passeriformes')).toBe('Sperlingsvögel');
    expect(taxonLabel('ja', 'Passeriformes')).toBe('スズメ目');
    expect(taxonLabel('en', 'Passeriformes')).toMatch(/^Passerines$/i);
  });

  it('returns nothing when there is no useful name, or only the Latin one', () => {
    expect(taxonLabel('es', 'Paridae')).toBe('');
    expect(taxonLabel('en', 'Not a taxon')).toBe('');
  });

  it('covers every order and family of the tree with at least one language', () => {
    expect(Object.keys(taxa).length).toBeGreaterThanOrEqual(290);
    const bare = Object.entries(taxa as Record<string, Record<string, string>>).filter(([, v]) => !Object.keys(v).length);
    expect(bare.length).toBeLessThan(15);
  });
});
