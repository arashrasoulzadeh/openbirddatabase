import 'package:openbird/models/species.dart';

/// Language codes the API returns species names for (besides `en`).
const _nameLanguages = ['fa', 'ar', 'es', 'fr', 'de', 'pt', 'ru', 'ja', 'zh', 'nl', 'pl', 'tr'];

/// `/species/{name}` returns the species file frontmatter (nested: `names`, `taxonomy`, ...).
/// [Species.fromJson] expects flat `common_name_xx` / `order` / `family` keys, so flatten first.
Map<String, dynamic> flattenSpeciesJson(Map<String, dynamic> json) {
  final names = (json['names'] as Map?)?.cast<String, dynamic>() ?? const {};
  final taxonomy = (json['taxonomy'] as Map?)?.cast<String, dynamic>() ?? const {};
  final flat = Map<String, dynamic>.from(json);

  flat['scientific_name'] = names['scientific'] ?? json['scientific_name'] ?? '';
  flat['common_name_en'] = names['en'] ?? json['common_name_en'] ?? '';
  for (final lang in _nameLanguages) {
    final name = names[lang] ?? json['common_name_$lang'];
    if (name != null) flat['common_name_$lang'] = name;
  }
  flat['birdnet_id'] = json['birdnet_id'] ?? json['taxon_id'] ?? '';
  flat['order'] = taxonomy['order'] ?? json['order'] ?? '';
  flat['family'] = taxonomy['family'] ?? json['family'] ?? '';
  flat['genus'] = taxonomy['genus'] ?? json['genus'] ?? '';
  flat['species'] = taxonomy['species'] ?? json['species'] ?? '';
  return flat;
}

/// `/search` returns `{hits: [...], total | estimatedTotalHits}` with flat documents.
SearchResult searchResultFromApi(Map<String, dynamic> json, String query) {
  final hits = (json['hits'] as List? ?? const [])
      .map((h) => Species.fromJson((h as Map).cast<String, dynamic>()))
      .toList();
  final total = json['total'] ?? json['estimatedTotalHits'] ?? hits.length;
  return SearchResult(species: hits, total: (total as num).toInt(), query: query);
}

/// `/taxonomy` returns `{order: {family: {genus: [species...]}}}`.
/// The app browses orders -> families, so genera are folded into the family count.
List<TaxonomyNode> taxonomyFromApi(Map<String, dynamic> tree) {
  final orders = <TaxonomyNode>[];
  for (final order in tree.entries) {
    final families = <TaxonomyNode>[];
    var orderCount = 0;
    for (final family in (order.value as Map).entries) {
      var familyCount = 0;
      for (final genus in (family.value as Map).values) {
        familyCount += (genus as List).length;
      }
      orderCount += familyCount;
      families.add(TaxonomyNode(name: family.key as String, rank: 'family', count: familyCount));
    }
    orders.add(TaxonomyNode(
      name: order.key,
      rank: 'order',
      count: orderCount,
      children: families,
    ));
  }
  orders.sort((a, b) => a.name.compareTo(b.name));
  return orders;
}

/// Species of one family, taken from the already-downloaded `/taxonomy` tree.
List<Species> speciesInFamilyFromTree(Map<String, dynamic> tree, String family) {
  final result = <Species>[];
  for (final order in tree.entries) {
    final families = order.value as Map;
    if (!families.containsKey(family)) continue;
    for (final genus in (families[family] as Map).entries) {
      for (final entry in genus.value as List) {
        final sp = (entry as Map).cast<String, dynamic>();
        final names = (sp['names'] as Map?)?.cast<String, dynamic>() ?? const {};
        result.add(Species.fromJson({
          'scientific_name': sp['scientific'],
          'common_name_en': sp['common_en'],
          'common_name_fa': sp['common_fa'],
          for (final e in names.entries) 'common_name_${e.key}': e.value,
          'birdnet_id': sp['id'],
          'order': order.key,
          'family': family,
          'genus': genus.key,
        }));
      }
    }
  }
  return result;
}
