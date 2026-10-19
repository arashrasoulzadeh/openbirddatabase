import 'package:flutter/material.dart';

class Species {
  final String scientificName;
  final String commonNameEn;
  final String? commonNameFa;
  final String? commonNameAr;
  final String? commonNameEs;
  final String? commonNameFr;
  final String? commonNameDe;
  final String? commonNamePt;
  final String? commonNameRu;
  final String? commonNameJa;
  final String? commonNameZh;
  final String? commonNameNl;
  final String? commonNamePl;
  final String? commonNameTr;
  final String birdnetId;
  final String ebirdCode;
  final int gbifKey;
  final String avibaseId;
  final String iucnStatus;
  final int taxonOrder;
  final String order;
  final String family;
  final String genus;
  final String species;
  
  final Morphology? morphology;
  final Distribution? distribution;
  final Habitat? habitat;
  final Diet? diet;
  final Behavior? behavior;
  final Reproduction? reproduction;
  final Demography? demography;
  final Conservation? conservation;
  final Veterinary? veterinary;
  final Enrichment? enrichment;
  final List<String>? sources;
  final String? dataQuality;
  final String? lastUpdated;

  /// Photos of the species (CC0 / CC BY, with author and source), the first one is the main photo.
  final List<SpeciesPhoto> photos;

  /// How many of the 57 core fields have data, and which are still empty (from the API's `completeness` report).
  final Completeness? completeness;

  Species({
    required this.scientificName,
    required this.commonNameEn,
    this.commonNameFa,
    this.commonNameAr,
    this.commonNameEs,
    this.commonNameFr,
    this.commonNameDe,
    this.commonNamePt,
    this.commonNameRu,
    this.commonNameJa,
    this.commonNameZh,
    this.commonNameNl,
    this.commonNamePl,
    this.commonNameTr,
    required this.birdnetId,
    required this.ebirdCode,
    required this.gbifKey,
    required this.avibaseId,
    required this.iucnStatus,
    required this.taxonOrder,
    required this.order,
    required this.family,
    required this.genus,
    required this.species,
    this.morphology,
    this.distribution,
    this.habitat,
    this.diet,
    this.behavior,
    this.reproduction,
    this.demography,
    this.conservation,
    this.veterinary,
    this.enrichment,
    this.sources,
    this.dataQuality,
    this.lastUpdated,
    this.photos = const [],
    this.completeness,
  });

  factory Species.fromJson(Map<String, dynamic> json) {
    return Species(
      scientificName: _asString(json['scientific_name']) ?? '',
      commonNameEn: _asString(json['common_name_en']) ?? '',
      commonNameFa: _asString(json['common_name_fa']),
      commonNameAr: _asString(json['common_name_ar']),
      commonNameEs: _asString(json['common_name_es']),
      commonNameFr: _asString(json['common_name_fr']),
      commonNameDe: _asString(json['common_name_de']),
      commonNamePt: _asString(json['common_name_pt']),
      commonNameRu: _asString(json['common_name_ru']),
      commonNameJa: _asString(json['common_name_ja']),
      commonNameZh: _asString(json['common_name_zh']),
      commonNameNl: _asString(json['common_name_nl']),
      commonNamePl: _asString(json['common_name_pl']),
      commonNameTr: _asString(json['common_name_tr']),
      birdnetId: _asString(json['birdnet_id']) ?? '',
      ebirdCode: _asString(json['ebird_code']) ?? '',
      gbifKey: _asInt(json['gbif_key']) ?? 0,
      avibaseId: _asString(json['avibase_id']) ?? '',
      iucnStatus: _asString(json['iucn_status']) ?? 'LC',
      taxonOrder: _asInt(json['taxon_order']) ?? 0,
      order: _asString(json['order']) ?? '',
      family: _asString(json['family']) ?? '',
      genus: _asString(json['genus']) ?? '',
      species: _asString(json['species']) ?? '',
      morphology: json['morphology'] != null ? Morphology.fromJson(json['morphology']) : null,
      distribution: json['distribution'] != null ? Distribution.fromJson(json['distribution']) : null,
      habitat: json['habitat'] != null ? Habitat.fromJson(json['habitat']) : null,
      diet: json['diet'] != null ? Diet.fromJson(json['diet']) : null,
      behavior: json['behavior'] != null ? Behavior.fromJson(json['behavior']) : null,
      reproduction: json['reproduction'] != null ? Reproduction.fromJson(json['reproduction']) : null,
      demography: json['demography'] != null ? Demography.fromJson(json['demography']) : null,
      conservation: json['conservation'] != null ? Conservation.fromJson(json['conservation']) : null,
      veterinary: json['veterinary'] != null ? Veterinary.fromJson(json['veterinary']) : null,
      enrichment: json['enrichment'] != null ? Enrichment.fromJson(json['enrichment']) : null,
      sources: _asStringList(json['sources']),
      dataQuality: _asString(json['data_quality']),
      lastUpdated: _asString(json['last_updated']),
      photos: SpeciesPhoto.listFrom(json['images'] ?? json['image']),
      completeness: Completeness.from(json['completeness']),
    );
  }

