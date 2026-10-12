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
  });

  factory Species.fromJson(Map<String, dynamic> json) {
    return Species(
      scientificName: json['scientific_name'] ?? '',
      commonNameEn: json['common_name_en'] ?? '',
      commonNameFa: json['common_name_fa'],
      commonNameAr: json['common_name_ar'],
      commonNameEs: json['common_name_es'],
      commonNameFr: json['common_name_fr'],
      commonNameDe: json['common_name_de'],
      commonNamePt: json['common_name_pt'],
      commonNameRu: json['common_name_ru'],
      commonNameJa: json['common_name_ja'],
      commonNameZh: json['common_name_zh'],
      commonNameNl: json['common_name_nl'],
      commonNamePl: json['common_name_pl'],
      commonNameTr: json['common_name_tr'],
      birdnetId: json['birdnet_id'] ?? '',
      ebirdCode: json['ebird_code'] ?? '',
      gbifKey: json['gbif_key'] ?? 0,
      avibaseId: json['avibase_id'] ?? '',
      iucnStatus: json['iucn_status'] ?? 'LC',
      taxonOrder: json['taxon_order'] ?? 0,
      order: json['order'] ?? '',
      family: json['family'] ?? '',
      genus: json['genus'] ?? '',
      species: json['species'] ?? '',
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
      sources: (json['sources'] as List?)?.cast<String>(),
      dataQuality: json['data_quality'],
      lastUpdated: json['last_updated'],
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

  Distribution({
    this.breedingRange,
    this.nonBreedingRange,
    this.biogeographicRealms,
    this.islandEndemic,
    this.endemicRegion,
  });

  factory Distribution.fromJson(Map<String, dynamic> json) {
    return Distribution(
      breedingRange: json['breeding_range'],
      nonBreedingRange: json['non_breeding_range'],
      biogeographicRealms: (json['biogeographic_realms'] as List?)?.cast<String>(),
      islandEndemic: json['island_endemic'],
      endemicRegion: json['endemic_region'],
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
      primary: json['primary'],
      secondary: (json['secondary'] as List?)?.cast<String>(),
      habitatBreadth: json['habitat_breadth'],
      elevationalMinM: json['elevational_min_m'],
      elevationalMaxM: json['elevational_max_m'],
      habitatTypes: (json['habitat_types'] as List?)?.cast<String>(),
      microhabitat: json['microhabitat'],
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
      categories: categoriesJson?.map((k, v) => MapEntry(k, (v as num).toDouble())),
      dietBreadth: json['diet_breadth'],
      primary: json['primary'],
      foragingStrategy: json['foraging_strategy'],
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

  Behavior({
    this.sociality,
    this.flockSize,
    this.territoriality,
    this.migrationStatus,
    this.movementType,
    this.dispersalDistanceKm,
    this.activityPattern,
  });

  factory Behavior.fromJson(Map<String, dynamic> json) {
    return Behavior(
      sociality: json['sociality'],
      flockSize: json['flock_size'],
      territoriality: json['territoriality'],
      migrationStatus: json['migration_status'],
      movementType: json['movement_type'],
      dispersalDistanceKm: (json['dispersal_distance_km'] as num?)?.toDouble(),
      activityPattern: json['activity_pattern'],
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
      clutchSizeMin: json['clutch_size_min'],
      clutchSizeMax: json['clutch_size_max'],
      clutchSizeMean: (json['clutch_size_mean'] as num?)?.toDouble(),
      eggLengthMm: (json['egg_length_mm'] as num?)?.toDouble(),
      eggWidthMm: (json['egg_width_mm'] as num?)?.toDouble(),
      incubationDays: json['incubation_days'],
      fledgingDays: json['fledging_days'],
      broodsPerYear: json['broods_per_year'],
      nestType: json['nest_type'],
      nestPlacement: json['nest_placement'],
      nestMaterial: (json['nest_material'] as List?)?.cast<String>(),
      matingSystem: json['mating_system'],
      parentalCare: json['parental_care'],
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
      maxLongevityYears: json['max_longevity_years'],
      annualSurvivalAdult: (json['annual_survival_adult'] as num?)?.toDouble(),
      annualSurvivalJuvenile: (json['annual_survival_juvenile'] as num?)?.toDouble(),
      populationTrend: json['population_trend'],
      populationSize: json['population_size'],
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
      iucnStatus: json['iucn_status'],
      populationTrend: json['population_trend'],
      threats: (json['threats'] as List?)?.cast<String>(),
      conservationActions: (json['conservation_actions'] as List?)?.cast<String>(),
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
      commonDiseases: (json['common_diseases'] as List?)?.cast<String>(),
      vaccinationSchedule: (json['vaccination_schedule'] as List?)?.cast<String>(),
      dewormingFrequencyMonths: json['deworming_frequency_months'],
      healthCheckFrequencyMonths: json['health_check_frequency_months'],
      zoonoticRisks: (json['zoonotic_risks'] as List?)?.cast<String>(),
      emergencySigns: (json['emergency_signs'] as List?)?.cast<String>(),
      vetSpecialistType: json['vet_specialist_type'],
      source: json['source'],
      contributor: json['contributor'],
      dateAdded: json['date_added'],
      verified: json['verified'],
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
      foragingToys: (json['foraging_toys'] as List?)?.cast<String>(),
      socialEnrichment: json['social_enrichment'],
      cognitiveToys: (json['cognitive_toys'] as List?)?.cast<String>(),
      bathing: json['bathing'],
      training: json['training'] != null ? Training.fromJson(json['training']) : null,
      playBehaviors: (json['play_behaviors'] as List?)?.cast<String>(),
      environmentalEnrichment: (json['environmental_enrichment'] as List?)?.cast<String>(),
      source: json['source'],
      contributor: json['contributor'],
      dateAdded: json['date_added'],
      verified: json['verified'],
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
      targetTraining: json['target_training'],
      recallTraining: json['recall_training'],
      harnessTraining: json['harness_training'],
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
      name: json['name'] ?? '',
      rank: json['rank'] ?? '',
      scientificName: json['scientific_name'],
      children: (json['children'] as List?)?.map((c) => TaxonomyNode.fromJson(c)).toList(),
      count: json['count'],
    );
  }
}

class SearchResult {
  final List<Species> species;
  final int total;
  final String query;

  SearchResult({
    required this.species,
    required this.total,
    required this.query,
  });

  factory SearchResult.fromJson(Map<String, dynamic> json) {
    return SearchResult(
      species: (json['species'] as List).map((s) => Species.fromJson(s)).toList(),
      total: json['total'] ?? 0,
      query: json['query'] ?? '',
    );
  }
}