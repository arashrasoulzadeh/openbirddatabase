import 'package:flutter/widgets.dart';
import 'package:openbird/services/analytics_service.dart';

/// Reports every screen the user visits (tabs, species pages, family lists) as a page view with its time on screen.
class AnalyticsObserver extends NavigatorObserver {
  /// Path used for a route in the analytics dashboard, or null for routes that are not tracked (splash...).
  static String? pathFor(RouteSettings? settings) {
    if (settings == null) return null;
    final args = settings.arguments;
    switch (settings.name) {
      case '/home':
        return AnalyticsService.instance.tabPath;
      case '/species':
        if (args is Map && args['scientificName'] != null) {
          return '/species/${Uri.encodeComponent(args['scientificName'].toString())}';
        }
        return null;
      case '/family':
        if (args is Map && args['familyName'] != null) {
          return '/family/${Uri.encodeComponent(args['familyName'].toString())}';
        }
        return null;
      default:
        return null;
    }
  }

  void _report(Route<dynamic>? route) {
    final path = pathFor(route?.settings);
    if (path != null) AnalyticsService.instance.screen(path);
  }

  @override
  void didPush(Route<dynamic> route, Route<dynamic>? previousRoute) => _report(route);

  @override
  void didReplace({Route<dynamic>? newRoute, Route<dynamic>? oldRoute}) => _report(newRoute);

  @override
  void didPop(Route<dynamic> route, Route<dynamic>? previousRoute) => _report(previousRoute);
}
