import 'package:openbird/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:openbird/providers/app_provider.dart';
import 'package:openbird/providers/language_provider.dart';
import 'package:openbird/models/species.dart';
import 'package:openbird/services/analytics_service.dart';
import 'package:openbird/widgets/species_list_item.dart';
import 'package:openbird/utils/constants.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  String _query = '';
  SearchResult? _result;
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _controller.addListener(_onSearchChanged);
    _focusNode.requestFocus();
  }

  void _onSearchChanged() {
    final query = _controller.text.trim();
    if (query == _query) return;
    _query = query;
    _debouncedSearch();
  }

  Future<void> _debouncedSearch() async {
    await Future.delayed(const Duration(milliseconds: 300));
    if (_query != _controller.text.trim()) return;
    if (_query.length < 2) {
      setState(() {
        _result = null;
        _error = null;
      });
      return;
    }
    await _search();
  }

  Future<void> _search() async {
    if (_query.length < 2) return;
    
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final appProvider = context.read<AppProvider>();
      final result = await appProvider.searchSpecies(_query);
      if (mounted && _query == _controller.text.trim()) {
        setState(() {
          _result = result;
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
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final languageProvider = context.watch<LanguageProvider>();
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.search),
        automaticallyImplyLeading: false,
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _controller,
              focusNode: _focusNode,
              decoration: InputDecoration(
                hintText: l10n.searchHint,
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _controller.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _controller.clear();
                          setState(() {
                            _query = '';
                            _result = null;
                          });
                        },
                      )
                    : null,
              ),
              textInputAction: TextInputAction.search,
              onSubmitted: (_) => _search(),
            ),
          ),
          if (_isLoading)
            const LinearProgressIndicator(minHeight: 2),
          Expanded(
            child: _buildResults(),
          ),
        ],
      ),
    );
  }

  Widget _buildResults() {
    final l10n = AppLocalizations.of(context)!;
    final languageProvider = context.watch<LanguageProvider>();
    final theme = Theme.of(context);

    if (_error != null) {
      return _buildErrorState(l10n.searchError, _error!);
    }

    if (_query.length < 2) {
      return _buildEmptyState(
        icon: Icons.search,
        title: l10n.searchPrompt,
        subtitle: l10n.searchHint,
      );
    }

    if (_result == null) {
      return _buildEmptyState(
        icon: Icons.hourglass_empty,
        title: l10n.searching,
        subtitle: '',
      );
    }

    if (_result!.species.isEmpty) {
      return _buildEmptyState(
        icon: Icons.sentiment_dissatisfied,
        title: l10n.noResults,
        subtitle: l10n.noResultsSubtitle(_query),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      itemCount: _result!.species.length,
      itemBuilder: (context, index) {
        final species = _result!.species[index];
        return SpeciesListItem(
          species: species,
          languageCode: languageProvider.locale.languageCode,
          onTap: () => _navigateToSpecies(species),
        );
      },
    );
  }

  Widget _buildEmptyState({
    required IconData icon,
    required String title,
    required String subtitle,
  }) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 64, color: theme.colorScheme.onSurfaceVariant.withOpacity(0.5)),
            const SizedBox(height: 16),
            Text(title, style: theme.textTheme.headlineSmall, textAlign: TextAlign.center),
            if (subtitle.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(subtitle, style: theme.textTheme.bodyMedium?.copyWith(color: theme.colorScheme.onSurfaceVariant), textAlign: TextAlign.center),
            ],
          ],
        ),
      ),
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
              onPressed: _search,
            ),
          ],
        ),
      ),
    );
  }

  void _navigateToSpecies(Species species) {
    AnalyticsService.instance.track('bird_click', bird: species.scientificName, source: 'search', query: _query);
    Navigator.of(context).pushNamed(
      '/species',
      arguments: {'scientificName': species.scientificName},
    );
  }
}