import 'dart:convert';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:openbird/services/analytics_observer.dart';
import 'package:openbird/services/analytics_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class _Sent {
  _Sent(this.request, this.events);
  final http.Request request;
  final List<Map<String, dynamic>> events;
}

void main() {
  late List<_Sent> sent;
  late DateTime now;
  late bool failNetwork;

  AnalyticsService make() {
    return AnalyticsService(
      client: MockClient((request) async {
        if (failNetwork) throw Exception('offline');
        sent.add(_Sent(request, (jsonDecode(request.body)['events'] as List).cast<Map<String, dynamic>>()));
        return http.Response('', 204);
      }),
      baseUrl: 'https://api.example.org',
      clock: () => now,
      flushDelay: const Duration(days: 1), // flush explicitly in tests
    );
  }

  setUp(() {
    SharedPreferences.setMockInitialValues({});
    sent = [];
    failNetwork = false;
    now = DateTime(2026, 10, 16, 12);
  });

  test('is disabled until init, so nothing is queued or sent', () async {
    final service = make();
    service.track('search', query: 'owl');
    await service.flush();
    expect(sent, isEmpty);
    expect(service.enabled, isFalse);
  });

  test('init enables it by default and keeps one visitor id on the device', () async {
    final first = make();
    await first.init();
    first.track('pageview', path: '/');
    await first.flush();
    final second = make();
    await second.init();
    second.track('pageview', path: '/');
    await second.flush();
    expect(sent[0].events.single['visitor'], isNotEmpty);
    expect(sent[1].events.single['visitor'], sent[0].events.single['visitor']);
    expect(sent[1].events.single['session'], isNot(sent[0].events.single['session']));
  });

  test('sends a batch to /analytics/event as text/plain with an app user agent', () async {
    final service = make();
    await service.init();
    service.language = 'fa';
    service.track('search', query: 'owl', value: 12, path: '/');
    service.track('bird_click', bird: 'Parus major', source: 'search', query: 'owl');
    await service.flush();

    expect(sent, hasLength(1));
    final request = sent.single.request;
    expect(request.url.toString(), 'https://api.example.org/analytics/event');
    expect(request.headers['Content-Type'], startsWith('text/plain'));
    expect(request.headers['User-Agent'], contains('OpenBirdApp'));
    expect(request.headers['User-Agent'], contains('Mobile'));
    final events = sent.single.events;
    expect(events.map((e) => e['type']), ['search', 'bird_click']);
    expect(events[0], containsPair('query', 'owl'));
    expect(events[0], containsPair('value', 12));
    expect(events[0], containsPair('lang', 'fa'));
    expect(events[1], containsPair('bird', 'Parus major'));
    expect(events[1], containsPair('source', 'search'));
  });

  test('screen() records a page view, then the time spent when the next screen opens', () async {
    final service = make();
    await service.init();
    service.screen('/');
    now = now.add(const Duration(seconds: 12));
    service.screen('/taxonomy');
    service.screen('/taxonomy'); // same screen again: ignored
    await service.flush();

    final events = sent.single.events;
    expect(events.map((e) => '${e['type']} ${e['path']}'), ['pageview /', 'page_leave /', 'pageview /taxonomy']);
    expect(events[1]['value'], 12000);
  });

  test('time in the background is not counted', () async {
    final service = make();
    await service.init();
    service.screen('/');
    now = now.add(const Duration(seconds: 5));
    service.onBackground(); // sends immediately
    await Future<void>.delayed(Duration.zero);
    expect(sent.single.events.last, containsPair('type', 'page_leave'));
    expect(sent.single.events.last['value'], 5000);

    now = now.add(const Duration(hours: 3)); // app stays in the background
    service.onForeground();
    now = now.add(const Duration(seconds: 7));
    service.screen('/favorites');
    await service.flush();
    final leave = sent.last.events.firstWhere((e) => e['type'] == 'page_leave');
    expect(leave['value'], 7000);
  });

  test('opting out clears the queue, stops tracking and is remembered', () async {
    final service = make();
    await service.init();
    service.track('search', query: 'owl');
    await service.setEnabled(false);
    service.track('search', query: 'eagle');
    service.screen('/');
    await service.flush();
    expect(sent, isEmpty);

    final next = make();
    await next.init();
    expect(next.enabled, isFalse);
  });

  test('flushes by itself once 20 events are queued', () async {
    final service = make();
    await service.init();
    for (var i = 0; i < 20; i++) {
      service.track('search', query: 'q$i');
    }
    await Future<void>.delayed(Duration.zero);
    expect(sent, hasLength(1));
    expect(sent.single.events, hasLength(20));
  });

  test('network errors never reach the app', () async {
    final service = make();
    await service.init();
    failNetwork = true;
    service.track('search', query: 'owl');
    await service.flush(); // must not throw
    expect(sent, isEmpty);
  });

  test('observer maps routes to dashboard paths', () {
    AnalyticsService.instance.tabPath = '/taxonomy';
    expect(AnalyticsObserver.pathFor(const RouteSettings(name: '/home')), '/taxonomy');
    expect(
      AnalyticsObserver.pathFor(const RouteSettings(name: '/species', arguments: {'scientificName': 'Parus major'})),
      '/species/Parus%20major',
    );
    expect(
      AnalyticsObserver.pathFor(const RouteSettings(name: '/family', arguments: {'familyName': 'Paridae'})),
      '/family/Paridae',
    );
    expect(AnalyticsObserver.pathFor(const RouteSettings(name: '/')), isNull); // splash is not tracked
    expect(AnalyticsObserver.pathFor(null), isNull);
    AnalyticsService.instance.tabPath = '/';
  });
}
