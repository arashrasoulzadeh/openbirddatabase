import 'package:flutter_test/flutter_test.dart';
import 'package:openbird/models/species.dart';

void main() {
  group('Species Model', () {
    test('fromJson creates Species with all fields', () {
      final json = {
        'scientific_name': 'Parus major',
        'common_name_en': 'Great Tit',
        'common_name_fa': 'کلاغ‌کوچک بزرگ',
        'common_name_ar': 'العصفور الكبير',
        'common_name_es': 'Carbonero común',
        'common_name_fr': 'Mésange charbonnière',
        'common_name_de': 'Kohlmeise',
        'common_name_pt': 'Chapim-real',
        'common_name_ru': 'Большая синица',
        'common_name_ja': 'シジュウカラ',
        'common_name_zh': '大山雀',
        'common_name_nl': 'Koolmees',
        'common_name_pl': 'Sosnowka wielka',
        'common_name_tr': 'Başkuşu',
        'birdnet_id': 'BT00012345',
        'ebird_code': 'gretit',
        'gbif_key': 2480498,
        'avibase_id': 'ABCD1234',
        'iucn_status': 'LC',
        'taxon_order': 12345,
        'order': 'Passeriformes',
        'family': 'Paridae',
        'genus': 'Parus',
        'species': 'major',
        'morphology': {
          'body_mass_g': 18.5,
          'body_length_cm': 14.0,
          'wingspan_cm': 24.0,
          'bill_length_mm': 12.5,
          'tarsus_length_mm': 18.2,
          'wing_length_mm': 72.0,
          'tail_length_mm': 58.0,
        },
        'distribution': {
          'breeding_range': 'Europe, Asia',
          'non_breeding_range': 'Same',
          'biogeographic_realms': ['Palearctic'],
          'island_endemic': false,
          'endemic_region': null,
        },
        'habitat': {
          'primary': 'Deciduous forest',
          'secondary': ['Mixed forest', 'Urban parks'],
          'habitat_breadth': 3,
          'elevational_min_m': 0,
          'elevational_max_m': 2000,
          'habitat_types': ['Forest', 'Urban'],
          'microhabitat': 'Canopy',
        },
        'diet': {
          'categories': {'insects': 0.6, 'seeds': 0.4},
          'diet_breadth': 2,
          'primary': 'Insectivore',
          'foraging_strategy': 'Gleaning',
        },
        'behavior': {
          'sociality': 'Pairs and family groups',
          'flock_size': 'Small groups',
          'territoriality': 'Territorial',
          'migration_status': 'Resident',
          'movement_type': 'Sedentary',
          'dispersal_distance_km': 5.0,
          'activity_pattern': 'Diurnal',
        },
        'reproduction': {
          'clutch_size_min': 5,
          'clutch_size_max': 12,
          'clutch_size_mean': 8.5,
          'egg_length_mm': 16.2,
          'egg_width_mm': 12.8,
          'incubation_days': 14,
          'fledging_days': 18,
          'broods_per_year': 1,
          'nest_type': 'Cavity',
          'nest_placement': 'Tree cavity',
          'nest_material': ['Moss', 'Hair', 'Feathers'],
          'mating_system': 'Monogamous',
          'parental_care': 'Biparental',
        },
        'demography': {
          'generation_length_years': 2.5,
          'max_longevity_years': 10,
          'annual_survival_adult': 0.6,
          'annual_survival_juvenile': 0.3,
          'population_trend': 'Stable',
          'population_size': 'Large',
          'density_individuals_per_km2': 50.0,
        },
        'conservation': {
          'iucn_status': 'LC',
          'population_trend': 'Stable',
          'threats': ['Habitat loss'],
          'conservation_actions': ['Protected areas'],
        },
        'veterinary': {
          'common_diseases': ['Avian pox'],
          'vaccination_schedule': ['None routine'],
          'deworming_frequency_months': 6,
          'health_check_frequency_months': 12,
          'zoonotic_risks': ['Salmonella'],
          'emergency_signs': ['Lethargy', 'Fluffed feathers'],
          'vet_specialist_type': 'Avian veterinarian',
          'source': 'Avian Medicine 2023',
          'contributor': 'Dr. Smith',
          'date_added': '2026-01-01',
          'verified': true,
        },
        'enrichment': {
          'foraging_toys': ['Puzzle feeder', 'Scatter feeding'],
          'social_enrichment': 'Conspecifics recommended',
          'cognitive_toys': ['Color discrimination'],
          'bathing': 'Daily misting',
          'training': {
            'target_training': true,
            'recall_training': true,
            'harness_training': 'Possible',
          },
          'play_behaviors': ['Object manipulation'],
          'environmental_enrichment': ['Variable perches', 'UV lighting'],
          'source': 'AZA Guidelines',
          'contributor': 'AZA TAG',
          'date_added': '2026-01-01',
          'verified': true,
        },
        'sources': ['BirdNET', 'BIRDBASE', 'AVONICHE'],
        'data_quality': 'High',
        'last_updated': '2026-01-15',
      };

      final species = Species.fromJson(json);

      expect(species.scientificName, 'Parus major');
      expect(species.commonNameEn, 'Great Tit');
      expect(species.commonNameFa, 'کلاغ‌کوچک بزرگ');
      expect(species.commonNameAr, 'العصفور الكبير');
      expect(species.commonNameEs, 'Carbonero común');
      expect(species.commonNameFr, 'Mésange charbonnière');
      expect(species.commonNameDe, 'Kohlmeise');
      expect(species.commonNamePt, 'Chapim-real');
      expect(species.commonNameRu, 'Большая синица');
      expect(species.commonNameJa, 'シジュウカラ');
      expect(species.commonNameZh, '大山雀');
      expect(species.commonNameNl, 'Koolmees');
      expect(species.commonNamePl, 'Sosnowka wielka');
      expect(species.commonNameTr, 'Başkuşu');
      expect(species.birdnetId, 'BT00012345');
      expect(species.ebirdCode, 'gretit');
      expect(species.gbifKey, 2480498);
      expect(species.avibaseId, 'ABCD1234');
      expect(species.iucnStatus, 'LC');
      expect(species.taxonOrder, 12345);
      expect(species.order, 'Passeriformes');
      expect(species.family, 'Paridae');
      expect(species.genus, 'Parus');
      expect(species.species, 'major');

      // Test morphology
      expect(species.morphology!.bodyMassG, 18.5);
      expect(species.morphology!.bodyLengthCm, 14.0);
      expect(species.morphology!.wingspanCm, 24.0);

      // Test distribution
      expect(species.distribution!.breedingRange, 'Europe, Asia');
      expect(species.distribution!.biogeographicRealms, ['Palearctic']);

      // Test habitat
      expect(species.habitat!.primary, 'Deciduous forest');
      expect(species.habitat!.habitatTypes, ['Forest', 'Urban']);

      // Test diet
      expect(species.diet!.categories!['insects'], 0.6);
      expect(species.diet!.primary, 'Insectivore');

      // Test behavior
      expect(species.behavior!.sociality, 'Pairs and family groups');
      expect(species.behavior!.migrationStatus, 'Resident');

      // Test reproduction
      expect(species.reproduction!.clutchSizeMin, 5);
      expect(species.reproduction!.clutchSizeMax, 12);
      expect(species.reproduction!.nestMaterial, ['Moss', 'Hair', 'Feathers']);

      // Test demography
      expect(species.demography!.generationLengthYears, 2.5);
      expect(species.demography!.maxLongevityYears, 10);

      // Test conservation
      expect(species.conservation!.iucnStatus, 'LC');
      expect(species.conservation!.threats, ['Habitat loss']);

      // Test veterinary
      expect(species.veterinary!.commonDiseases, ['Avian pox']);
      expect(species.veterinary!.dewormingFrequencyMonths, 6);
      expect(species.veterinary!.verified, true);

      // Test enrichment
      expect(species.enrichment!.foragingToys, ['Puzzle feeder', 'Scatter feeding']);
      expect(species.enrichment!.training!.targetTraining, true);
      expect(species.enrichment!.verified, true);

      // Test sources
      expect(species.sources, ['BirdNET', 'BIRDBASE', 'AVONICHE']);
      expect(species.dataQuality, 'High');
      expect(species.lastUpdated, '2026-01-15');
    });

    test('getCommonName returns correct language', () {
      final species = Species(
        scientificName: 'Test',
        commonNameEn: 'English',
        commonNameFa: 'Persian',
        commonNameAr: 'Arabic',
        birdnetId: '',
        ebirdCode: '',
        gbifKey: 0,
        avibaseId: '',
        iucnStatus: 'LC',
        taxonOrder: 0,
        order: '',
        family: '',
        genus: '',
        species: '',
      );

      expect(species.getCommonName('en'), 'English');
      expect(species.getCommonName('fa'), 'Persian');
      expect(species.getCommonName('ar'), 'Arabic');
      expect(species.getCommonName('es'), 'English'); // fallback
      expect(species.getCommonName('xx'), 'English'); // unknown fallback
    });

    test('getIUCNColor returns correct colors', () {
      final species = Species(
        scientificName: 'Test',
        commonNameEn: 'Test',
        birdnetId: '',
        ebirdCode: '',
        gbifKey: 0,
        avibaseId: '',
        iucnStatus: 'LC',
        taxonOrder: 0,
        order: '',
        family: '',
        genus: '',
        species: '',
      );

      expect(species.getIUCNColor(), Colors.green);
      
      species.iucnStatus = 'EN';
      expect(species.getIUCNColor(), Colors.red);
      
      species.iucnStatus = 'CR';
      expect(species.getIUCNColor(), Colors.red[900]);
      
      species.iucnStatus = 'DD';
      expect(species.getIUCNColor(), Colors.blue);
    });
  });

  group('Morphology Model', () {
    test('fromJson creates Morphology', () {
      final json = {
        'body_mass_g': 20.5,
        'body_length_cm': 15.0,
        'wingspan_cm': 25.0,
        'bill_length_mm': 13.0,
        'tarsus_length_mm': 19.0,
        'wing_length_mm': 75.0,
        'tail_length_mm': 60.0,
      };

      final morph = Morphology.fromJson(json);

      expect(morph.bodyMassG, 20.5);
      expect(morph.bodyLengthCm, 15.0);
      expect(morph.wingspanCm, 25.0);
      expect(morph.billLengthMm, 13.0);
      expect(morph.tarsusLengthMm, 19.0);
      expect(morph.wingLengthMm, 75.0);
      expect(morph.tailLengthMm, 60.0);
    });
  });

  group('TaxonomyNode Model', () {
    test('fromJson creates TaxonomyNode with children', () {
      final json = {
        'name': 'Passeriformes',
        'rank': 'order',
        'scientific_name': 'Passeriformes',
        'count': 100,
        'children': [
          {
            'name': 'Paridae',
            'rank': 'family',
            'scientific_name': 'Paridae',
            'count': 10,
          },
        ],
      };

      final node = TaxonomyNode.fromJson(json);

      expect(node.name, 'Passeriformes');
      expect(node.rank, 'order');
      expect(node.scientificName, 'Passeriformes');
      expect(node.count, 100);
      expect(node.children!.length, 1);
      expect(node.children!.first.name, 'Paridae');
      expect(node.children!.first.rank, 'family');
    });
  });
}