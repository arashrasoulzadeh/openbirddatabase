import 'dart:convert';
import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:openbird/models/species.dart';
import 'package:openbird/services/api_mapper.dart';
import 'package:yaml/yaml.dart';

dynamic plain(dynamic y) {
  if (y is YamlMap) return {for (final e in y.entries) e.key.toString(): plain(e.value)};
  if (y is YamlList) return [for (final v in y) plain(v)];
  if (y is double && (y.isNaN || y.isInfinite)) return null;
  return y;
}

void main() {
  final root = Directory.current.parent.path; // repo root (tests run from flutter_app/)

  test('real species files parse via the API mapper (regression: 22163.0 vs int)', () {
    final files = Directory('$root/birds')
        .listSync(recursive: true)
        .whereType<File>()
        .where((f) => f.path.endsWith('.md'))
        .toList();
    expect(files.length, greaterThan(11000));
    files.sort((a, b) => a.path.compareTo(b.path));
    // every 4th file keeps CI fast while still covering all orders
    final sample = [for (var i = 0; i < files.length; i += 4) files[i]];
    final failures = <String, int>{};
    final examples = <String, String>{};
    for (final f in sample) {
      final text = f.readAsStringSync();
      final fm = text.split('---')[1];
      try {
        // Round-trip through JSON exactly like an HTTP response
        final json = jsonDecode(jsonEncode(plain(loadYaml(fm)))) as Map<String, dynamic>;
        final sp = Species.fromJson(flattenSpeciesJson(json));
        expect(sp.scientificName, isNotEmpty);
        sp.getCommonName('fa');
        sp.getIUCNColor();
      } catch (e) {
        final key = e.toString().split('\n').first;
        failures[key] = (failures[key] ?? 0) + 1;
        examples[key] = f.path;
      }
    }
    for (final k in failures.keys) {
      // ignore: avoid_print
      print('FAIL x${failures[k]}: $k  e.g. ${examples[k]}');
    }
    expect(failures, isEmpty);
  }, timeout: const Timeout(Duration(minutes: 10)));

  test('search hits, taxonomy and family lookup map from real index files', () {
    final index = jsonDecode(File('$root/_index/species-index.json').readAsStringSync()) as List;
    final result = searchResultFromApi({'hits': index.take(500).toList(), 'estimatedTotalHits': index.length}, 'q');
    expect(result.species.length, 500);
    expect(result.total, index.length);
    final tree = jsonDecode(File('$root/_index/taxonomy-tree.json').readAsStringSync()) as Map<String, dynamic>;
    final nodes = taxonomyFromApi(tree);
    expect(nodes.length, 45);
    expect(nodes.first.children, isNotEmpty);
    final fam = speciesInFamilyFromTree(tree, 'Paridae');
    expect(fam, isNotEmpty);
    expect(fam.first.family, 'Paridae');
    expect(fam.any((s) => s.getCommonName('es') != s.commonNameEn), isTrue);
  });
}
