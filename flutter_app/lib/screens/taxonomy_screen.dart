import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:openbird/providers/app_provider.dart';
import 'package:openbird/providers/language_provider.dart';
import 'package:openbird/models/species.dart';
import 'package:openbird/widgets/taxonomy_expansion_tile.dart';

class TaxonomyScreen extends StatefulWidget {
  const TaxonomyScreen({super.key});

  @override
  State<TaxonomyScreen> createState() => _TaxonomyScreenState();
}

class _TaxonomyScreenState extends State<TaxonomyScreen> {
  List<TaxonomyNode>? _taxonomy;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadTaxonomy();
  }

  Future<void> _loadTaxonomy() async {
    try {
      final appProvider = context.read<AppProvider>();
      final taxonomy = await appProvider.getTaxonomy();
      if (mounted) {
        setState(() {
          _taxonomy = taxonomy;
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
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.taxonomy),
        actions: [
          if (!_isLoading && _taxonomy != null)
            IconButton(
              icon: const Icon(Icons.expand_more),
              onPressed: _expandAll,
              tooltip: l10n.expandAll,
            ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return _buildErrorState(l10n.loadError, _error!);
    }

    if (_taxonomy == null || _taxonomy!.isEmpty) {
      return _buildEmptyState();
    }

    return ListView.builder(
      padding: const EdgeInsets.all(8),
      itemCount: _taxonomy!.length,
      itemBuilder: (context, index) {
        final order = _taxonomy![index];
        return TaxonomyExpansionTile(
          node: order,
          level: 0,
          onFamilyTap: _navigateToFamily,
        );
      },
    );
  }

  void _expandAll() {
    // This would need a more complex implementation with keys
    // For now, just show a snackbar
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(AppLocalizations.of(context)!.expandAllNotImplemented)),
    );
  }

  Widget _buildErrorState(String title, String message) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: theme.colorScheme.error),
            const SizedBox(height: 16),
            Text(title, style: theme.textTheme.headlineSmall, textAlign: TextAlign.center),
            const SizedBox(height: 8),
            Text(message, style: theme.textTheme.bodyMedium?.copyWith(color: theme.colorScheme.onSurfaceVariant), textAlign: TextAlign.center),
            const SizedBox(height: 16),
            FilledButton.icon(
              icon: const Icon(Icons.refresh),
              label: Text(AppLocalizations.of(context)!.retry),
              onPressed: () {
                setState(() {
                  _isLoading = true;
                  _error = null;
                });
                _loadTaxonomy();
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.account_tree, size: 64, color: theme.colorScheme.onSurfaceVariant.withOpacity(0.5)),
            const SizedBox(height: 16),
            Text(AppLocalizations.of(context)!.noTaxonomyData, style: theme.textTheme.headlineSmall, textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }

  void _navigateToFamily(String familyName) {
    Navigator.of(context).pushNamed(
      '/family',
      arguments: {'familyName': familyName},
    );
  }
}