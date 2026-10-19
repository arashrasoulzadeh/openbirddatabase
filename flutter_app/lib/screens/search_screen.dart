import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:openbird/l10n/app_localizations.dart';
import 'package:openbird/models/species.dart';
import 'package:openbird/providers/app_provider.dart';
import 'package:openbird/providers/language_provider.dart';
import 'package:openbird/services/analytics_service.dart';
import 'package:openbird/widgets/search_filters.dart';
import 'package:openbird/widgets/search_interpretation.dart';
import 'package:openbird/widgets/species_list_item.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  String _query = '';
  Map<String, String> _filters = {};
  Map<String, dynamic>? _filterOptions;

  SearchResult? _result; // first page: carries the total and how a sentence was understood
  List<Species> _species = [];
  bool _isLoading = false;
  bool _isLoadingMore = false;
  String? _error;
  int _requestId = 0; // an answer that arrives after a newer search was started is dropped

  @override
  void initState() {
    super.initState();
    _controller.addListener(_onSearchChanged);
    _loadFilterOptions();
    _search(); // like the website: the list of birds is there before anything is typed
  }

  Future<void> _loadFilterOptions() async {
    try {
      final options = await context.read<AppProvider>().getFilters();
      if (mounted) setState(() => _filterOptions = options);
    } catch (_) {
      // filters are optional: the search works without them
    }
  }

  void _onSearchChanged() {
    final query = _controller.text.trim();
    if (query == _query) return;
    _query = query;
    _debouncedSearch();
  }

  Future<void> _debouncedSearch() async {
    await Future.delayed(const Duration(milliseconds: 150));
    if (!mounted || _query != _controller.text.trim()) return;
    if (_query.length == 1) return; // one letter matches almost everything
    await _search();
  }

  Future<void> _search() async {
    final id = ++_requestId;
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final result = await context.read<AppProvider>().searchSpecies(_query, filters: _filters);
      if (!mounted || id != _requestId) return;
      setState(() {
        _result = result;
        _species = List<Species>.of(result.species);
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted || id != _requestId) return;
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _loadMore() async {
    if (_isLoadingMore) return;
    final id = _requestId;
    setState(() => _isLoadingMore = true);
    try {
      AnalyticsService.instance.track('load_more', value: _species.length);
      final more = await context.read<AppProvider>().searchSpecies(_query, offset: _species.length, filters: _filters);
      if (!mounted || id != _requestId) return;
      setState(() {
        _species = [..._species, ...more.species];
        _isLoadingMore = false;
      });
    } catch (e) {
      if (mounted) setState(() => _isLoadingMore = false);
    }
  }

  Future<void> _randomBird() async {
    try {
      final species = await context.read<AppProvider>().getRandomSpecies();
      if (!mounted) return;
      AnalyticsService.instance.track('random_bird', bird: species.scientificName);
      _navigateToSpecies(species, source: 'random');
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
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
    final languageCode = context.watch<LanguageProvider>().locale.languageCode;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.search),
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.casino_outlined),
            tooltip: l10n.randomBird,
            onPressed: _randomBird,
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
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
                          setState(() => _query = '');
                          _search();
                        },
                      )
                    : null,
              ),
              textInputAction: TextInputAction.search,
              onSubmitted: (_) => _search(),
            ),
          ),
          SearchFilters(
            options: _filterOptions,
            selected: _filters,
            languageCode: languageCode,
            onChanged: (next) {
              setState(() => _filters = next);
              _search();
            },
          ),
          const SizedBox(height: 4),
          if (_isLoading) const LinearProgressIndicator(minHeight: 2),
          if (_result != null) SearchInterpretation(result: _result!),
          Expanded(child: _buildResults(l10n, languageCode)),
        ],
      ),
    );
  }

  Widget _buildResults(AppLocalizations l10n, String languageCode) {
    if (_error != null) {
      return _buildErrorState(l10n.searchError, _error!);
    }
    if (_result == null) {
      return const SizedBox.shrink(); // the first answer is on its way (the progress bar shows it)
    }
    if (_species.isEmpty) {
      return _buildEmptyState(
        icon: Icons.sentiment_dissatisfied,
        title: l10n.noResults,
        subtitle: l10n.noResultsSubtitle(_query),
      );
    }

    final total = _result!.total;
    final hasMore = _species.length < total;
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      itemCount: _species.length + 1,
      itemBuilder: (context, index) {
        if (index == _species.length) {
          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 16),
            child: Column(
              children: [
                Text(l10n.showingCount(_species.length.toString(), total.toString()), style: Theme.of(context).textTheme.bodySmall),
                if (hasMore) ...[
                  const SizedBox(height: 8),
                  FilledButton(
                    onPressed: _isLoadingMore ? null : _loadMore,
                    child: _isLoadingMore
                        ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                        : Text(l10n.loadMore),
                  ),
                ],
              ],
            ),
          );
        }
        final species = _species[index];
        return SpeciesListItem(
          species: species,
          languageCode: languageCode,
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

  void _navigateToSpecies(Species species, {String source = 'search'}) {
    AnalyticsService.instance.track('bird_click', bird: species.scientificName, source: source, query: _query);
    Navigator.of(context).pushNamed(
      '/species',
      arguments: {'scientificName': species.scientificName},
    );
  }
}
