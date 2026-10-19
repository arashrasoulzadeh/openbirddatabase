import 'package:flutter/material.dart';
import 'package:openbird/l10n/app_localizations.dart';
import 'package:openbird/utils/iucn.dart';
import 'package:openbird/utils/web_labels.dart';

/// The same filters as the website: conservation status, habitat, diet, migration and order.
/// [options] is the API's `/filters` answer: {iucn_status: {LC: 8927, ...}, primary_habitat: {...}, ...}.
class SearchFilters extends StatelessWidget {
  final Map<String, dynamic>? options;
  final Map<String, String> selected;
  final String languageCode;
  final ValueChanged<Map<String, String>> onChanged;

  const SearchFilters({
    super.key,
    required this.options,
    required this.selected,
    required this.languageCode,
    required this.onChanged,
  });

  static const _fields = ['iucn_status', 'primary_habitat', 'primary_diet', 'migration_status', 'order'];

  @override
  Widget build(BuildContext context) {
    final opts = options;
    if (opts == null) return const SizedBox.shrink();
    final l10n = AppLocalizations.of(context)!;

    String title(String field) {
      switch (field) {
        case 'iucn_status': return l10n.iucnStatus;
        case 'primary_habitat': return l10n.primaryHabitat;
        case 'primary_diet': return l10n.primaryDiet;
        case 'migration_status': return l10n.migrationStatus;
        default: return l10n.order;
      }
    }

    String label(String field, String value) {
      if (field == 'iucn_status') return iucnLabelFor(l10n, value);
      if (field == 'order') return value;
      return valueLabelFor(languageCode, value);
    }

    return SizedBox(
      height: 44,
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        children: [
          for (final field in _fields)
            if (opts[field] is Map && (opts[field] as Map).isNotEmpty)
              Padding(
                padding: const EdgeInsetsDirectional.only(end: 8),
                child: PopupMenuButton<String>(
                  tooltip: title(field),
                  onSelected: (value) {
                    final next = Map<String, String>.from(selected);
                    if (value.isEmpty) {
                      next.remove(field);
                    } else {
                      next[field] = value;
                    }
                    onChanged(next);
                  },
                  itemBuilder: (context) {
                    final entries = (opts[field] as Map).entries.where((e) => e.key.toString().isNotEmpty).toList();
                    if (field != 'iucn_status') {
                      entries.sort((a, b) => ((b.value as num?) ?? 0).compareTo((a.value as num?) ?? 0));
                    }
                    return [
                      PopupMenuItem<String>(value: '', child: Text(l10n.filterAll)),
                      for (final e in entries)
                        PopupMenuItem<String>(
                          value: e.key.toString(),
                          child: Text('${label(field, e.key.toString())} (${e.value})'),
                        ),
                    ];
                  },
                  child: Chip(
                    avatar: selected.containsKey(field) ? const Icon(Icons.check, size: 16) : null,
                    label: Text(selected.containsKey(field) ? label(field, selected[field]!) : title(field)),
                    visualDensity: VisualDensity.compact,
                  ),
                ),
              ),
          if (selected.isNotEmpty)
            TextButton(onPressed: () => onChanged(const {}), child: Text(l10n.clearFilters)),
        ],
      ),
    );
  }
}
