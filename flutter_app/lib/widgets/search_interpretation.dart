import 'package:flutter/material.dart';
import 'package:openbird/l10n/app_localizations.dart';
import 'package:openbird/models/species.dart';
import 'package:openbird/utils/iucn.dart';

/// One line under the search box when the search was a sentence ("endangered owls in forests") or a typo was fixed.
class SearchInterpretation extends StatelessWidget {
  final SearchResult result;

  const SearchInterpretation({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final corrected = result.correctedQuery;

    if (corrected != null && corrected.isNotEmpty) {
      return Padding(
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
        child: Text.rich(
          TextSpan(
            text: '${l10n.showingResultsFor} ',
            style: theme.textTheme.bodyMedium,
            children: [
              TextSpan(text: corrected, style: const TextStyle(fontWeight: FontWeight.w700)),
            ],
          ),
        ),
      );
    }
    if (!result.isSentence) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
      child: Wrap(
        spacing: 8,
        runSpacing: 4,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          Text('${l10n.understoodAs}:', style: theme.textTheme.bodyMedium),
          for (final entry in result.interpretedFilters.entries)
            Chip(
              visualDensity: VisualDensity.compact,
              label: Text(entry.value
                  .map((v) => entry.key == 'iucn_status' ? iucnLabelFor(l10n, v) : v)
                  .join(' · ')),
            ),
          for (final word in result.interpretedWords)
            Chip(visualDensity: VisualDensity.compact, label: Text(word)),
          if (result.ignoredWords.isNotEmpty)
            Text(
              '(${l10n.ignoredWords}: ${result.ignoredWords.join(', ')})',
              style: theme.textTheme.bodySmall?.copyWith(color: theme.hintColor),
            ),
        ],
      ),
    );
  }
}
