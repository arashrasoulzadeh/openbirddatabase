import 'package:flutter/material.dart';

class ChipWrap extends StatelessWidget {
  final String label;
  final List<String> chips;

  const ChipWrap({
    super.key,
    required this.label,
    required this.chips,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 6),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: chips.map((chip) => Chip(
              label: Text(chip, style: theme.textTheme.labelMedium),
              visualDensity: VisualDensity.compact,
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            )).toList(),
          ),
        ],
      ),
    );
  }
}