  String getCommonName(String languageCode) {
    switch (languageCode) {
      case 'fa': return commonNameFa ?? commonNameEn;
      case 'ar': return commonNameAr ?? commonNameEn;
      case 'es': return commonNameEs ?? commonNameEn;
      case 'fr': return commonNameFr ?? commonNameEn;
      case 'de': return commonNameDe ?? commonNameEn;
      case 'pt': return commonNamePt ?? commonNameEn;
      case 'ru': return commonNameRu ?? commonNameEn;
      case 'ja': return commonNameJa ?? commonNameEn;
      case 'zh': return commonNameZh ?? commonNameEn;
      case 'nl': return commonNameNl ?? commonNameEn;
      case 'pl': return commonNamePl ?? commonNameEn;
      case 'tr': return commonNameTr ?? commonNameEn;
      default: return commonNameEn;
    }
  }

  Color getIUCNColor() {
    switch (iucnStatus) {
      case 'LC': return Colors.green;
      case 'NT': return Colors.amber;
      case 'VU': return Colors.orange;
      case 'EN': return Colors.red;
      case 'CR': return Colors.red[900]!;
      case 'EW': return Colors.grey;
      case 'EX': return Colors.grey[900]!;
      case 'DD': return Colors.blue;
      default: return Colors.grey;
    }
  }
}

class Morphology {
  final double? bodyMassG;
  final double? bodyLengthCm;
  final double? wingspanCm;
  final double? billLengthMm;
  final double? tarsusLengthMm;
  final double? wingLengthMm;
  final double? tailLengthMm;

  Morphology({
    this.bodyMassG,
    this.bodyLengthCm,
    this.wingspanCm,
    this.billLengthMm,
    this.tarsusLengthMm,
    this.wingLengthMm,
    this.tailLengthMm,
  });

  factory Morphology.fromJson(Map<String, dynamic> json) {
    return Morphology(
      bodyMassG: (json['body_mass_g'] as num?)?.toDouble(),
      bodyLengthCm: (json['body_length_cm'] as num?)?.toDouble(),
      wingspanCm: (json['wingspan_cm'] as num?)?.toDouble(),
      billLengthMm: (json['bill_length_mm'] as num?)?.toDouble(),
      tarsusLengthMm: (json['tarsus_length_mm'] as num?)?.toDouble(),
      wingLengthMm: (json['wing_length_mm'] as num?)?.toDouble(),
      tailLengthMm: (json['tail_length_mm'] as num?)?.toDouble(),
    );
  }
}

class Distribution {
  final String? breedingRange;
  final String? nonBreedingRange;
  final List<String>? biogeographicRealms;
  final bool? islandEndemic;
  final String? endemicRegion;

