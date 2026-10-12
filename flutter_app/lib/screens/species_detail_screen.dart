import 'package:openbird/utils/extensions.dart';
import 'package:openbird/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:openbird/providers/app_provider.dart';
import 'package:openbird/providers/language_provider.dart';
import 'package:openbird/models/species.dart';
import 'package:openbird/widgets/section_card.dart';
import 'package:openbird/widgets/detail_row.dart';
import 'package:openbird/widgets/chip_wrap.dart';
import 'package:openbird/utils/constants.dart';
import 'package:openbird/utils/formatters.dart';

class SpeciesDetailScreen extends StatefulWidget {
  final String scientificName;

  const SpeciesDetailScreen({super.key, required this.scientificName});

  @override
  State<SpeciesDetailScreen> createState() => _SpeciesDetailScreenState();
}

class _SpeciesDetailScreenState extends State<SpeciesDetailScreen> {
  Species? _species;
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
      final species = await appProvider.getSpecies(widget.scientificName);
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

  Future<void> _refresh() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    await _loadSpecies();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final languageProvider = context.watch<LanguageProvider>();
    final theme = Theme.of(context);
    final langCode = languageProvider.locale.languageCode;

    return Scaffold(
      body: _buildBody(l10n, langCode, theme),
    );
  }

  Widget _buildBody(AppLocalizations l10n, String langCode, ThemeData theme) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return _buildErrorState(l10n, theme);
    }

    if (_species == null) {
      return _buildNotFound(l10n, theme);
    }

    final species = _species!;
    final commonName = species.getCommonName(langCode);

    return RefreshIndicator(
      onRefresh: _refresh,
      child: CustomScrollView(
        slivers: [
          _buildSliverAppBar(species, commonName, theme),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildIdentificationSection(species, l10n),
                  if (species.morphology != null) _buildMorphologySection(species, l10n),
                  if (species.distribution != null) _buildDistributionSection(species, l10n),
                  if (species.habitat != null) _buildHabitatSection(species, l10n),
                  if (species.diet != null) _buildDietSection(species, l10n),
                  if (species.behavior != null) _buildBehaviorSection(species, l10n),
                  if (species.reproduction != null) _buildReproductionSection(species, l10n),
                  if (species.demography != null) _buildDemographySection(species, l10n),
                  if (species.conservation != null) _buildConservationSection(species, l10n),
                  if (species.veterinary != null) _buildVeterinarySection(species, l10n),
                  if (species.enrichment != null) _buildEnrichmentSection(species, l10n),
                  _buildSourcesSection(species, l10n),
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSliverAppBar(Species species, String commonName, ThemeData theme) {
    return SliverAppBar(
      expandedHeight: 200,
      pinned: true,
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                theme.colorScheme.primary,
                theme.colorScheme.primary.withOpacity(0.7),
              ],
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
            ),
          ),
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  Text(
                    commonName,
                    style: theme.textTheme.headlineLarge?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.w700,
                      shadows: [
                        Shadow(
                          color: Colors.black.withOpacity(0.3),
                          offset: const Offset(0, 2),
                          blurRadius: 4,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    species.scientificName,
                    style: theme.textTheme.titleLarge?.copyWith(
                      color: Colors.white.withOpacity(0.9),
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      _buildBadge(species.iucnStatus, species.getIUCNColor(), theme),
                      _buildBadge(species.order, theme.colorScheme.secondary, theme),
                      _buildBadge(species.family, theme.colorScheme.tertiary, theme),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildBadge(String label, Color color, ThemeData theme) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        label,
        style: theme.textTheme.labelMedium?.copyWith(
          color: Colors.white,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildIdentificationSection(Species species, AppLocalizations l10n) {
    return SectionCard(
      title: l10n.identification,
      children: [
        DetailRow(label: l10n.birdnetId, value: species.birdnetId),
        DetailRow(label: l10n.ebirdCode, value: species.ebirdCode),
        DetailRow(label: l10n.gbifKey, value: species.gbifKey.toString()),
        DetailRow(label: l10n.avibaseId, value: species.avibaseId),
        DetailRow(label: l10n.order, value: species.order),
        DetailRow(label: l10n.family, value: species.family),
        DetailRow(label: l10n.genus, value: species.genus),
      ],
    );
  }

  Widget _buildMorphologySection(Species species, AppLocalizations l10n) {
    final m = species.morphology!;
    return SectionCard(
      title: l10n.morphology,
      children: [
        if (m.bodyMassG != null) DetailRow(label: l10n.bodyMass, value: Formatters.formatMass(m.bodyMassG!)),
        if (m.bodyLengthCm != null) DetailRow(label: l10n.bodyLength, value: Formatters.formatLength(m.bodyLengthCm!)),
        if (m.wingspanCm != null) DetailRow(label: l10n.wingspan, value: Formatters.formatLength(m.wingspanCm!)),
        if (m.billLengthMm != null) DetailRow(label: l10n.billLength, value: Formatters.formatLengthMm(m.billLengthMm!)),
        if (m.tarsusLengthMm != null) DetailRow(label: l10n.tarsusLength, value: Formatters.formatLengthMm(m.tarsusLengthMm!)),
        if (m.wingLengthMm != null) DetailRow(label: l10n.wingLength, value: Formatters.formatLengthMm(m.wingLengthMm!)),
        if (m.tailLengthMm != null) DetailRow(label: l10n.tailLength, value: Formatters.formatLengthMm(m.tailLengthMm!)),
      ],
    );
  }

  Widget _buildDistributionSection(Species species, AppLocalizations l10n) {
    final d = species.distribution!;
    return SectionCard(
      title: l10n.distribution,
      children: [
        if (d.breedingRange != null) DetailRow(label: l10n.breedingRange, value: d.breedingRange!),
        if (d.nonBreedingRange != null) DetailRow(label: l10n.nonBreedingRange, value: d.nonBreedingRange!),
        if (d.biogeographicRealms != null && d.biogeographicRealms!.isNotNullOrEmpty)
          DetailRow(label: l10n.biogeographicRealms, value: d.biogeographicRealms!.join(', ')),
        if (d.islandEndemic == true) DetailRow(label: l10n.islandEndemic, value: l10n.yes),
        if (d.endemicRegion != null) DetailRow(label: l10n.endemicRegion, value: d.endemicRegion!),
      ],
    );
  }

  Widget _buildHabitatSection(Species species, AppLocalizations l10n) {
    final h = species.habitat!;
    return SectionCard(
      title: l10n.habitat,
      children: [
        if (h.primary != null) DetailRow(label: l10n.primaryHabitat, value: h.primary!),
        if (h.secondary != null && h.secondary!.isNotNullOrEmpty)
          DetailRow(label: l10n.secondaryHabitats, value: h.secondary!.join(', ')),
        if (h.habitatBreadth != null) DetailRow(label: l10n.habitatBreadth, value: h.habitatBreadth.toString()),
        if (h.elevationalMinM != null || h.elevationalMaxM != null)
          DetailRow(label: l10n.elevationRange, value: Formatters.formatElevationRange(h.elevationalMinM, h.elevationalMaxM)),
        if (h.habitatTypes != null && h.habitatTypes!.isNotNullOrEmpty)
          ChipWrap(label: l10n.habitatTypes, chips: h.habitatTypes!),
        if (h.microhabitat != null) DetailRow(label: l10n.microhabitat, value: h.microhabitat!),
      ],
    );
  }

  Widget _buildDietSection(Species species, AppLocalizations l10n) {
    final d = species.diet!;
    return SectionCard(
      title: l10n.dietForaging,
      children: [
        if (d.primary != null) DetailRow(label: l10n.primaryDiet, value: d.primary!),
        if (d.dietBreadth != null) DetailRow(label: l10n.dietBreadth, value: d.dietBreadth.toString()),
        if (d.foragingStrategy != null) DetailRow(label: l10n.foragingStrategy, value: d.foragingStrategy!),
        if (d.categories != null && d.categories!.isNotEmpty)
          ...d.categories!.entries.map((e) => DetailRow(
            label: e.key,
            value: '${(e.value * 100).toStringAsFixed(0)}%',
          )),
      ],
    );
  }

  Widget _buildBehaviorSection(Species species, AppLocalizations l10n) {
    final b = species.behavior!;
    return SectionCard(
      title: l10n.behavior,
      children: [
        if (b.sociality != null) DetailRow(label: l10n.sociality, value: b.sociality!),
        if (b.flockSize != null) DetailRow(label: l10n.flockSize, value: b.flockSize!),
        if (b.territoriality != null) DetailRow(label: l10n.territoriality, value: b.territoriality!),
        if (b.migrationStatus != null) DetailRow(label: l10n.migrationStatus, value: b.migrationStatus!),
        if (b.movementType != null) DetailRow(label: l10n.movementType, value: b.movementType!),
        if (b.dispersalDistanceKm != null) DetailRow(label: l10n.dispersalDistance, value: Formatters.formatDistance(b.dispersalDistanceKm!)),
        if (b.activityPattern != null) DetailRow(label: l10n.activityPattern, value: b.activityPattern!),
      ],
    );
  }

  Widget _buildReproductionSection(Species species, AppLocalizations l10n) {
    final r = species.reproduction!;
    return SectionCard(
      title: l10n.reproduction,
      children: [
        if (r.clutchSizeMin != null || r.clutchSizeMax != null)
          DetailRow(label: l10n.clutchSize, value: Formatters.formatRange(r.clutchSizeMin, r.clutchSizeMax)),
        if (r.clutchSizeMean != null) DetailRow(label: l10n.meanClutchSize, value: r.clutchSizeMean!.toStringAsFixed(1)),
        if (r.eggLengthMm != null && r.eggWidthMm != null)
          DetailRow(label: l10n.eggSize, value: Formatters.formatEggSize(r.eggLengthMm!, r.eggWidthMm!)),
        if (r.incubationDays != null) DetailRow(label: l10n.incubationPeriod, value: Formatters.formatDays(r.incubationDays!)),
        if (r.fledgingDays != null) DetailRow(label: l10n.fledgingPeriod, value: Formatters.formatDays(r.fledgingDays!)),
        if (r.broodsPerYear != null) DetailRow(label: l10n.broodsPerYear, value: r.broodsPerYear.toString()),
        if (r.nestType != null) DetailRow(label: l10n.nestType, value: r.nestType!),
        if (r.nestPlacement != null) DetailRow(label: l10n.nestPlacement, value: r.nestPlacement!),
        if (r.nestMaterial != null && r.nestMaterial!.isNotNullOrEmpty)
          ChipWrap(label: l10n.nestMaterial, chips: r.nestMaterial!),
        if (r.matingSystem != null) DetailRow(label: l10n.matingSystem, value: r.matingSystem!),
        if (r.parentalCare != null) DetailRow(label: l10n.parentalCare, value: r.parentalCare!),
      ],
    );
  }

  Widget _buildDemographySection(Species species, AppLocalizations l10n) {
    final d = species.demography!;
    return SectionCard(
      title: l10n.demography,
      children: [
        if (d.generationLengthYears != null) DetailRow(label: l10n.generationLength, value: Formatters.formatYears(d.generationLengthYears!)),
        if (d.maxLongevityYears != null) DetailRow(label: l10n.maxLongevity, value: Formatters.formatYears(d.maxLongevityYears!.toDouble())),
        if (d.annualSurvivalAdult != null) DetailRow(label: l10n.adultSurvival, value: Formatters.formatPercent(d.annualSurvivalAdult!)),
        if (d.annualSurvivalJuvenile != null) DetailRow(label: l10n.juvenileSurvival, value: Formatters.formatPercent(d.annualSurvivalJuvenile!)),
        if (d.populationTrend != null) DetailRow(label: l10n.populationTrend, value: d.populationTrend!),
        if (d.populationSize != null) DetailRow(label: l10n.populationSize, value: d.populationSize!),
        if (d.densityIndividualsPerKm2 != null) DetailRow(label: l10n.density, value: Formatters.formatDensity(d.densityIndividualsPerKm2!)),
      ],
    );
  }

  Widget _buildConservationSection(Species species, AppLocalizations l10n) {
    final c = species.conservation!;
    return SectionCard(
      title: l10n.conservation,
      children: [
        if (c.iucnStatus != null) DetailRow(label: l10n.iucnStatus, value: c.iucnStatus!),
        if (c.populationTrend != null) DetailRow(label: l10n.populationTrend, value: c.populationTrend!),
        if (c.threats != null && c.threats!.isNotNullOrEmpty)
          ChipWrap(label: l10n.threats, chips: c.threats!),
        if (c.conservationActions != null && c.conservationActions!.isNotNullOrEmpty)
          ChipWrap(label: l10n.conservationActions, chips: c.conservationActions!),
      ],
    );
  }

  Widget _buildVeterinarySection(Species species, AppLocalizations l10n) {
    final v = species.veterinary!;
    return SectionCard(
      title: l10n.veterinaryCare,
      children: [
        if (v.commonDiseases != null && v.commonDiseases!.isNotNullOrEmpty)
          ChipWrap(label: l10n.commonDiseases, chips: v.commonDiseases!),
        if (v.vaccinationSchedule != null && v.vaccinationSchedule!.isNotNullOrEmpty)
          ChipWrap(label: l10n.vaccinationSchedule, chips: v.vaccinationSchedule!),
        if (v.dewormingFrequencyMonths != null) DetailRow(label: l10n.dewormingFrequency, value: Formatters.formatMonths(v.dewormingFrequencyMonths!)),
        if (v.healthCheckFrequencyMonths != null) DetailRow(label: l10n.healthCheckFrequency, value: Formatters.formatMonths(v.healthCheckFrequencyMonths!)),
        if (v.zoonoticRisks != null && v.zoonoticRisks!.isNotNullOrEmpty)
          ChipWrap(label: l10n.zoonoticRisks, chips: v.zoonoticRisks!),
        if (v.emergencySigns != null && v.emergencySigns!.isNotNullOrEmpty)
          ChipWrap(label: l10n.emergencySigns, chips: v.emergencySigns!),
        if (v.vetSpecialistType != null) DetailRow(label: l10n.specialistType, value: v.vetSpecialistType!),
        if (v.source != null) DetailRow(label: l10n.source, value: v.source!),
        if (v.contributor != null) DetailRow(label: l10n.contributor, value: v.contributor!),
        if (v.verified == true)
          Row(
            children: [
              Icon(Icons.verified, size: 16, color: Colors.green),
              const SizedBox(width: 4),
              Text(l10n.verified, style: TextStyle(color: Colors.green, fontWeight: FontWeight.w500)),
            ],
          ),
      ],
    );
  }

  Widget _buildEnrichmentSection(Species species, AppLocalizations l10n) {
    final e = species.enrichment!;
    return SectionCard(
      title: l10n.enrichmentTraining,
      children: [
        if (e.foragingToys != null && e.foragingToys!.isNotNullOrEmpty)
          ChipWrap(label: l10n.foragingToys, chips: e.foragingToys!),
        if (e.socialEnrichment != null) DetailRow(label: l10n.socialEnrichment, value: e.socialEnrichment!),
        if (e.cognitiveToys != null && e.cognitiveToys!.isNotNullOrEmpty)
          ChipWrap(label: l10n.cognitiveToys, chips: e.cognitiveToys!),
        if (e.bathing != null) DetailRow(label: l10n.bathing, value: e.bathing!),
        if (e.training != null) ...[
          if (e.training!.targetTraining == true) DetailRow(label: l10n.targetTraining, value: l10n.yes),
          if (e.training!.recallTraining == true) DetailRow(label: l10n.recallTraining, value: l10n.yes),
          if (e.training!.harnessTraining != null) DetailRow(label: l10n.harnessTraining, value: e.training!.harnessTraining!),
        ],
        if (e.playBehaviors != null && e.playBehaviors!.isNotNullOrEmpty)
          ChipWrap(label: l10n.playBehaviors, chips: e.playBehaviors!),
        if (e.environmentalEnrichment != null && e.environmentalEnrichment!.isNotNullOrEmpty)
          ChipWrap(label: l10n.environmentalEnrichment, chips: e.environmentalEnrichment!),
        if (e.source != null) DetailRow(label: l10n.source, value: e.source!),
        if (e.contributor != null) DetailRow(label: l10n.contributor, value: e.contributor!),
        if (e.verified == true)
          Row(
            children: [
              Icon(Icons.verified, size: 16, color: Colors.green),
              const SizedBox(width: 4),
              Text(l10n.verified, style: TextStyle(color: Colors.green, fontWeight: FontWeight.w500)),
            ],
          ),
      ],
    );
  }

  Widget _buildSourcesSection(Species species, AppLocalizations l10n) {
    return SectionCard(
      title: l10n.sourcesQuality,
      children: [
        if (species.sources != null && species.sources!.isNotNullOrEmpty)
          DetailRow(label: l10n.sources, value: species.sources!.join(', ')),
        if (species.dataQuality != null) DetailRow(label: l10n.dataQuality, value: species.dataQuality!),
        if (species.lastUpdated != null) DetailRow(label: l10n.lastUpdated, value: species.lastUpdated!),
      ],
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
              onPressed: _refresh,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNotFound(AppLocalizations l10n, ThemeData theme) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search_off, size: 64, color: theme.colorScheme.onSurfaceVariant.withOpacity(0.5)),
            const SizedBox(height: 16),
            Text(l10n.speciesNotFound, style: theme.textTheme.headlineSmall, textAlign: TextAlign.center),
            const SizedBox(height: 8),
            Text(widget.scientificName, style: theme.textTheme.bodyMedium?.copyWith(fontStyle: FontStyle.italic), textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }
}