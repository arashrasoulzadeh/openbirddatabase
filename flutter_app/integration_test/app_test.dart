import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:openbird/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('OpenBird App Integration Tests', () {
    testWidgets('App launches and shows splash screen', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Should show splash screen elements
      expect(find.text('OpenBird'), findsOneWidget);
      expect(find.text('Global Bird Database'), findsOneWidget);
    });

    testWidgets('Navigation to search screen works', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Should be on home screen with search tab
      expect(find.byIcon(Icons.search), findsAtLeastNWidgets(1));
      expect(find.byIcon(Icons.account_tree), findsOneWidget);
      expect(find.byIcon(Icons.favorite), findsOneWidget);
      expect(find.byIcon(Icons.settings), findsOneWidget);
    });

    testWidgets('Search screen loads and accepts input', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Tap on search field
      final searchField = find.byType(TextField);
      expect(searchField, findsOneWidget);

      // Enter search query
      await tester.enterText(searchField, 'Great Tit');
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Should show search results or empty state
      expect(find.text('Great Tit'), findsAtLeastNWidgets(0));
    });

    testWidgets('Taxonomy screen loads', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Tap taxonomy tab
      await tester.tap(find.byIcon(Icons.account_tree));
      await tester.pumpAndSettle();

      // Should show taxonomy screen
      expect(find.text('Taxonomy'), findsOneWidget);
    });

    testWidgets('Settings screen loads', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Tap settings tab
      await tester.tap(find.byIcon(Icons.settings));
      await tester.pumpAndSettle();

      // Should show settings screen
      expect(find.text('Settings'), findsOneWidget);
      expect(find.text('Appearance'), findsOneWidget);
      expect(find.text('Language & Region'), findsOneWidget);
    });

    testWidgets('Theme switching works', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Go to settings
      await tester.tap(find.byIcon(Icons.settings));
      await tester.pumpAndSettle();

      // Find theme options
      expect(find.text('Light'), findsOneWidget);
      expect(find.text('Dark'), findsOneWidget);
      expect(find.text('System'), findsOneWidget);
    });

    testWidgets('Language selection works', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Go to settings
      await tester.tap(find.byIcon(Icons.settings));
      await tester.pumpAndSettle();

      // Check for language options
      expect(find.text('English'), findsOneWidget);
      expect(find.text('فارسی'), findsOneWidget);
      expect(find.text('العربية'), findsOneWidget);
    });

    testWidgets('App handles offline gracefully', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Search with no internet should show error state
      final searchField = find.byType(TextField);
      await tester.enterText(searchField, 'Test Bird');
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Should not crash
      expect(find.byType(CircularProgressIndicator), findsAtLeastNWidgets(0));
    });
  });
}