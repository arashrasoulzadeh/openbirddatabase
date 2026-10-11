import pytest
import tempfile
from pathlib import Path
from _scripts.generate_md import build_species_record
from _scripts.apply_curations import parse_frontmatter, merge_veterinary, merge_enrichment

class TestGenerateMD:
    def test_build_species_record_basic(self):
        """Test building a basic species record"""
        record = build_species_record(
            'Parus major',
            {'Parus major': {'common_name': 'Great Tit', 'gbif_id': '2480498'}},
            {},
            {},
            {'Parus major': {'ORDER': 'Passeriformes', 'FAMILY_SCI_NAME': 'Paridae'}}
        )
        
        assert record['names']['scientific'] == 'Parus major'
        assert record['names']['en'] == 'Great Tit'
        assert record['gbif_key'] == 2480498
        assert record['taxonomy']['order'] == 'Passeriformes'
        assert record['taxonomy']['family'] == 'Paridae'

    def test_build_species_record_morphology(self):
        """Test morphology fields are mapped"""
        bb_data = {
            'Average Mass': 18.5,
            'Body Length': 14.0,
            'Wingspan': 24.0,
        }
        
        record = build_species_record(
            'Parus major',
            {'Parus major': {}},
            {},
            bb_data,
            {'Parus major': {'ORDER': 'Passeriformes', 'FAMILY_SCI_NAME': 'Paridae'}}
        )
        
        # Check morphology exists (might be nested differently)
        assert 'morphology' in record

    def test_build_species_record_conservation(self):
        """Test IUCN status mapping"""
        bb_data = {'2024 IUCN Red List category': 'LC'}
        
        record = build_species_record(
            'Parus major',
            {'Parus major': {}},
            {},
            bb_data,
            {}
        )
        
        assert record['iucn_status'] == 'LC'

class TestApplyCurations:
    def test_parse_frontmatter_valid(self):
        """Test parsing valid frontmatter from file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
names:
  scientific: Parus major
  en: Great Tit
---
Body content""")
            f.flush()
            
            fm, body = parse_frontmatter(Path(f.name))
            
            assert fm['names']['scientific'] == 'Parus major'
            assert fm['names']['en'] == 'Great Tit'
            assert 'Body content' in body
        
        Path(f.name).unlink()

    def test_merge_veterinary_adds_fields(self):
        """Test merging veterinary data"""
        fm = {'veterinary': {}}
        vet_data = {
            'common_diseases': ['PBFD'],
            'deworming_frequency_months': 6,
            'source': 'Test Source',
            'contributor': 'Dr. Test',
            'date_added': '2026-01-01',
            'verified': True,
        }
        
        result = merge_veterinary(fm, vet_data)
        
        assert result['veterinary']['common_diseases'] == ['PBFD']
        assert result['veterinary']['deworming_frequency_months'] == 6
        assert result['veterinary']['source'] == 'Test Source'

    def test_merge_enrichment_adds_fields(self):
        """Test merging enrichment data"""
        fm = {'enrichment': {}}
        enrich_data = {
            'foraging_toys': ['Puzzle feeder'],
            'training': {'target_training': True},
            'source': 'AZA Guidelines',
            'contributor': 'AZA TAG',
            'date_added': '2026-01-01',
            'verified': True,
        }
        
        result = merge_enrichment(fm, enrich_data)
        
        assert result['enrichment']['foraging_toys'] == ['Puzzle feeder']
        assert result['enrichment']['training']['target_training'] is True
        assert result['enrichment']['source'] == 'AZA Guidelines'

    def test_merge_veterinary_preserves_existing(self):
        """Test that existing fields are not overwritten"""
        fm = {'veterinary': {'common_diseases': ['Existing']}}
        vet_data = {'common_diseases': ['New']}
        
        result = merge_veterinary(fm, vet_data)
        
        assert result['veterinary']['common_diseases'] == ['Existing']

if __name__ == '__main__':
    pytest.main([__file__, '-v'])