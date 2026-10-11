import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:openbird/providers/language_provider.dart';
import 'package:openbird/models/species.dart';
import 'package:openbird/widgets/species_list_item.dart';

class FavoritesScreen extends StatefulWidget {
  const FavoritesScreen({super.key});

  @override
  State<FavoritesScreen> createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends State<FavoritesScreen> {
  final Set<String> _favoriteIds = {};

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final languageProvider = context.watch<LanguageProvider>();
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.favorites),
      ),
      body: _favoriteIds.isEmpty
          ? _buildEmptyState(l10n, theme)
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _favoriteIds.length,
              itemBuilder: (context, index) {
                final scientificName = _favoriteIds.elementAt(index);
                return SpeciesListItem(
                  species: Species(
                    scientificName: scientificName,
                    commonNameEn: scientificName,
                    birdnetId: '',
                    ebirdCode: '',
                    gbifKey: 0,
                    avibaseId: '',
                    iucnStatus: 'LC',
                    taxonOrder: 0,
                    order: '',
                    family: '',
                    genus: '',
                    species: '',
                  ),
                  languageCode: langCode,
                  onTap: () => _navigateToSpecies(scientificName),
                  isFavorite: true,
                  onFavoriteToggle: (isFav) => _toggleFavorite(scientificName, isFav),
                );
              },
            ),
    );
  }

  Widget _buildEmptyState(AppLocalizations l10n, ThemeData theme) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.favorite_border, size: 64, color: theme.colorScheme.onSurfaceVariant.withOpacity(0.5)),
            const SizedBox(height: 16),
            Text(l10n.noFavorites, style: theme.textTheme.headlineSmall, textAlign: TextAlign.center),
            const SizedBox(height: 8),
            Text(l10n.noFavoritesSubtitle, style: theme.textTheme.bodyMedium?.copyWith(color: theme.colorScheme.onSurfaceVariant), textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }

  void _toggleFavorite(String scientificName, bool isFavorite) {
    setState(() {
      if (isFavorite) {
        _favoriteIds.add(scientificName);
      } else {
        _favoriteIds.remove(scientificName);
      }
    });
  }

  void _navigateToSpecies(String scientificName) {
    Navigator.of(context).pushNamed(
      '/species',
      arguments: {'scientificName': scientificName},
    );
  }
}