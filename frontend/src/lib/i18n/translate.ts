import { tables } from './store';
import { Lang, DEFAULT_LANG } from './locales';

type Dict = Record<string, string>;
const all = tables.messages as Record<string, Dict>;

/** Translate a UI string; falls back to English, then to the key. `{name}` placeholders are filled from params. */
export function translate(lang: Lang, key: string, params?: Record<string, string | number>): string {
  let text = all[lang]?.[key] ?? all[DEFAULT_LANG]?.[key] ?? key;
  if (params) for (const [k, v] of Object.entries(params)) text = text.replaceAll(`{${k}}`, String(v));
  return text;
}

// Species-file field -> message key. Entries with a dotted path win over the bare field name.
const FIELD_BY_PATH: Record<string, string> = {
  'habitat.primary': 'primaryHabitat',
  'habitat.secondary': 'secondaryHabitats',
  'diet.primary': 'primaryDiet',
  'diet.categories': 'dietCategories',
  'behavior.vocalizations.calls': 'vocalCalls',
  'behavior.vocalizations.song': 'vocalSong',
  'conservation.iucn_status': 'iucnStatus',
  'taxonomy.species': 'speciesLabel',
  'taxon_id': 'birdnetId',
};

const FIELD_BY_NAME: Record<string, string> = {
  // sections
  taxonomy: 'taxonomy', morphology: 'morphology', distribution: 'distribution', habitat: 'habitat',
  diet: 'dietForaging', behavior: 'behavior', reproduction: 'reproduction', demography: 'demography',
  conservation: 'conservation', veterinary: 'veterinaryCare', enrichment: 'enrichmentTraining',
  // identifiers
  avibase_id: 'avibaseId', ebird_code: 'ebirdCode', gbif_key: 'gbifKey', taxon_order: 'taxonOrder',
  data_quality: 'dataQuality', last_updated: 'lastUpdated', sources: 'sources', iucn_status: 'iucnStatus',
  order: 'order', family: 'family', genus: 'genus',
  // morphology
  body_mass_g: 'bodyMass', body_length_cm: 'bodyLength', wingspan_cm: 'wingspan', bill_length_mm: 'billLength',
  tarsus_length_mm: 'tarsusLength', wing_length_mm: 'wingLength', tail_length_mm: 'tailLength',
  // distribution
  breeding_range: 'breedingRange', range_size_km2: 'rangeSize', restricted_range: 'restrictedRange', non_breeding_range: 'nonBreedingRange', countries: 'countries',
  biogeographic_realms: 'biogeographicRealms', endemic: 'endemic', island_endemic: 'islandEndemic',
  endemic_region: 'endemicRegion',
  // habitat
  habitat_breadth: 'habitatBreadth', habitat_types: 'habitatTypes', microhabitat: 'microhabitat',
  elevational_min_m: 'elevationMin', elevational_max_m: 'elevationMax',
  // diet
  diet_breadth: 'dietBreadth', foraging_niches: 'foragingNiches', diet_sources: 'dietSources',
  foraging_strategy: 'foragingStrategy',
  invertebrates: 'dietInvertebrates', seeds: 'dietSeeds', fruit: 'dietFruit', nectar: 'dietNectar',
  vertebrates: 'dietVertebrates', fish: 'dietFish', carrion: 'dietCarrion', plant_material: 'dietPlantMaterial',
  // behavior
  activity_pattern: 'activityPattern', flock_size_typical: 'flockSize', migration_status: 'migrationStatus',
  movement_type: 'movementType', sociality: 'sociality', territorial: 'territoriality',
  vocalizations: 'vocalizations', xeno_canto_ids: 'xenoCantoIds',
  // reproduction
  egg_length_mm: 'eggLength', egg_width_mm: 'eggWidth',
  generation_length_years: 'generationLength', max_longevity_years: 'maxLongevity',
  annual_survival_adult: 'adultSurvival', annual_survival_juvenile: 'juvenileSurvival',
  density_individuals_per_km2: 'density',
  clutch_size_min: 'clutchSizeMin', clutch_size_max: 'clutchSizeMax', clutch_size_mean: 'meanClutchSize',
  incubation_days: 'incubationPeriod', fledging_days: 'fledgingPeriod', broods_per_year: 'broodsPerYear',
  nest_type: 'nestType', nest_placement: 'nestPlacement', nest_material: 'nestMaterial',
  mating_system: 'matingSystem', parental_care: 'parentalCare',
  // conservation
  cites_appendix: 'citesAppendix', iucn_tag: 'iucnTag', conservation_actions: 'conservationActions', threats: 'threats',
  population_trend: 'populationTrend', population_size: 'populationSize',
  // veterinary
  common_diseases: 'commonDiseases', vaccination_schedule: 'vaccinationSchedule',
  deworming_frequency_months: 'dewormingFrequency', health_check_frequency_months: 'healthCheckFrequency',
  zoonotic_risks: 'zoonoticRisks', emergency_signs: 'emergencySigns', vet_specialist_type: 'specialistType',
  // enrichment
  foraging_toys: 'foragingToys', social_enrichment: 'socialEnrichment', cognitive_toys: 'cognitiveToys',
  bathing: 'bathing', training: 'training', target_training: 'targetTraining', recall_training: 'recallTraining',
  harness_training: 'harnessTraining', play_behaviors: 'playBehaviors', environmental_enrichment: 'environmentalEnrichment',
  // shared
  source: 'source', contributor: 'contributor', date_added: 'dateAdded', verified: 'verified',
};

