import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:openbird/utils/constants.dart';

/// Anonymous usage statistics, sent to the same API as the website (POST /analytics/event).
///
/// No personal data: the visitor id is a random string stored on the device, nothing else identifies the user.
/// Users can turn it off in Settings. Until [init] has run the service is disabled, so tests and widgets that
/// never call it do not create timers or network traffic.
class AnalyticsService {
  AnalyticsService({
    http.Client? client,
    String? baseUrl,
    DateTime Function()? clock,
    Duration flushDelay = const Duration(seconds: 1),
  })  : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? Constants.apiBaseUrl,
        _now = clock ?? DateTime.now,
        _flushDelay = flushDelay;

  /// App-wide instance (replaced in tests).
  static AnalyticsService instance = AnalyticsService();

  static const _visitorKey = 'analytics_visitor';
  static const _enabledKey = 'analytics_enabled';

  final http.Client _client;
  final String _baseUrl;
  final DateTime Function() _now;
  final Duration _flushDelay;

  final String _session = _randomId();
  String _visitor = _randomId();
  bool _enabled = false;
  final List<Map<String, dynamic>> _queue = [];
  Timer? _timer;
  String? _currentPath;
  DateTime? _since;

  /// Interface language, kept up to date by the language provider.
  String language = 'en';

  /// Screen shown by the bottom navigation ('/', '/taxonomy', '/favorites', '/settings').
  String tabPath = '/';

  bool get enabled => _enabled;

  static String _randomId() {
    final random = Random.secure();
    return List.generate(16, (_) => random.nextInt(256).toRadixString(16).padLeft(2, '0')).join();
  }

  /// Loads the device's visitor id and the user's opt-in choice (on by default). Call once at startup.
  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    final stored = prefs.getString(_visitorKey);
    if (stored != null) {
      _visitor = stored;
    } else {
      await prefs.setString(_visitorKey, _visitor);
    }
    _enabled = prefs.getBool(_enabledKey) ?? true;
  }

  Future<void> setEnabled(bool value) async {
    _enabled = value;
    if (!value) {
      _timer?.cancel();
      _timer = null;
      _queue.clear();
      _currentPath = null;
      _since = null;
    }
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_enabledKey, value);
  }

  /// Queue an event; events are sent in small batches.
  void track(
    String type, {
    String? path,
    String? bird,
    String? query,
    String? source,
    num? value,
  }) {
    if (!_enabled) return;
    _queue.add({
      'type': type,
      'path': path ?? _currentPath ?? '/',
      'visitor': _visitor,
      'session': _session,
      'lang': language,
      if (bird != null) 'bird': bird,
      if (query != null && query.isNotEmpty) 'query': query,
      if (source != null) 'source': source,
      if (value != null) 'value': value,
    });
    if (_queue.length >= 20) {
      flush();
    } else {
      _timer ??= Timer(_flushDelay, flush);
    }
  }

  /// A screen came into view: closes the previous one (with the time spent on it) and records a page view.
  void screen(String path) {
    if (!_enabled || path == _currentPath) return;
    _leave();
    _currentPath = path;
    _since = _now();
    track('pageview', path: path);
  }

  void _leave() {
    final path = _currentPath;
    final since = _since;
    if (path != null && since != null) {
      track('page_leave', path: path, value: _now().difference(since).inMilliseconds);
    }
    _since = null;
  }

  /// The app went to the background: record the visible time so far and send everything.
  void onBackground() {
    _leave();
    flush();
  }

  void onForeground() {
    if (_currentPath != null) _since = _now();
  }

  Future<void> flush() async {
    _timer?.cancel();
    _timer = null;
    if (_queue.isEmpty) return;
    final batch = List<Map<String, dynamic>>.of(_queue);
    _queue.clear();
    try {
      await _client.post(
        Uri.parse('$_baseUrl/analytics/event'),
        // text/plain, like the website's beacon; the API parses the body as JSON either way
        headers: {
          'Content-Type': 'text/plain; charset=utf-8',
          'User-Agent': 'OpenBirdApp/1.0 (Mobile; ${defaultTargetPlatform.name})',
        },
        body: jsonEncode({'events': batch}),
      );
    } catch (_) {
      // Statistics must never affect the app: drop the batch if the network is unavailable
    }
  }
}
