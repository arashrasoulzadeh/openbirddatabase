import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:openbird/models/species.dart';
import 'package:openbird/services/api_mapper.dart';
import 'package:openbird/utils/constants.dart';

class ApiService {
  final String baseUrl;
  final http.Client _client;

  ApiService({String? baseUrl, http.Client? client})
      : baseUrl = baseUrl ?? Constants.apiBaseUrl,
        _client = client ?? http.Client();

  final Map<String, Map<String, dynamic>> _taxonomyCache = {};

  /// [lang] makes each hit carry only English and that language's name (a third of the bytes). Sentences such as
  /// "endangered owls in forests" and misspelled names are understood by the server in every language.
  ///
  /// [filters] are exact matches (`iucn_status`, `primary_habitat`, `primary_diet`, `migration_status`, `order`);
  /// an empty [query] with filters lists the matching species. [offset] pages through the results.
  Future<SearchResult> searchSpecies(
    String query, {
    int limit = 20,
    int offset = 0,
    String? lang,
    Map<String, String> filters = const {},
  }) async {
    final uri = Uri.parse('$baseUrl/search').replace(queryParameters: {
      'q': query,
      'limit': limit.toString(),
      if (offset > 0) 'offset': offset.toString(),
      if (lang != null && lang.isNotEmpty) 'lang': lang,
      for (final e in filters.entries)
        if (e.value.isNotEmpty) e.key: e.value,
    });
    final response = await _client.get(uri, headers: _headers);
    _checkResponse(response);
    return searchResultFromApi(_decodeMap(response), query);
  }

  Future<Species> getSpecies(String scientificName) async {
    final uri = Uri.parse('$baseUrl/species/${Uri.encodeComponent(scientificName)}')
        .replace(queryParameters: {'lang': 'en'});
    final response = await _client.get(uri, headers: _headers);
    _checkResponse(response);
    return Species.fromJson(flattenSpeciesJson(_decodeMap(response)));
  }

  /// Downloads the taxonomy tree once per language and keeps it for family lookups. With a language the server
  /// sends one common name per species (about a quarter of the full tree).
  Future<Map<String, dynamic>> _loadTaxonomy(String? lang) async {
    final key = lang ?? '';
    final cached = _taxonomyCache[key];
    if (cached != null) return cached;
    final uri = Uri.parse('$baseUrl/taxonomy').replace(queryParameters: {
      if (lang != null && lang.isNotEmpty) 'lang': lang,
    });
    final response = await _client.get(uri, headers: _headers);
    _checkResponse(response);
    return _taxonomyCache[key] = _decodeMap(response);
  }

  Future<List<TaxonomyNode>> getTaxonomy({String? lang}) async {
    return taxonomyFromApi(await _loadTaxonomy(lang));
  }

  Future<List<Species>> getSpeciesByFamily(String family, {String? lang}) async {
    return speciesInFamilyFromTree(await _loadTaxonomy(lang), family, lang: lang);
  }

  Future<List<Species>> getSpeciesByOrder(String order) async {
    final uri = Uri.parse('$baseUrl/taxonomy/${Uri.encodeComponent(order)}');
    final response = await _client.get(uri, headers: _headers);
    _checkResponse(response);
    final tree = {order: _decodeMap(response)};
    return [
      for (final family in (tree[order] as Map).keys)
        ...speciesInFamilyFromTree(tree, family as String),
    ];
  }

  /// A random species (search-hit shape).
  Future<Species> getRandomSpecies() async {
    final response = await _client.get(Uri.parse('$baseUrl/random'), headers: _headers);
    _checkResponse(response);
    return Species.fromJson(_decodeMap(response));
  }

  Future<Map<String, dynamic>> getFilters() async {
    final response = await _client.get(Uri.parse('$baseUrl/filters'), headers: _headers);
    _checkResponse(response);
    return _decodeMap(response);
  }

  Map<String, dynamic> _decodeMap(http.Response response) =>
      (json.decode(utf8.decode(response.bodyBytes)) as Map).cast<String, dynamic>();

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  void _checkResponse(http.Response response) {
    if (response.statusCode >= 400) {
      throw ApiException('API Error: ${response.statusCode} - ${response.body}');
    }
  }

  void dispose() {
    _client.close();
  }
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);
  @override
  String toString() => message;
}