import 'package:flutter/material.dart';
import 'package:openbird/models/species.dart';

class SpeciesListItem extends StatelessWidget {
  final Species species;
  final String languageCode;
  final VoidCallback onTap;
  final bool isFavorite;
  final ValueChanged<bool>? onFavoriteToggle;

  const SpeciesListItem({
    super.key,
    required this.species,
    required this.languageCode,
    required this.onTap,
    this.isFavorite = false,
    this.onFavoriteToggle,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final commonName = species.getCommonName(languageCode);

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      commonName,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      species.scientificName,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontStyle: FontStyle.italic,
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 6,
                      runSpacing: 4,
                      children: [
                        _buildChip(species.order, theme.colorScheme.primaryContainer, theme.colorScheme.onPrimaryContainer),
                        _buildChip(species.family, theme.colorScheme.secondaryContainer, theme.colorScheme.onSecondaryContainer),
                        _buildIUCNChip(species.iucnStatus),
                      ],
                    ),
                  ],
                ),
              ),
              if (onFavoriteToggle != null) ...[
                const SizedBox(width: 8),
                IconButton(
                  icon: Icon(
                    isFavorite ? Icons.favorite : Icons.favorite_border,
                    color: isFavorite ? Colors.red : theme.colorScheme.onSurfaceVariant,
                  ),
                  onPressed: () => onFavoriteToggle!(!isFavorite),
                  tooltip: isFavorite ? 'Remove from favorites' : 'Add to favorites',
                ),
              ] else ...[
                const SizedBox(width: 8),
                Icon(
                  Icons.chevron_right,
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildChip(String label, Color backgroundColor, Color textColor) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w500,
          color: textColor,
        ),
      ),
    );
  }

  Widget _buildIUCNChip(String status) {
    Color color;
    switch (status) {
      case 'LC': color = Colors.green; break;
      case 'NT': color = Colors.amber; break;
      case 'VU': color = Colors.orange; break;
      case 'EN': color = Colors.red; break;
      case 'CR': color = Colors.red[900]!; break;
      case 'EW': color = Colors.grey; break;
      case 'EX': color = Colors.grey[900]!; break;
      case 'DD': color = Colors.blue; break;
      default: color = Colors.grey;
    }
    return _buildChip(status, color.withOpacity(0.15), color);
  }
}