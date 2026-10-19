import 'package:flutter_test/flutter_test.dart';
import 'package:openbird/models/species.dart';
import 'package:openbird/services/api_mapper.dart';

void main() {
  group('search results', () {
    test('a sentence keeps how the server understood it', () {
      final r = searchResultFromApi({
        'hits': [
          {'scientific_name': 'Strix aluco', 'common_name_en': 'Tawny Owl', 'order': 'Strigiformes', 'family': 'Strigidae', 'iucn_status': 'EN'},
        ],
        'total': 1,
        'interpreted': {
          'filters': {'iucn_status': ['CR', 'EN', 'VU'], 'order': ['Strigiformes']},
          'words': ['owl'],
          'ignored': ['iran'],
        },
      }, 'endangered owls in Iran');
      expect(r.isSentence, isTrue);
      expect(r.interpretedFilters['iucn_status'], ['CR', 'EN', 'VU']);
      expect(r.interpretedWords, ['owl']);
      expect(r.ignoredWords, ['iran']);
      expect(r.correctedQuery, isNull);
    });

    test('a fixed typo is reported', () {
      final r = searchResultFromApi({'hits': [], 'total': 0, 'corrected_query': 'penguin'}, 'pengiun');
      expect(r.correctedQuery, 'penguin');
      expect(r.isSentence, isFalse);
    });

    test('a plain search has no interpretation', () {
      final r = searchResultFromApi({'hits': [], 'total': 0}, 'parus');
      expect(r.isSentence, isFalse);
      expect(r.correctedQuery, isNull);
      expect(r.ignoredWords, isEmpty);
    });
  });

  group('taxonomy', () {
    test('the slim per-language tree gives the species their name in that language', () {
      final tree = {
        'Strigiformes': {
          'Strigidae': {
            'Strix': [
              {'scientific': 'Strix aluco', 'id': 'BN1', 'name': 'جغد', 'common_en': 'Tawny Owl'},
            ],
          },
        },
      };
      final list = speciesInFamilyFromTree(tree, 'Strigidae', lang: 'fa');
      expect(list, hasLength(1));
      expect(list.first.getCommonName('fa'), 'جغد');
      expect(list.first.commonNameEn, 'Tawny Owl');
      expect(list.first.family, 'Strigidae');
    });
  });

  group('photos', () {
    final base = {
      'names': {'scientific': 'Parus major', 'en': 'Great Tit'},
    };

    test('a species lists its photos with credit and a URL on the API', () {
      final sp = Species.fromJson(flattenSpeciesJson({
        ...base,
        'images': [
          {'file': 'images/passeriformes/paridae/parus-major/1.jpg', 'author': 'Jane Doe', 'license': 'CC-BY-4.0', 'source': 'iNaturalist', 'page': 'https://example.org/1'},
          {'oops': 1}, // unreadable entries are skipped, never fatal
        ],
      }));
      expect(sp.photos, hasLength(1));
      expect(sp.photos.first.author, 'Jane Doe');
      expect(sp.photos.first.url('https://api.example.org'), 'https://api.example.org/images/passeriformes/paridae/parus-major/1.jpg');
      expect(sp.photos.first.licenseUrl, contains('licenses/by/4.0'));
    });

    test('a single photo or no photo also parses', () {
      final one = Species.fromJson(flattenSpeciesJson({
        ...base,
        'image': {'file': 'images/a/b/c/1.jpg', 'license': 'CC0-1.0'},
      }));
      expect(one.photos, hasLength(1));
      expect(one.photos.first.licenseUrl, contains('publicdomain/zero'));
      expect(Species.fromJson(flattenSpeciesJson(base)).photos, isEmpty);
    });
  });
}
