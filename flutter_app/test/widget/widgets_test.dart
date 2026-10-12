import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:openbird/widgets/detail_row.dart';
import 'package:openbird/widgets/section_card.dart';
import 'package:openbird/widgets/chip_wrap.dart';

void main() {
  group('DetailRow Widget', () {
    testWidgets('renders label and value correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: DetailRow(label: 'Test Label', value: 'Test Value'),
          ),
        ),
      );

      expect(find.text('Test Label'), findsOneWidget);
      expect(find.text('Test Value'), findsOneWidget);
    });

    testWidgets('applies correct styles', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.light(),
          home: const Scaffold(
            body: DetailRow(label: 'Label', value: 'Value'),
          ),
        ),
      );

      final labelText = tester.widget<Text>(find.text('Label').first);
      final valueText = tester.widget<Text>(find.text('Value').first);

      expect(labelText.style?.color, ThemeData.light().colorScheme.onSurfaceVariant);
      expect(valueText.style?.fontWeight, FontWeight.w500);
    });
  });

  group('SectionCard Widget', () {
    testWidgets('renders title and children', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SectionCard(
              title: 'Test Section',
              children: [
                const Text('Child 1'),
                const Text('Child 2'),
              ],
            ),
          ),
        ),
      );

      expect(find.text('Test Section'), findsOneWidget);
      expect(find.text('Child 1'), findsOneWidget);
      expect(find.text('Child 2'), findsOneWidget);
    });

    testWidgets('does not render when children empty', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SectionCard(
              title: 'Empty Section',
              children: [],
            ),
          ),
        ),
      );

      expect(find.text('Empty Section'), findsNothing);
    });

    testWidgets('applies primary color to title', (WidgetTester tester) async {
      final theme = ThemeData(primarySwatch: Colors.blue);
      await tester.pumpWidget(
        MaterialApp(
          theme: theme,
          home: const Scaffold(
            body: SectionCard(
              title: 'Test',
              children: [Text('Child')],
            ),
          ),
        ),
      );

      final titleText = tester.widget<Text>(find.text('Test').first);
      expect(titleText.style?.color, theme.colorScheme.primary);
      expect(titleText.style?.fontWeight, FontWeight.w700);
    });
  });

  group('ChipWrap Widget', () {
    testWidgets('renders label and chips', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ChipWrap(
              label: 'Test Label',
              chips: ['Chip 1', 'Chip 2', 'Chip 3'],
            ),
          ),
        ),
      );

      expect(find.text('Test Label'), findsOneWidget);
      expect(find.text('Chip 1'), findsOneWidget);
      expect(find.text('Chip 2'), findsOneWidget);
      expect(find.text('Chip 3'), findsOneWidget);
    });

    testWidgets('wraps chips correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ChipWrap(
              label: 'Label',
              chips: List.generate(10, (i) => 'Chip $i'),
            ),
          ),
        ),
      );

      // All chips should be present
      for (int i = 0; i < 10; i++) {
        expect(find.text('Chip $i'), findsOneWidget);
      }
    });

    testWidgets('handles empty chips list', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ChipWrap(
              label: 'Label',
              chips: [],
            ),
          ),
        ),
      );

      expect(find.text('Label'), findsOneWidget);
      // No chips should be rendered
      expect(find.byType(Chip), findsNothing);
    });
  });
}