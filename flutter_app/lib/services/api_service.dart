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

  Map<String, dynamic>? _taxonomyCache;

  Future<SearchResult> searchSpecies(String query, {int limit = 20}) async {
    final uri = Uri.parse('$baseUrl/search').replace(queryParameters: {
      'q': query,
      'limit': limit.toString(),
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

  /// Downloads the full taxonomy tree once and keeps it for family lookups.
  Future<Map<String, dynamic>> _loadTaxonomy() async {
    final cached = _taxonomyCache;
    if (cached != null) return cached;
    final response = await _client.get(Uri.parse('$baseUrl/taxonomy'), headers: _headers);
    _checkResponse(response);
    return _taxonomyCache = _decodeMap(response);
  }

  Future<List<TaxonomyNode>> getTaxonomy() async {
    return taxonomyFromApi(await _loadTaxonomy());
  }

  Future<List<Species>> getSpeciesByFamily(String family) async {
    return speciesInFamilyFromTree(await _loadTaxonomy(), family);
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