  /// ISO country codes (GBIF occurrence records), range size in km2 and the "restricted range" flag (under 50,000 km2).
  final List<String>? countries;
  final double? rangeSizeKm2;
  final bool? restrictedRange;

  Distribution({
    this.breedingRange,
    this.nonBreedingRange,
    this.biogeographicRealms,
    this.islandEndemic,
    this.endemicRegion,
    this.countries,
    this.rangeSizeKm2,
    this.restrictedRange,
  });

  factory Distribution.fromJson(Map<String, dynamic> json) {
    return Distribution(
      breedingRange: _asString(json['breeding_range']),
      nonBreedingRange: _asString(json['non_breeding_range']),
      biogeographicRealms: _asStringList(json['biogeographic_realms']),
      islandEndemic: _asBool(json['island_endemic']),
      endemicRegion: _asString(json['endemic_region']),
      countries: _asStringList(json['countries']),
      rangeSizeKm2: _asDouble(json['range_size_km2']),
      restrictedRange: _asBool(json['restricted_range']),
    );
  }
}

class Habitat {
  final String? primary;
  final List<String>? secondary;
  final int? habitatBreadth;
  final int? elevationalMinM;
  final int? elevationalMaxM;
  final List<String>? habitatTypes;
  final String? microhabitat;

  Habitat({
    this.primary,
    this.secondary,
    this.habitatBreadth,
    this.elevationalMinM,
    this.elevationalMaxM,
    this.habitatTypes,
    this.microhabitat,
  });

  factory Habitat.fromJson(Map<String, dynamic> json) {
    return Habitat(
      primary: _asString(json['primary']),
      secondary: _asStringList(json['secondary']),
      habitatBreadth: _asInt(json['habitat_breadth']),
      elevationalMinM: _asInt(json['elevational_min_m']),
      elevationalMaxM: _asInt(json['elevational_max_m']),
      habitatTypes: _asStringList(json['habitat_types']),
      microhabitat: _asString(json['microhabitat']),
    );
  }
}

class Diet {
  final Map<String, double>? categories;
  final int? dietBreadth;
  final String? primary;
  final String? foragingStrategy;

  Diet({
    this.categories,
    this.dietBreadth,
    this.primary,
    this.foragingStrategy,
  });

  factory Diet.fromJson(Map<String, dynamic> json) {
    final categoriesJson = json['categories'] as Map<String, dynamic>?;
    return Diet(
      categories: categoriesJson?.map((k, v) => MapEntry(k, _asDouble(v) ?? 0.0)),
      dietBreadth: _asInt(json['diet_breadth']),
      primary: _asString(json['primary']),
      foragingStrategy: _asString(json['foraging_strategy']),
    );
  }
}

class Behavior {
  final String? sociality;
  final String? flockSize;
  final String? territoriality;
  final String? migrationStatus;
  final String? movementType;
  final double? dispersalDistanceKm;
  final String? activityPattern;

  /// Xeno-canto recording ids ("XC1074952"); each opens on xeno-canto.org.
  final List<String>? xenoCantoIds;

  Behavior({
    this.sociality,
    this.flockSize,
    this.territoriality,
    this.migrationStatus,
    this.movementType,
    this.dispersalDistanceKm,
    this.activityPattern,
    this.xenoCantoIds,
  });

  factory Behavior.fromJson(Map<String, dynamic> json) {
    return Behavior(
      sociality: _asString(json['sociality']),
      flockSize: _asString(json['flock_size']),
      territoriality: _asString(json['territoriality']),
      migrationStatus: _asString(json['migration_status']),
      movementType: _asString(json['movement_type']),
      dispersalDistanceKm: (json['dispersal_distance_km'] as num?)?.toDouble(),
      activityPattern: _asString(json['activity_pattern']),
      xenoCantoIds: _asStringList(json['xeno_canto_ids']),
    );
  }
}

