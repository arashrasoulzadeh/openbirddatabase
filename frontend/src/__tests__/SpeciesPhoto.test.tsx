import { render, screen } from '@testing-library/react';
import SpeciesPhoto from '@/components/SpeciesPhoto';

describe('SpeciesPhoto', () => {
  it('renders nothing for a species without a photo', () => {
    const { container } = render(<SpeciesPhoto image={undefined} alt="Great Tit" label="Photo" />);
    expect(container).toBeEmptyDOMElement();
  });

  it('shows the photo with author, licence and a link to the source', () => {
    render(
      <SpeciesPhoto
        image={{ file: 'images/parus-major.jpg', author: 'Jane Doe', license: 'CC-BY-4.0', source: 'iNaturalist via GBIF', page: 'https://www.inaturalist.org/photos/1' }}
        alt="Great Tit"
        label="Photo"
      />,
    );
    expect(screen.getByAltText('Great Tit').getAttribute('src')).toMatch(/\/images\/parus-major\.jpg$/);
    expect(screen.getByText(/Jane Doe/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'CC-BY-4.0' }).getAttribute('href')).toContain('creativecommons.org/licenses/by/4.0');
    expect(screen.getByRole('link', { name: /iNaturalist/ }).getAttribute('href')).toBe('https://www.inaturalist.org/photos/1');
  });
});
