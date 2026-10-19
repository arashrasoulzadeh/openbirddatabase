import 'package:flutter/foundation.dart';
import 'package:openbird/providers/theme_provider.dart';
import 'package:openbird/providers/language_provider.dart';
import 'package:openbird/services/analytics_service.dart';
import 'package:openbird/services/api_service.dart';
import 'package:openbird/models/species.dart';

class AppProvider extends ChangeNotifier {
  ThemeProvider? _themeProvider;
  LanguageProvider? _languageProvider;
  ApiService? _apiService;
  bool _isInitialized = false;
  String? _error;

  bool get isInitialized => _isInitialized;
  String? get error => _error;
  ApiService? get apiService => _apiService;

  void initialize(ThemeProvider theme, LanguageProvider language) {
    _themeProvider = theme;
    _languageProvider = language;
    _apiService = ApiService();
    _isInitialized = true;
    notifyListeners();
  }

  Future<SearchResult> searchSpecies(String query) async {
    if (_apiService == null) throw StateError('App not initialized');
    try {
      _error = null;
      notifyListeners();
      final result = await _apiService!.searchSpecies(query, lang: _languageProvider?.locale.languageCode);
      AnalyticsService.instance.track('search', query: query, value: result.total, path: '/');
      return result;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      rethrow;
    }
  }

  Future<Species> getSpecies(String scientificName) async {
    if (_apiService == null) throw StateError('App not initialized');
    try {
      _error = null;
      notifyListeners();
      return await _apiService!.getSpecies(scientificName);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      rethrow;
    }
  }

  Future<List<TaxonomyNode>> getTaxonomy() async {
    if (_apiService == null) throw StateError('App not initialized');
    try {
      _error = null;
      notifyListeners();
      return await _apiService!.getTaxonomy(lang: _languageProvider?.locale.languageCode);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      rethrow;
    }
  }

  Future<List<Species>> getSpeciesByFamily(String family) async {
    if (_apiService == null) throw StateError('App not initialized');
    try {
      _error = null;
      notifyListeners();
      return await _apiService!.getSpeciesByFamily(family, lang: _languageProvider?.locale.languageCode);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      rethrow;
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }

  @override
  void dispose() {
    _apiService?.dispose();
    super.dispose();
  }
}