class Reproduction {
  final int? clutchSizeMin;
  final int? clutchSizeMax;
  final double? clutchSizeMean;
  final double? eggLengthMm;
  final double? eggWidthMm;
  final int? incubationDays;
  final int? fledgingDays;
  final int? broodsPerYear;
  final String? nestType;
  final String? nestPlacement;
  final List<String>? nestMaterial;
  final String? matingSystem;
  final String? parentalCare;

  Reproduction({
    this.clutchSizeMin,
    this.clutchSizeMax,
    this.clutchSizeMean,
    this.eggLengthMm,
    this.eggWidthMm,
    this.incubationDays,
    this.fledgingDays,
    this.broodsPerYear,
    this.nestType,
    this.nestPlacement,
    this.nestMaterial,
    this.matingSystem,
    this.parentalCare,
  });

  factory Reproduction.fromJson(Map<String, dynamic> json) {
    return Reproduction(
      clutchSizeMin: _asInt(json['clutch_size_min']),
      clutchSizeMax: _asInt(json['clutch_size_max']),
      clutchSizeMean: (json['clutch_size_mean'] as num?)?.toDouble(),
      eggLengthMm: (json['egg_length_mm'] as num?)?.toDouble(),
      eggWidthMm: (json['egg_width_mm'] as num?)?.toDouble(),
      incubationDays: _asInt(json['incubation_days']),
      fledgingDays: _asInt(json['fledging_days']),
      broodsPerYear: _asInt(json['broods_per_year']),
      nestType: _asString(json['nest_type']),
      nestPlacement: _asString(json['nest_placement']),
      nestMaterial: _asStringList(json['nest_material']),
      matingSystem: _asString(json['mating_system']),
      parentalCare: _asString(json['parental_care']),
    );
  }
}

class Demography {
  final double? generationLengthYears;
  final int? maxLongevityYears;
  final double? annualSurvivalAdult;
  final double? annualSurvivalJuvenile;
  final String? populationTrend;
  final String? populationSize;
  final double? densityIndividualsPerKm2;

  Demography({
    this.generationLengthYears,
    this.maxLongevityYears,
    this.annualSurvivalAdult,
    this.annualSurvivalJuvenile,
    this.populationTrend,
    this.populationSize,
    this.densityIndividualsPerKm2,
  });

  factory Demography.fromJson(Map<String, dynamic> json) {
    return Demography(
      generationLengthYears: (json['generation_length_years'] as num?)?.toDouble(),
      maxLongevityYears: _asInt(json['max_longevity_years']),
      annualSurvivalAdult: (json['annual_survival_adult'] as num?)?.toDouble(),
      annualSurvivalJuvenile: (json['annual_survival_juvenile'] as num?)?.toDouble(),
      populationTrend: _asString(json['population_trend']),
      populationSize: _asString(json['population_size']),
      densityIndividualsPerKm2: (json['density_individuals_per_km2'] as num?)?.toDouble(),
    );
  }
}

class Conservation {
  final String? iucnStatus;
  final String? populationTrend;
  final List<String>? threats;
  final List<String>? conservationActions;

  Conservation({
    this.iucnStatus,
    this.populationTrend,
    this.threats,
    this.conservationActions,
  });

  factory Conservation.fromJson(Map<String, dynamic> json) {
    return Conservation(
      iucnStatus: _asString(json['iucn_status']),
      populationTrend: _asString(json['population_trend']),
      threats: _asStringList(json['threats']),
      conservationActions: _asStringList(json['conservation_actions']),
    );
  }
}

class Veterinary {
  final List<String>? commonDiseases;
  final List<String>? vaccinationSchedule;
  final int? dewormingFrequencyMonths;
  final int? healthCheckFrequencyMonths;
  final List<String>? zoonoticRisks;
  final List<String>? emergencySigns;
  final String? vetSpecialistType;
  final String? source;
  final String? contributor;
  final String? dateAdded;
  final bool? verified;

