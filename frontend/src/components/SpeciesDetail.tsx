'use client';

import { Species } from '@/lib/types';

interface SpeciesDetailProps {
  species: any;
}

export default function SpeciesDetail({ species }: SpeciesDetailProps) {
  const formatNumber = (num: number | null | undefined) => {
    if (num === null || num === undefined) return '—';
    return typeof num === 'number' ? num.toLocaleString() : num;
  };

  const getIUCNColor = (status: string) => {
    switch (status) {
      case 'LC': return 'bg-green-100 text-green-800';
      case 'NT': return 'bg-yellow-100 text-yellow-800';
      case 'VU': return 'bg-orange-100 text-orange-800';
      case 'EN': return 'bg-red-100 text-red-800';
      case 'CR': return 'bg-red-200 text-red-900';
      case 'EW': return 'bg-purple-100 text-purple-800';
      case 'EX': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const renderSection = (title: string, children: React.ReactNode, condition: boolean = true) => {
    if (!condition) return null;
    return (
      <section className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b border-gray-200">{title}</h3>
        {children}
      </section>
    );
  };

  const renderKeyValue = (label: string, value: any, unit?: string) => {
    if (value === null || value === undefined || value === '' || value === '—') return null;
    return (
      <div className="flex justify-between py-2 border-b border-gray-100 last:border-0">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium text-gray-900">{value}{unit ? ` ${unit}` : ''}</span>
      </div>
    );
  };

  const renderArray = (label: string, items: string[]) => {
    if (!items || !items.length) return null;
    return (
      <div className="mb-2">
        <span className="text-gray-600">{label}:</span>
        <ul className="list-disc list-inside text-gray-900 mt-1 space-y-1">
          {items.map((item, i) => <li key={i}>{item}</li>)}
        </ul>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col md:flex-row gap-6 items-start">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-900">{species.common_name_en || species.scientific_name}</h1>
              {species.common_name_fa && (
                <span className="text-xl font-vazir text-gray-600" dir="rtl">{species.common_name_fa}</span>
              )}
            </div>
            <p className="text-2xl text-gray-500 font-italic mb-4">{species.scientific_name}</p>
            
            <div className="flex flex-wrap gap-3">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${({
                'bg-green-100 text-green-800': species.iucn_status === 'LC',
                'bg-yellow-100 text-yellow-800': species.iucn_status === 'NT',
                'bg-orange-100 text-orange-800': species.iucn_status === 'VU',
                'bg-red-100 text-red-800': species.iucn_status === 'EN',
                'bg-red-200 text-red-900': species.iucn_status === 'CR',
              }[species.iucn_status] || 'bg-gray-100 text-gray-700')}`}>
                IUCN: {species.iucn_status}
              </span>
              <span className="px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-sm font-medium">
                {species.order}
              </span>
              <span className="px-3 py-1 rounded-full bg-green-100 text-green-800 text-sm font-medium">
                {species.family}
              </span>
            </div>
          </div>
          
          <div className="md:w-64 flex-shrink-0">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-center">
                <p className="text-3xl font-bold text-gray-900">{species.body_mass_g ? species.body_mass_g.toLocaleString() : '—'} <span className="text-sm font-normal text-gray-500">g</span></p>
                <p className="text-sm text-gray-500">Body Mass</p>
              </div>
              {species.wingspan_cm && (
                <div className="mt-3 pt-3 border-t border-gray-200 text-center">
                  <p className="text-2xl font-bold text-gray-900">{species.wingspan_cm} <span className="text-sm font-normal text-gray-500">cm</span></p>
                  <p className="text-sm text-gray-500">Wingspan</p>
                </div>
              )}
              {species.body_length_cm && (
                <div className="mt-3 pt-3 border-t border-gray-200 text-center">
                  <p className="text-2xl font-bold text-gray-900">{species.body_length_cm} <span className="text-sm font-normal text-gray-500">cm</span></p>
                  <p className="text-sm text-gray-500">Body Length</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Sections */}
      <div className="space-y-8">
        {renderSection('Taxonomy', (
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {renderKeyValue('Order', species.order)}
            {renderKeyValue('Family', species.family)}
            {renderKeyValue('Genus', species.genus)}
            {renderKeyValue('Species', species.scientific_name.split(' ')[1])}
            {renderKeyValue('eBird Code', species.ebird_code)}
            {renderKeyValue('GBIF Key', species.gbif_key?.toLocaleString())}
            {renderKeyValue('BirdNET ID', species.taxon_id)}
            {renderKeyValue('Avibase ID', species.avibase_id)}
          </dl>
        ))}

        {renderSection('Conservation Status', (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <span className={`px-4 py-2 rounded-full text-sm font-semibold ${({
                'bg-green-100 text-green-800': species.iucn_status === 'LC',
                'bg-yellow-100 text-yellow-800': species.iucn_status === 'NT',
                'bg-orange-100 text-orange-800': species.iucn_status === 'VU',
                'bg-red-100 text-red-800': species.iucn_status === 'EN',
                'bg-red-200 text-red-900': species.iucn_status === 'CR',
              }[species.iucn_status] || 'bg-gray-100 text-gray-700')}`}>
                IUCN: {species.iucn_status}
              </span>
              <span className="px-3 py-1 bg-gray-100 rounded-full text-sm text-gray-700">
                CITES: {species.conservation?.cites_appendix || 'Not listed'}
              </span>
            </div>
            {renderArray('Threats', species.conservation?.threats || [])}
            {renderArray('Conservation Actions', species.conservation?.conservation_actions || [])}
          </div>
        ))}

        {renderSection('Morphology', (
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {renderKeyValue('Body Mass', species.morphology?.body_mass_g, 'g')}
            {renderKeyValue('Body Length', species.morphology?.body_length_cm, 'cm')}
            {renderKeyValue('Wingspan', species.morphology?.wingspan_cm, 'cm')}
            {renderKeyValue('Bill Length', species.morphology?.bill_length_mm, 'mm')}
            {renderKeyValue('Tarsus Length', species.morphology?.tarsus_length_mm, 'mm')}
            {renderKeyValue('Wing Length', species.morphology?.wing_length_mm, 'mm')}
            {renderKeyValue('Tail Length', species.morphology?.tail_length_mm, 'mm')}
          </dl>
        ), species.morphology?.body_mass_g || species.morphology?.body_length_cm)}

        {renderSection('Habitat', (
          <div className="space-y-4">
            {renderKeyValue('Primary Habitat', species.habitat?.primary)}
            {renderArray('Secondary Habitats', species.habitat?.secondary || [])}
            {renderKeyValue('Habitat Breadth', species.habitat?.habitat_breadth)}
            {renderKeyValue('Elevation Range', `${species.habitat?.elevational_min_m || 0}–${species.habitat?.elevational_max_m || 0} m`)}
            {renderArray('Habitat Types', species.habitat?.habitat_types || [])}
            {renderKeyValue('Microhabitat', species.habitat?.microhabitat)}
          </div>
        ), species.habitat?.primary)}

        {renderSection('Diet & Foraging', (
          <div className="space-y-4">
            {renderKeyValue('Primary Diet', species.diet?.primary)}
            {renderKeyValue('Diet Breadth', species.diet?.diet_breadth)}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(species.diet?.categories || {}).map(([key, value]) => (
                <div key={key} className="flex justify-between py-2 border-b border-gray-100">
                  <span className="capitalize text-gray-600">{key.replace('_', ' ')}</span>
                  <span className="font-medium text-gray-900">{value}</span>
                </div>
              ))}
            </div>
            <p className="text-sm text-gray-500">Sum: {Object.values(species.diet?.categories || {}).reduce((a: number, b: number) => a + (b || 0), 0)}</p>
          </div>
        ), species.diet?.primary)}

        {renderSection('Behavior', (
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {renderKeyValue('Sociality', species.behavior?.sociality)}
            {renderKeyValue('Typical Flock Size', species.behavior?.flock_size_typical)}
            {renderKeyValue('Max Flock Size', species.behavior?.flock_size_max)}
            {renderKeyValue('Territorial', species.behavior?.territorial ? 'Yes' : 'No')}
            {renderKeyValue('Migration Status', species.behavior?.migration_status)}
            {renderKeyValue('Movement Type', species.behavior?.movement_type)}
            {renderKeyValue('Activity Pattern', species.behavior?.activity_pattern)}
            {renderKeyValue('Song', species.behavior?.vocalizations?.song)}
            {renderArray('Calls', species.behavior?.vocalizations?.calls || [])}
          </dl>
        ), species.behavior?.sociality)}

        {renderSection('Reproduction', (
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {renderKeyValue('Clutch Size (mean)', species.reproduction?.clutch_size_mean)}
            {renderKeyValue('Clutch Size Range', `${species.reproduction?.clutch_size_min || '—'}–${species.reproduction?.clutch_size_max || '—'}`)
            {renderKeyValue('Incubation', species.reproduction?.incubation_days ? `${species.reproduction.incubation_days} days` : '—')}
            {renderKeyValue('Fledging', species.reproduction?.fledging_days ? `${species.reproduction.fledging_days} days` : '—')}
            {renderKeyValue('Broods/Year', species.reproduction?.broods_per_year)}
            {renderKeyValue('Nest Type', species.reproduction?.nest_type)}
            {renderKeyValue('Nest Placement', species.reproduction?.nest_placement)}
            {renderArray('Nest Materials', species.reproduction?.nest_material || [])}
            {renderKeyValue('Mating System', species.reproduction?.mating_system)}
            {renderKeyValue('Parental Care', species.reproduction?.parental_care)}
          </dl>
        ), species.reproduction?.clutch_size_mean || species.reproduction?.nest_type)}

        {renderSection('Demography', (
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {renderKeyValue('Generation Length', species.demography?.generation_length_years ? `${species.demography.generation_length_years} years` : '—')}
            {renderKeyValue('Max Longevity', species.demography?.max_longevity_years ? `${species.demography.max_longevity_years} years` : '—')}
            {renderKeyValue('Adult Survival', species.demography?.annual_survival_adult ? `${(species.demography.annual_survival_adult * 100).toFixed(1)}%` : '—')}
            {renderKeyValue('Juvenile Survival', species.demography?.annual_survival_juvenile ? `${(species.demography.annual_survival_juvenile * 100).toFixed(1)}%` : '—')}
            {renderKeyValue('Population Trend', species.demography?.population_trend)}
            {renderKeyValue('Population Size', species.demography?.population_size)}
            {renderKeyValue('Density', species.demography?.density_individuals_per_km2 ? `${species.demography.density_individuals_per_km2}/km²` : '—')}
          </dl>
        ), species.demography?.generation_length_years || species.demography?.max_longevity_years)}

        {renderSection('Distribution', (
          <div className="space-y-4">
            {renderKeyValue('Breeding Range', species.distribution?.breeding_range)}
            {renderKeyValue('Non-breeding Range', species.distribution?.non_breeding_range)}
            {renderArray('Countries (ISO)', species.distribution?.countries || [])}
            {renderArray('Biogeographic Realms', species.distribution?.biogeographic_realms || [])}
            {renderKeyValue('Endemic', species.distribution?.endemic ? 'Yes' : 'No')}
            {renderKeyValue('Island Endemic', species.distribution?.island_endemic ? 'Yes' : 'No')}
          </div>
        ), species.distribution?.breeding_range)}

        {renderSection('Veterinary Care', (
          <div className="space-y-4">
            {renderArray('Common Diseases', species.veterinary?.common_diseases || [])}
            {renderArray('Vaccination Schedule', species.veterinary?.vaccination_schedule || [])}
            {renderKeyValue('Deworming Frequency', species.veterinary?.deworming_frequency_months ? `${species.veterinary.deworming_frequency_months} months` : '—')}
            {renderKeyValue('Health Check Frequency', species.veterinary?.health_check_frequency_months ? `${species.veterinary.health_check_frequency_months} months` : '—')}
            {renderArray('Zoonotic Risks', species.veterinary?.zoonotic_risks || [])}
            {renderArray('Emergency Signs', species.veterinary?.emergency_signs || [])}
            {renderKeyValue('Specialist Type', species.veterinary?.vet_specialist_type)}
          </div>
        ), species.veterinary?.common_diseases?.length || species.veterinary?.emergency_signs?.length)}

        {renderSection('Enrichment & Training', (
          <div className="space-y-4">
            {renderArray('Foraging Toys', species.enrichment?.foraging_toys || [])}
            {renderKeyValue('Social Enrichment', species.enrichment?.social_enrichment)}
            {renderArray('Cognitive Toys', species.enrichment?.cognitive_toys || [])}
            {renderKeyValue('Bathing', species.enrichment?.bathing)}
            {renderKeyValue('Target Training', species.enrichment?.training?.target_training ? 'Yes' : 'No')}
            {renderKeyValue('Recall Training', species.enrichment?.training?.recall_training ? 'Yes' : 'No')}
            {renderKeyValue('Harness Training', species.enrichment?.training?.harness_training || '—')}
            {renderArray('Play Behaviors', species.enrichment?.play_behaviors || [])}
            {renderArray('Environmental Enrichment', species.enrichment?.environmental_enrichment || [])}
          </div>
        ), species.enrichment?.foraging_toys?.length || species.enrichment?.training?.target_training)}

        {renderSection('Sources & Quality', (
          <div className="space-y-2">
            <p className="text-sm text-gray-600">Sources: {species.sources?.join(', ') || '—'}</p>
            <p className="text-sm text-gray-600">Last Updated: {species.last_updated || '—'}</p>
            <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${{
              'bg-green-100 text-green-800': species.data_quality === 'High',
              'bg-yellow-100 text-yellow-800': species.data_quality === 'Medium',
              'bg-orange-100 text-orange-800': species.data_quality === 'Low',
              'bg-gray-100 text-gray-700': species.data_quality === 'Interpolated',
            }[species.data_quality] || 'bg-gray-100 text-gray-700'}`}>
              Data Quality: {species.data_quality}
            </span>
          </div>
        ))}
      </div>
    );
  }
}