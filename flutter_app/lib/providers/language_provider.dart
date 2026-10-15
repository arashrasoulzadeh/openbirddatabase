import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:openbird/services/analytics_service.dart';

class LanguageProvider extends ChangeNotifier {
  static const _languageKey = 'app_language';
  
  Locale _locale = const Locale('en');
  Locale get locale => _locale;

  static const supportedLocales = [
    Locale('en'), // English
    Locale('fa'), // Persian
    Locale('ar'), // Arabic
    Locale('es'), // Spanish
    Locale('fr'), // French
    Locale('de'), // German
    Locale('pt'), // Portuguese
    Locale('ru'), // Russian
    Locale('ja'), // Japanese
    Locale('zh'), // Chinese
    Locale('nl'), // Dutch
    Locale('pl'), // Polish
    Locale('tr'), // Turkish
  ];

  static const languageNames = {
    'en': 'English',
    'fa': 'فارسی',
    'ar': 'العربية',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'pt': 'Português',
    'ru': 'Русский',
    'ja': '日本語',
    'zh': '中文',
    'nl': 'Nederlands',
    'pl': 'Polski',
    'tr': 'Türkçe',
  };

  static const nativeNames = {
    'en': 'English',
    'fa': 'فارسی',
    'ar': 'العربية',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'pt': 'Português',
    'ru': 'Русский',
    'ja': '日本語',
    'zh': '中文',
    'nl': 'Nederlands',
    'pl': 'Polski',
    'tr': 'Türkçe',
  };

  Future<void> loadLanguage() async {
    final prefs = await SharedPreferences.getInstance();
    final languageCode = prefs.getString(_languageKey) ?? 'en';
    _locale = Locale(languageCode);
    AnalyticsService.instance.language = languageCode;
    notifyListeners();
  }

  Future<void> setLanguage(String languageCode) async {
    if (!supportedLocales.any((l) => l.languageCode == languageCode)) return;
    
    final previous = _locale.languageCode;
    _locale = Locale(languageCode);
    AnalyticsService.instance
      ..track('language_change', source: previous, query: languageCode)
      ..language = languageCode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_languageKey, languageCode);
    notifyListeners();
  }

  String getLanguageName(String code) => languageNames[code] ?? code;
  String getNativeName(String code) => nativeNames[code] ?? code;
}