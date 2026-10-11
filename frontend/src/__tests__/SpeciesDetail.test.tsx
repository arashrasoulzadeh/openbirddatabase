import { render, screen } from '@testing-library/react';
import { SpeciesDetail } from '@/components/SpeciesDetail';

const mockSpecies = {
  scientific_name: 'Parus major',
  common_name_en: 'Great Tit',
  common_name_fa: 'کلاغ‌کوچک بزرگ',
  birdnet_id: 'BT00012345',
  ebird_code: 'gretit',
  gbif_key: 2480498,
  avibase_id: 'AVIBASE123',
  iucn_status: 'LC',
  taxon_order: 12345,
  order: 'Passeriformes',
  family: 'Paridae',
  genus: 'Parus',
  species: 'major',
  morphology: {
    body_mass_g: 18.5,
    body_length_cm: 14.0,
    wingspan_cm: 24.0,
  },
  habitat: {
    primary: 'Deciduous forest',
    habitat_types: ['Forest', 'Urban'],
  },
  diet: {
    primary: 'Insectivore',
    diet_breadth: 2,
  },
  sources: ['BirdNET', 'BIRDBASE'],
  data_quality: 'High',
  last_updated: '2026-01-15',
};

describe('SpeciesDetail Component', () => {
  it('renders species name', () => {
    render(<SpeciesDetail species={mockSpecies} />);
    expect(screen.getByText('Great Tit')).toBeInTheDocument();
    expect(screen.getByText('Parus major')).toBeInTheDocument();
  });

  it('renders IUCN status badge', () => {
    render(<SpeciesDetail species={mockSpecies} />);
    expect(screen.getByText('LC')).toBeInTheDocument();
  });

  it('renders order and family', () => {
    render(<SpeciesDetail species={mockSpecies} />);
    expect(screen.getByText('Passeriformes')).toBeInTheDocument();
    expect(screen.getByText('Paridae')).toBeInTheDocument();
  });

  it('renders morphology data', () => {
    render(<SpeciesDetail species={mockSpecies} />);
    expect(screen.getByText('18.5 g')).toBeInTheDocument();
    expect(screen.getByText('14 cm')).toBeInTheDocument();
    expect(screen.getByText('24 cm')).toBeInTheDocument();
  });

  it('renders habitat information', () => {
    render(<SpeciesDetail species={mockSpecies} />);
    expect(screen.getByText('Deciduous forest')).toBeInTheDocument();
    expect(screen.getByText('Forest')).toBeInTheDocument();
    expect(screen.getByText('Urban')).toBeInTheDocument();
  });

  it('renders diet information', () => {
    render(<SpeciesDetail species={mockSpecies} />);
    expect(screen.getByText('Insectivore')).toBeInTheDocument();
  });

  it('renders sources and quality', () => {
    render(<SpeciesDetail species={mockSpecies} />);
    expect(screen.getByText('BirdNET, BIRDBASE')).toBeInTheDocument();
    expect(screen.getByText('High')).toBeInTheDocument();
  });
});

describe('SpeciesDetail with missing data', () => {
  const minimalSpecies = {
    scientific_name: 'Test Species',
    common_name_en: 'Test Bird',
    birdnet_id: '',
    ebird_code: '',
    gbif_key: 0,
    avibase_id: '',
    iucn_status: 'DD',
    taxon_order: 0,
    order: 'TestOrder',
    family: 'TestFamily',
    genus: 'TestGenus',
    species: 'test',
  };

  it('handles missing optional data gracefully', () => {
    render(<SpeciesDetail species={minimalSpecies} />);
    expect(screen.getByText('Test Bird')).toBeInTheDocument();
    expect(screen.getByText('Test Species')).toBeInTheDocument();
    expect(screen.getByText('DD')).toBeInTheDocument();
  });
});