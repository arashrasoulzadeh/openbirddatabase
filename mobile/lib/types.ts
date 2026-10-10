export interface Species {
  scientific_name: string;
  common_name_en: string;
  common_name_fa?: string;
  common_name_ar?: string;
  birdnet_id: string;
  ebird_code: string;
  gbif_key: number;
  avibase_id: string;
  iucn_status: string;
  taxon_order: number;
  order: string;
  family: string;
  genus: string;
  species: string;
  
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
    breeding_range?: string;
    non_breeding_range?: string;
    biogeographic_realms?: string[];
    island_endemic?: boolean;
    endemic_region?: string;
  };
  
  habitat?: {
    primary?: string;
    secondary?: string[];
    habitat_breadth?: number;
    elevational_min_m?: number;
    elevational_max_m?: number;
    habitat_types?: string[];
    microhabitat?: string;
  };
  
  diet?: {
    categories?: Record<string, number>;
    diet_breadth?: number;
    primary?: string;
    foraging_strategy?: string;
  };
  
  behavior?: {
    sociality?: string;
    flock_size?: string;
    territoriality?: string;
    migration_status?: string;
    movement_type?: string;
    dispersal_distance_km?: number;
    activity_pattern?: string;
  };
  
  reproduction?: {
    clutch_size_min?: number;
    clutch_size_max?: number;
    clutch_size_mean?: number;
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
    iucn_status?: string;
    population_trend?: string;
    threats?: string[];
    conservation_actions?: string[];
  };
  
  veterinary?: {
    common_diseases?: string[];
    vaccination_schedule?: string[];
    deworming_frequency_months?: number;
    health_check_frequency_months?: number;
    zoonotic_risks?: string[];
    emergency_signs?: string[];
    vet_specialist_type?: string;
  };
  
  enrichment?: {
    foraging_toys?: string[];
    social_enrichment?: string;
    cognitive_toys?: string[];
    bathing?: string;
    training?: {
      target_training?: boolean;
      recall_training?: boolean;
      harness_training?: string;
    };
    play_behaviors?: string[];
    environmental_enrichment?: string[];
  };
  
  sources?: string[];
  data_quality?: 'High' | 'Medium' | 'Low';
  last_updated?: string;
}

export interface SearchResult {
  species: Species[];
  total: number;
  query: string;
}

export interface TaxonomyNode {
  name: string;
  rank: 'order' | 'family' | 'genus' | 'species';
  scientific_name?: string;
  children?: TaxonomyNode[];
  count?: number;
}

export interface FilterOptions {
  orders: string[];
  families: string[];
  iucn_statuses: string[];
  habitats: string[];
  diet_categories: string[];
  migration_types: string[];
}