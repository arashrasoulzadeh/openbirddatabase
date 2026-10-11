import 'package:flutter_test/flutter_test.dart';
import 'package:openbird/utils/formatters.dart';

void main() {
  group('Formatters', () {
    group('formatMass', () {
      test('formats grams correctly', () {
        expect(Formatters.formatMass(10.5), '10.5 g');
        expect(Formatters.formatMass(500), '500.0 g');
      });

      test('formats kilograms for values >= 1000g', () {
        expect(Formatters.formatMass(1000), '1.00 kg');
        expect(Formatters.formatMass(1500), '1.50 kg');
        expect(Formatters.formatMass(2500.5), '2.50 kg');
      });
    });

    group('formatLength', () {
      test('formats centimeters correctly', () {
        expect(Formatters.formatLength(10.5), '10.5 cm');
        expect(Formatters.formatLength(50), '50.0 cm');
      });

      test('formats meters for values >= 100cm', () {
        expect(Formatters.formatLength(100), '1.00 m');
        expect(Formatters.formatLength(150), '1.50 m');
        expect(Formatters.formatLength(250.5), '2.50 m');
      });
    });

    group('formatLengthMm', () {
      test('formats millimeters correctly', () {
        expect(Formatters.formatLengthMm(10.5), '10.5 mm');
        expect(Formatters.formatLengthMm(50), '50.0 mm');
      });
    });

    group('formatElevationRange', () {
      test('formats range with both min and max', () {
        expect(Formatters.formatElevationRange(0, 2000), '0–2000 m');
        expect(Formatters.formatElevationRange(500, 3000), '500–3000 m');
      });

      test('formats range with only min', () {
        expect(Formatters.formatElevationRange(100, null), '≥100 m');
      });

      test('formats range with only max', () {
        expect(Formatters.formatElevationRange(null, 2000), '≤2000 m');
      });

      test('returns dash for null values', () {
        expect(Formatters.formatElevationRange(null, null), '—');
      });
    });

    group('formatRange', () {
      test('formats range with both min and max', () {
        expect(Formatters.formatRange(5, 12), '5–12');
        expect(Formatters.formatRange(1, 10), '1–10');
      });

      test('formats range with only min', () {
        expect(Formatters.formatRange(5, null), '≥5');
      });

      test('formats range with only max', () {
        expect(Formatters.formatRange(null, 12), '≤12');
      });

      test('returns dash for null values', () {
        expect(Formatters.formatRange(null, null), '—');
      });
    });

    group('formatEggSize', () {
      test('formats egg size correctly', () {
        expect(Formatters.formatEggSize(16.2, 12.8), '16.2 × 12.8 mm');
        expect(Formatters.formatEggSize(20.0, 15.0), '20.0 × 15.0 mm');
      });
    });

    group('formatDays', () {
      test('formats days correctly', () {
        expect(Formatters.formatDays(14), '14 days');
        expect(Formatters.formatDays(1), '1 days');
        expect(Formatters.formatDays(365), '365 days');
      });
    });

    group('formatYears', () {
      test('formats years with one decimal', () {
        expect(Formatters.formatYears(2.5), '2.5 years');
        expect(Formatters.formatYears(10.0), '10.0 years');
        expect(Formatters.formatYears(0.5), '0.5 years');
      });
    });

    group('formatPercent', () {
      test('formats percent with one decimal', () {
        expect(Formatters.formatPercent(0.5), '50.0%');
        expect(Formatters.formatPercent(0.75), '75.0%');
        expect(Formatters.formatPercent(1.0), '100.0%');
        expect(Formatters.formatPercent(0.0), '0.0%');
      });
    });

    group('formatDistance', () {
      test('formats kilometers for values >= 1000', () {
        expect(Formatters.formatDistance(1.5), '1.5 km');
        expect(Formatters.formatDistance(50.0), '50.0 km');
      });

      test('formats kilometers for values >= 1000 (using km)', () {
        expect(Formatters.formatDistance(1000), '1000 km');
        expect(Formatters.formatDistance(5000), '5000 km');
      });
    });

    group('formatDensity', () {
      test('formats density correctly', () {
        expect(Formatters.formatDensity(50.5), '50.5/km²');
        expect(Formatters.formatDensity(100), '100.0/km²');
      });
    });

    group('formatMonths', () {
      test('formats months correctly', () {
        expect(Formatters.formatMonths(6), '6 months');
        expect(Formatters.formatMonths(1), '1 months');
        expect(Formatters.formatMonths(12), '12 months');
      });
    });
  });
}