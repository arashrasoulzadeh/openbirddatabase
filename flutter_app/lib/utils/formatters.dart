class Formatters {
  static String formatMass(double grams) {
    if (grams >= 1000) {
      return '${(grams / 1000).toStringAsFixed(2)} kg';
    }
    return '${grams.toStringAsFixed(1)} g';
  }

  static String formatLength(double cm) {
    if (cm >= 100) {
      return '${(cm / 100).toStringAsFixed(2)} m';
    }
    return '${cm.toStringAsFixed(1)} cm';
  }

  static String formatLengthMm(double mm) {
    return '${mm.toStringAsFixed(1)} mm';
  }

  static String formatElevationRange(int? min, int? max) {
    if (min != null && max != null) {
      return '$min–$max m';
    } else if (min != null) {
      return '≥$min m';
    } else if (max != null) {
      return '≤$max m';
    }
    return '—';
  }

  static String formatRange(int? min, int? max) {
    if (min != null && max != null) {
      return '$min–$max';
    } else if (min != null) {
      return '≥$min';
    } else if (max != null) {
      return '≤$max';
    }
    return '—';
  }

  static String formatEggSize(double length, double width) {
    return '$length × $width mm';
  }

  static String formatDays(int days) {
    return '$days days';
  }

  static String formatYears(double years) {
    return '${years.toStringAsFixed(1)} years';
  }

  static String formatPercent(double value) {
    return '${(value * 100).toStringAsFixed(1)}%';
  }

  static String formatDistance(double km) {
    return '${km.toStringAsFixed(km >= 1000 ? 0 : 1)} km';
  }

  static String formatDensity(double density) {
    return '${density.toStringAsFixed(1)}/km²';
  }

  static String formatMonths(int months) {
    return '$months months';
  }
}