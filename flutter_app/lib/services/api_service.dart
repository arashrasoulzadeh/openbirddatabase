import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:openbird/models/species.dart';
import 'package:openbird/utils/constants.dart';

class ApiService {
  final String baseUrl;
  final http.Client _client;

  ApiService({String? baseUrl, http.Client? client})
      : baseUrl = baseUrl ?? Constants.apiBaseUrl,
        _client = client ?? http.Client();

  Future<SearchResult> searchSpecies(String query, {int limit = 20}) async {
    final uri = Uri.parse('$baseUrl/api/search').replace(queryParameters: {
      'q': query,
      'limit': limit.toString(),
    });
    
    final response = await _client.get(uri, headers: _headers);
    _checkResponse(response);
    return SearchResult.fromJson(json.decode(response.body));
  }

  Future<Species> getSpecies(String scientificName) async {
    final uri = Uri.parse('$baseUrl/api/species/${Uri.encodeComponent(scientificName)}');
    final response = await _client.get(uri, headers: _headers);
    _checkResponse(response);
    return Species.fromJson(json.decode(response.body));
  }

  Future<List<TaxonomyNode>> getTaxonomy() async {
    final uri = Uri.parse('$baseUrl/api/taxonomy');
    final response = await _client.get(uri, headers: _headers);
    _checkResponse(response);
    final List data = json.decode(response.body);
    return data.map((j) => TaxonomyNode.fromJson(j)).toList();
  }

  Future<List<Species>> getSpeciesByFamily(String family) async {
    final uri = Uri.parse('$baseUrl/api/taxonomy/family')
        .replace(queryParameters: {'family': family});
    final response = await _client.get(uri, headers: _headers);
    _checkResponse(response);
    final List data = json.decode(response.body);
    return data.map((j) => Species.fromJson(j)).toList();
  }

  Future<List<Species>> getSpeciesByOrder(String order) async {
    final uri = Uri.parse('$baseUrl/api/taxonomy/order')
        .replace(queryParameters: {'order': order});
    final response = await _client.get(uri, headers: _headers);
    _checkResponse(response);
    final List data = json.decode(response.body);
    return data.map((j) => Species.fromJson(j)).toList();
  }

  Future<Map<String, dynamic>> getFilters() async {
    final uri = Uri.parse('$baseUrl/api/filters');
    final response = await _client.get(uri, headers: _headers);
    _checkResponse(response);
    return json.decode(response.body);
  }

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