const humanize = (s: string) => s.replace(/_/g, ' ').replace(/^\w/, (c) => c.toUpperCase());

/** Label for a species-file field (`path` like "habitat.primary"), in the given language. */
export function fieldLabel(lang: Lang, path: string): string {
  const name = path.split('.').pop() as string;
  const key = FIELD_BY_PATH[path] ?? FIELD_BY_NAME[name];
  if (key && all[lang]?.[key] !== undefined) return translate(lang, key);
  if (key && all[DEFAULT_LANG]?.[key]) return translate(DEFAULT_LANG, key);
  return humanize(name);
}

export function iucnLabel(lang: Lang, code: string | undefined | null): string {
  if (!code) return '';
  const key = `iucn${code}`;
  return all[lang]?.[key] ?? all[DEFAULT_LANG]?.[key] ?? code;
}

// --- names -------------------------------------------------------------

const PLACEHOLDERS = new Set(['', 'nan', 'none', 'null', 'n/a']);

/** A usable common name, or '' for empty values and placeholders such as the text "nan". */
export const usableName = (value: unknown): string => {
  const text = value === null || value === undefined ? '' : String(value).trim();
  return PLACEHOLDERS.has(text.toLowerCase()) ? '' : text;
};

/** Common names are lowercase in several languages (Spanish, French, Portuguese, Polish...): capitalise for headings. */
export function displayName(lang: Lang, name: string): string {
  if (!name || /^[\u3040-\u30ff\u3400-\u9fff]/.test(name)) return name;
  return name.charAt(0).toLocaleUpperCase(lang) + name.slice(1);
}

/** Name from a search hit (flat `common_name_xx` keys): selected language, then English, then the scientific name. */
export function nameFromHit(hit: any, lang: Lang): string {
  const localized = usableName(lang === 'en' ? hit.common_name_en : hit[`common_name_${lang}`]);
  return localized || usableName(hit.common_name_en) || hit.scientific_name || '';
}

/** Name from a taxonomy-tree entry: slim entries carry `name`; full entries have `common_en`, `common_fa`, `names`. */
export function nameFromTree(entry: any, lang: Lang): string {
  const slim = usableName(entry.name);
  if (slim) return slim;
  const localized = usableName(
    lang === 'en' ? entry.common_en : lang === 'fa' ? entry.common_fa : entry.names?.[lang],
  );
  return localized || usableName(entry.common_en) || entry.scientific || '';
}

/** Name from a species-file `names` object. */
export function nameFromNames(names: Record<string, string> | undefined, lang: Lang, fallback = ''): string {
  return usableName(names?.[lang]) || usableName(names?.en) || fallback;
}

// --- data values ---------------------------------------------------------

// Fields whose values come from a small fixed vocabulary (translated in values.json).
// Free-text fields (veterinary/enrichment notes) stay in the language of the source data.
const CATEGORICAL_PATHS = new Set([
  'behavior.activity_pattern',
  'behavior.migration_status',
  'behavior.movement_type',
  'behavior.sociality',
  'conservation.cites_appendix',
  'conservation.iucn_tag',
  'data_quality',
  'diet.primary',
  'habitat.habitat_types',
  'habitat.primary',
  'habitat.secondary',
  'reproduction.parental_care',
]);

const valueTable = tables.values;

/** True for fields whose values come from a small fixed vocabulary (and have plain-language explanations). */
export const isCategoricalPath = (path: string) => CATEGORICAL_PATHS.has(path);

/** Translate a categorical data value such as "Forest" or "Small groups"; other values are returned unchanged. */
export function valueLabel(lang: Lang, path: string, value: string): string {
  if (!CATEGORICAL_PATHS.has(path)) return value;
  return valueTable[value]?.[lang] ?? value;
}
