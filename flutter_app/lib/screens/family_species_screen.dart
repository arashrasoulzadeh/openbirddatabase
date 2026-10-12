import 'package:openbird/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:openbird/providers/app_provider.dart';
import 'package:openbird/providers/language_provider.dart';
import 'package:openbird/models/species.dart';
import 'package:openbird/widgets/species_list_item.dart';

class FamilySpeciesScreen extends StatefulWidget {
  final String familyName;

  const FamilySpeciesScreen({super.key, required this.familyName});

  @override
  State<FamilySpeciesScreen> createState() => _FamilySpeciesScreenState();
}

class _FamilySpeciesScreenState extends State<FamilySpeciesScreen> {
  List<Species>? _species;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadSpecies();
  }

  Future<void> _loadSpecies() async {
    try {
      final appProvider = context.read<AppProvider>();
      final species = await appProvider.getSpeciesByFamily(widget.familyName);
      if (mounted) {
        setState(() {
          _species = species;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final languageProvider = context.watch<LanguageProvider>();
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.familyName),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: _buildBody(l10n, languageProvider.locale.languageCode, theme),
    );
  }

  Widget _buildBody(AppLocalizations l10n, String langCode, ThemeData theme) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return _buildErrorState(l10n, theme);
    }

    if (_species == null || _species!.isEmpty) {
      return _buildEmptyState(l10n, theme);
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _species!.length,
      itemBuilder: (context, index) {
        final species = _species![index];
        return SpeciesListItem(
          species: species,
          languageCode: langCode,
          onTap: () => _navigateToSpecies(species),
        );
      },
    );
  }

  Widget _buildErrorState(AppLocalizations l10n, ThemeData theme) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: theme.colorScheme.error),
            const SizedBox(height: 16),
            Text(l10n.loadError, style: theme.textTheme.headlineSmall, textAlign: TextAlign.center),
            const SizedBox(height: 8),
            Text(_error!, style: theme.textTheme.bodyMedium?.copyWith(color: theme.colorScheme.onSurfaceVariant), textAlign: TextAlign.center),
            const SizedBox(height: 16),
            FilledButton.icon(
              icon: const Icon(Icons.refresh),
              label: Text(l10n.retry),
              onPressed: _loadSpecies,
            ),
          ],
        ),
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
            Icon(Icons.folder_off, size: 64, color: theme.colorScheme.onSurfaceVariant.withOpacity(0.5)),
            const SizedBox(height: 16),
            Text(l10n.noSpeciesInFamily, style: theme.textTheme.headlineSmall, textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }

  void _navigateToSpecies(Species species) {
    Navigator.of(context).pushNamed(
      '/species',
      arguments: {'scientificName': species.scientificName},
    );
  }
}