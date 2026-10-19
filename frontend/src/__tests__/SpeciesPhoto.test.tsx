import { fireEvent, render, screen } from '@testing-library/react';
import SpeciesPhoto from '@/components/SpeciesPhoto';

describe('SpeciesPhoto', () => {
  it('renders nothing for a species without a photo', () => {
    const { container } = render(<SpeciesPhoto image={undefined} alt="Great Tit" label="Photo" />);
    expect(container).toBeEmptyDOMElement();
  });

  it('shows the photo with author, licence and a link to the source', () => {
    render(
      <SpeciesPhoto
        image={{ file: 'images/passeriformes/paridae/parus-major/1.jpg', author: 'Jane Doe', license: 'CC-BY-4.0', source: 'iNaturalist via GBIF', page: 'https://www.inaturalist.org/photos/1' }}
        alt="Great Tit"
        label="Photo"
      />,
    );
    expect(screen.getByAltText('Great Tit').getAttribute('src')).toMatch(/\/images\/passeriformes\/paridae\/parus-major\/1\.jpg$/);
    expect(screen.getByText(/Jane Doe/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'CC-BY-4.0' }).getAttribute('href')).toContain('creativecommons.org/licenses/by/4.0');
    expect(screen.getByRole('link', { name: /iNaturalist/ }).getAttribute('href')).toBe('https://www.inaturalist.org/photos/1');
  });

  it('shows thumbnails for several photos and switches the large photo and its credit', () => {
    const photos = [
      { file: 'images/passeriformes/paridae/parus-major/1.jpg', author: 'Jane Doe', license: 'CC-BY-4.0', source: 'iNaturalist', page: 'https://example.org/1' },
      { file: 'images/passeriformes/paridae/parus-major/2.jpg', author: 'John Roe', license: 'CC0-1.0', source: 'iNaturalist', page: 'https://example.org/2' },
    ];
    render(<SpeciesPhoto image={photos[0]} images={photos} alt="Great Tit" label="Photo" />);
    expect(screen.getAllByRole('button')).toHaveLength(2);
    expect(screen.getByText(/Jane Doe/)).toBeInTheDocument();
    fireEvent.click(screen.getAllByRole('button')[1]);
    expect(screen.getByText(/John Roe/)).toBeInTheDocument();
    expect(screen.getByAltText('Great Tit').getAttribute('src')).toMatch(/\/parus-major\/2\.jpg$/);
  });
});