  Veterinary({
    this.commonDiseases,
    this.vaccinationSchedule,
    this.dewormingFrequencyMonths,
    this.healthCheckFrequencyMonths,
    this.zoonoticRisks,
    this.emergencySigns,
    this.vetSpecialistType,
    this.source,
    this.contributor,
    this.dateAdded,
    this.verified,
  });

  factory Veterinary.fromJson(Map<String, dynamic> json) {
    return Veterinary(
      commonDiseases: _asStringList(json['common_diseases']),
      vaccinationSchedule: _asStringList(json['vaccination_schedule']),
      dewormingFrequencyMonths: _asInt(json['deworming_frequency_months']),
      healthCheckFrequencyMonths: _asInt(json['health_check_frequency_months']),
      zoonoticRisks: _asStringList(json['zoonotic_risks']),
      emergencySigns: _asStringList(json['emergency_signs']),
      vetSpecialistType: _asString(json['vet_specialist_type']),
      source: _asString(json['source']),
      contributor: _asString(json['contributor']),
      dateAdded: _asString(json['date_added']),
      verified: _asBool(json['verified']),
    );
  }
}

class Enrichment {
  final List<String>? foragingToys;
  final String? socialEnrichment;
  final List<String>? cognitiveToys;
  final String? bathing;
  final Training? training;
  final List<String>? playBehaviors;
  final List<String>? environmentalEnrichment;
  final String? source;
  final String? contributor;
  final String? dateAdded;
  final bool? verified;

  Enrichment({
    this.foragingToys,
    this.socialEnrichment,
    this.cognitiveToys,
    this.bathing,
    this.training,
    this.playBehaviors,
    this.environmentalEnrichment,
    this.source,
    this.contributor,
    this.dateAdded,
    this.verified,
  });

  factory Enrichment.fromJson(Map<String, dynamic> json) {
    return Enrichment(
      foragingToys: _asStringList(json['foraging_toys']),
      socialEnrichment: _asString(json['social_enrichment']),
      cognitiveToys: _asStringList(json['cognitive_toys']),
      bathing: _asString(json['bathing']),
      training: json['training'] != null ? Training.fromJson(json['training']) : null,
      playBehaviors: _asStringList(json['play_behaviors']),
      environmentalEnrichment: _asStringList(json['environmental_enrichment']),
      source: _asString(json['source']),
      contributor: _asString(json['contributor']),
      dateAdded: _asString(json['date_added']),
      verified: _asBool(json['verified']),
    );
  }
}

class Training {
  final bool? targetTraining;
  final bool? recallTraining;
  final String? harnessTraining;

  Training({
    this.targetTraining,
    this.recallTraining,
    this.harnessTraining,
  });

  factory Training.fromJson(Map<String, dynamic> json) {
    return Training(
      targetTraining: _asBool(json['target_training']),
      recallTraining: _asBool(json['recall_training']),
      harnessTraining: _asString(json['harness_training']),
    );
  }
}

class TaxonomyNode {
  final String name;
  final String rank;
  final String? scientificName;
  final List<TaxonomyNode>? children;
  final int? count;

  TaxonomyNode({
    required this.name,
    required this.rank,
    this.scientificName,
    this.children,
    this.count,
  });

  factory TaxonomyNode.fromJson(Map<String, dynamic> json) {
    return TaxonomyNode(
      name: _asString(json['name']) ?? '',
      rank: _asString(json['rank']) ?? '',
      scientificName: _asString(json['scientific_name']),
      children: (json['children'] as List?)?.map((c) => TaxonomyNode.fromJson(c)).toList(),
      count: _asInt(json['count']),
    );
  }
}

/// The API's data-completeness report for one species (core fields only).
class Completeness {
  final int filled;
  final int total;
  final double score;

  /// section -> names of the fields that have no data yet (e.g. morphology -> [body_length_cm, wingspan_cm])
  final Map<String, List<String>> missing;

  Completeness({required this.filled, required this.total, required this.score, this.missing = const {}});

