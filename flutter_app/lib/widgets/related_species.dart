import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:openbird/l10n/app_localizations.dart';
import 'package:openbird/models/species.dart';
import 'package:openbird/providers/app_provider.dart';

/// Other species of the same family (same genus first), loaded after the page; it simply stays empty if that fails.
class RelatedSpecies extends StatefulWidget {
  final Species species;
  final String languageCode;

  const RelatedSpecies({super.key, required this.species, required this.languageCode});

  @override
  State<RelatedSpecies> createState() => _RelatedSpeciesState();
}

class _RelatedSpeciesState extends State<RelatedSpecies> {
  Future<List<Species>>? _future; // started once, not on every rebuild

  @override
  void initState() {
    super.initState();
    if (widget.species.family.isNotEmpty) _future = _load();
  }

  Future<List<Species>> _load() async {
    final species = widget.species;
    final all = await context.read<AppProvider>().getSpeciesByFamily(species.family);
    final others = all.where((s) => s.scientificName != species.scientificName).toList();
    others.sort((a, b) {
      final sameA = a.genus == species.genus ? 0 : 1;
      final sameB = b.genus == species.genus ? 0 : 1;
      return sameA != sameB ? sameA.compareTo(sameB) : a.scientificName.compareTo(b.scientificName);
    });
    return others.take(12).toList();
  }

  @override
  Widget build(BuildContext context) {
    if (_future == null) return const SizedBox.shrink();
    final languageCode = widget.languageCode;
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return FutureBuilder<List<Species>>(
      future: _future,
      builder: (context, snapshot) {
        final related = snapshot.data;
        if (related == null || related.isEmpty) return const SizedBox.shrink();
        return Card(
          margin: const EdgeInsets.only(bottom: 16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l10n.relatedSpecies,
                  style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700, color: theme.colorScheme.primary),
                ),
                const SizedBox(height: 8),
                for (final s in related)
                  ListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    title: Text(s.getCommonName(languageCode), maxLines: 1, overflow: TextOverflow.ellipsis),
                    subtitle: Text(s.scientificName, style: const TextStyle(fontStyle: FontStyle.italic)),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => Navigator.of(context).pushNamed('/species', arguments: {'scientificName': s.scientificName}),
                  ),
              ],
            ),
          ),
        );
      },
    );
  }
}
