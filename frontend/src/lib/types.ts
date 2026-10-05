export interface Species {
  id: string;
  scientific_name: string;
  common_name_fa: string;
  common_name_en: string;
  common_name_ar?: string;
  common_name_es?: string;
  common_name_fr?: string;
  common_name_de?: string;
  common_name_ru?: string;
  common_name_zh?: string;
  order: string;
  family: string;
  genus: string;
  iucn_status: string;
  primary_habitat: string;
  primary_diet: string;
  migration_status: string;
  countries: string[];
  body_mass_g: number | null;
  body_length_cm: number | null;
  wingspan_cm: number | null;
  data_quality: string;
  sources: string[];
  taxon_order: number;
  ebird_code: string;
  gbif_key: number;
  avibase_id: string;
  avibase_id?: string;
  taxon_id: string;
  iucn_status: string;
  taxon_order: number;
  names?: {
    scientific: string;
    fa: string;
    en: string;
    [key: string]: string;
  };
  taxonomy?: {
    order: string;
    family: string;
    genus: string;
    species: string;
  };
  morphology?: {
    body_mass_g?: number;
    body_length_cm?: number;
    wingspan_cm?: number;
    bill_length_mm?: number;
    tarsus_length_mm?: number;
    wing_length_mm?: number;
    tail_length_mm?: number;
  };
  distribution?: {
    breeding_range: string;
    non_breeding_range: string;
    countries: string[];
    biogeographic_realms: string[];
    endemic: boolean;
    island_endemic: boolean;
  };
  habitat?: {
    primary: string;
    secondary: string[];
    habitat_breadth: number;
    elevational_min_m: number;
    elevational_max_m: number;
    habitat_types: string[];
    microhabitat: string;
  };
  diet?: {
    primary: string;
    diet_breadth: number;
    categories: {
      invertebrates: number;
      seeds: number;
      fruit: number;
      nectar: number;
      vertebrates: number;
      fish: number;
      carrion: number;
      plant_material: number;
    };
    foraging_niches: Record<string, number>;
    diet_sources: string[];
  };
  behavior?: {
    sociality: string;
    flock_size_typical: string;
    flock_size_max: number;
    territorial: boolean;
    migration_status: string;
    movement_type: string;
    activity_pattern: string;
    vocalizations: {
      song: string;
      calls: string[];
    };
    xeno_canto_ids: string[];
  };
  reproduction?: {
    clutch_size_mean?: number;
    clutch_size_min?: number;
    clutch_size_max?: number;
    egg_length_mm?: number;
    egg_width_mm?: number;
    incubation_days?: number;
    fledging_days?: number;
    broods_per_year?: number;
    nest_type?: string;
    nest_placement?: string;
    nest_material?: string[];
    mating_system?: string;
    parental_care?: string;
  };
  demography?: {
    generation_length_years?: number;
    max_longevity_years?: number;
    annual_survival_adult?: number;
    annual_survival_juvenile?: number;
    population_trend?: string;
    population_size?: string;
    density_individuals_per_km2?: number;
  };
  conservation?: {
    iucn_status: string;
    iucn_criteria?: string;
    cites_appendix: string;
    threats: string[];
    conservation_actions: string[];
  };
  veterinary?: {
    common_diseases: string[];
    vaccination_schedule: string[];
    deworming_frequency_months: number;
    health_check_frequency_months: number;
    zoonotic_risks: string[];
    emergency_signs: string[];
    vet_specialist_type: string;
  };
  enrichment?: {
    foraging_toys: string[];
    social_enrichment: string;
    cognitive_toys: string[];
    bathing: string;
    training: {
      target_training: boolean;
      recall_training: boolean;
      harness_training: string;
    };
    play_behaviors: string[];
    environmental_enrichment: string[];
  };
  sources: string[];
  last_updated: string;
  data_quality: string;
  body_text?: string;
}

export interface SearchResult {
  hits: Species[];
  total: number;
  limit: number;
  offset: number;
}

export interface TaxonomyTree {
  [order: string]: {
    [family: string]: {
      [genus: string]: Species[];
    };
  };
}

export interface FieldStats {
  iucn_status: Record<string, number>;
  primary_habitat: Record<string, number>;
  primary_diet: Record<string, number>;
  migration_status: Record<string, number>;
  order: Record<string, number>;
  family: Record<string, number>;
  countries: Record<string, number>;
}