  static Completeness? from(dynamic v) {
    final core = v is Map ? v['core'] : null;
    if (core is! Map) return null;
    final total = _asInt(core['total']) ?? 0;
    if (total == 0) return null;
    final missing = <String, List<String>>{};
    final raw = core['missing'];
    if (raw is Map) {
      for (final e in raw.entries) {
        final fields = _asStringList(e.value) ?? const <String>[];
        if (fields.isNotEmpty) missing[e.key.toString()] = fields;
      }
    }
    final filled = _asInt(core['filled']) ?? 0;
    return Completeness(
      filled: filled,
      total: total,
      score: _asDouble(core['score']) ?? filled / total,
      missing: missing,
    );
  }
}

/// A species photo served by the API at `<API>/images/<path>`.
class SpeciesPhoto {
  final String file; // e.g. images/passeriformes/paridae/parus-major/1.jpg
  final String? author;
  final String? license; // CC0-1.0 or CC-BY-4.0
  final String? source;
  final String? page; // link to the original photo

  SpeciesPhoto({required this.file, this.author, this.license, this.source, this.page});

  /// Accepts one photo (a map), a list of photos, or nothing; anything unreadable is skipped.
  static List<SpeciesPhoto> listFrom(dynamic v) {
    final items = v is List ? v : (v is Map ? [v] : const []);
    final photos = <SpeciesPhoto>[];
    for (final item in items) {
      if (item is! Map) continue;
      final file = _asString(item['file']);
      if (file == null || file.isEmpty) continue;
      photos.add(SpeciesPhoto(
        file: file,
        author: _asString(item['author']),
        license: _asString(item['license']),
        source: _asString(item['source']),
        page: _asString(item['page']),
      ));
    }
    return photos;
  }

  String url(String apiBaseUrl) {
    final path = file.replaceFirst(RegExp(r'^images/'), '').split('/').map(Uri.encodeComponent).join('/');
    return '$apiBaseUrl/images/$path';
  }

  String get licenseUrl => license == 'CC0-1.0'
      ? 'https://creativecommons.org/publicdomain/zero/1.0/'
      : 'https://creativecommons.org/licenses/by/4.0/';
}

class SearchResult {
  final List<Species> species;
  final int total;
  final String query;

  /// Set when the query was a sentence ("endangered owls in forests"): the filters it was understood as
  /// (field -> values, e.g. iucn_status -> [CR, EN, VU]) and the leftover words used for the names.
  final Map<String, List<String>> interpretedFilters;
  final List<String> interpretedWords;
  final List<String> ignoredWords;

  /// Set when a typo was fixed to find results: the spelling the results are for.
  final String? correctedQuery;

  SearchResult({
    required this.species,
    required this.total,
    required this.query,
    this.interpretedFilters = const {},
    this.interpretedWords = const [],
    this.ignoredWords = const [],
    this.correctedQuery,
  });

  bool get isSentence => interpretedFilters.isNotEmpty;

  factory SearchResult.fromJson(Map<String, dynamic> json) {
    return SearchResult(
      species: (json['species'] as List).map((s) => Species.fromJson(s)).toList(),
      total: _asInt(json['total']) ?? 0,
      query: _asString(json['query']) ?? '',
    );
  }
}

// Tolerant JSON readers: the API/YAML data mixes ints and doubles (e.g. `22163.0`)
// and occasionally numbers where strings are expected.
String? _asString(dynamic v) => v == null ? null : v.toString();

int? _asInt(dynamic v) {
  if (v is int) return v;
  if (v is num) return v.toInt();
  if (v is String) return int.tryParse(v) ?? double.tryParse(v)?.toInt();
  return null;
}

double? _asDouble(dynamic v) {
  if (v is num) return v.toDouble();
  if (v is String) return double.tryParse(v);
  return null;
}

bool? _asBool(dynamic v) {
  if (v is bool) return v;
  if (v is String) return v.toLowerCase() == 'true';
  return null;
}

List<String>? _asStringList(dynamic v) =>
    v is List ? v.where((e) => e != null).map((e) => e.toString()).toList() : null;
