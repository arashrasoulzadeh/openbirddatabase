import 'package:flutter/material.dart';
import 'package:openbird/l10n/app_localizations.dart';
import 'package:openbird/models/species.dart';
import 'package:openbird/utils/web_labels.dart';

/// "34 of 57 fields have data" with a progress bar, and what is still missing (the same card the website shows).
class CompletenessCard extends StatelessWidget {
  final Completeness completeness;
  final String languageCode;

  const CompletenessCard({super.key, required this.completeness, required this.languageCode});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final percent = (completeness.score * 100).round();

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    l10n.dataCompleteness,
                    style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700, color: theme.colorScheme.primary),
                  ),
                ),
                Text('$percent%', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
              ],
            ),
            const SizedBox(height: 8),
            ClipRRect(
              borderRadius: BorderRadius.circular(6),
              child: LinearProgressIndicator(value: completeness.score.clamp(0.0, 1.0), minHeight: 8),
            ),
            const SizedBox(height: 6),
            Text(
              l10n.fieldsFilled(completeness.filled.toString(), completeness.total.toString()),
              style: theme.textTheme.bodySmall,
            ),
            if (completeness.missing.isNotEmpty)
              Theme(
                data: theme.copyWith(dividerColor: Colors.transparent),
                child: ExpansionTile(
                  tilePadding: EdgeInsets.zero,
                  childrenPadding: EdgeInsets.zero,
                  title: Text(l10n.missingInformation, style: theme.textTheme.titleSmall),
                  children: [
                    Align(
                      alignment: AlignmentDirectional.centerStart,
                      child: Text(l10n.missingInformationHint, style: theme.textTheme.bodySmall),
                    ),
                    const SizedBox(height: 8),
                    Align(
                      alignment: AlignmentDirectional.centerStart,
                      child: Wrap(
                        spacing: 6,
                        runSpacing: 6,
                        children: [
                          for (final fields in completeness.missing.values)
                            for (final field in fields)
                              Chip(
                                visualDensity: VisualDensity.compact,
                                label: Text(fieldLabelFor(languageCode, field.split('.').last), style: theme.textTheme.labelSmall),
                              ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 8),
                    Align(
                      alignment: AlignmentDirectional.centerStart,
                      child: Text(l10n.expertCuratedNote, style: theme.textTheme.bodySmall?.copyWith(color: theme.hintColor)),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
