'use client';

import React, { useEffect } from 'react';
import { 
  View, 
  Text, 
  ScrollView, 
  StyleSheet,
  Image,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Species } from '@/lib/types';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { useSettingsStore } from '@/store/providers';

export default function SpeciesDetailScreen() {
  const { scientificName } = useLocalSearchParams<{ scientificName: string }>();
  const router = useRouter();
  const { language, units } = useSettingsStore();
  const [refreshing, setRefreshing] = React.useState(false);

  const { data: species, isLoading, error, refetch } = useQuery({
    queryKey: ['species', scientificName],
    queryFn: () => api.getSpecies(scientificName!),
    enabled: !!scientificName,
    staleTime: 10 * 60 * 1000,
  });

  const onRefresh = () => {
    setRefreshing(true);
    refetch().finally(() => setRefreshing(false));
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading species...</Text>
      </View>
    );
  }

  if (error || !species) {
    return (
      <View style={styles.errorContainer}>
        <Ionicons name="alert-circle" size={48} color="#F44336" />
        <Text style={styles.errorText}>Failed to load species</Text>
        <TouchableOpacity style={styles.retryButton} onPress={refetch}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const getCommonName = (s: Species) => {
    if (language === 'fa' && s.common_name_fa) return s.common_name_fa;
    if (language === 'ar' && s.common_name_ar) return s.common_name_ar;
    return s.common_name_en;
  };

  const formatNumber = (num?: number, unit?: string) => {
    if (num === undefined || num === null) return '—';
    const formatted = num.toLocaleString();
    return unit ? `${formatted} ${unit}` : formatted;
  };

  const formatRange = (min?: number, max?: number, unit?: string) => {
    if (!min && !max) return '—';
    const u = unit || '';
    if (min && max) return `${min.toLocaleString()}–${max.toLocaleString()} ${u}`;
    if (min) return `≥${min.toLocaleString()} ${u}`;
    return `≤${max.toLocaleString()} ${u}`;
  };

  const renderSection = (title: string, children: React.ReactNode, condition = true) => {
    if (!condition) return null;
    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{title}</Text>
        <View style={styles.sectionContent}>{children}</View>
      </View>
    );
  };

  const renderRow = (label: string, value: string | number) => (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue}>{value}</Text>
    </View>
  );

  const renderArray = (label: string, items: string[] | undefined) => {
    if (!items || items.length === 0) return null;
    return (
      <View style={styles.row}>
        <Text style={styles.rowLabel}>{label}</Text>
        <View style={styles.chipContainer}>
          {items.map((item, i) => (
            <View key={i} style={styles.chip}>
              <Text style={styles.chipText}>{item}</Text>
            </View>
          ))}
        </View>
      </View>
    );
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
      contentContainerStyle={styles.content}
    >
      <View style={styles.header}>
        <View style={styles.headerMain}>
          <Text style={styles.commonName}>{getCommonName(species)}</Text>
          <Text style={styles.scientificName}>{species.scientific_name}</Text>
          <View style={styles.badgeRow}>
            <View style={[styles.badge, { backgroundColor: getIUCNColor(species.iucn_status) }]}>
              <Text style={styles.badgeText}>{species.iucn_status}</Text>
            </View>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{species.order}</Text>
            </View>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{species.family}</Text>
            </View>
          </View>
        </View>
      </View>

      <View style={styles.card}>
        {renderSection('Identification', (
          <>
            {renderRow('BirdNET ID', species.birdnet_id)}
            {renderRow('eBird Code', species.ebird_code)}
            {renderRow('GBIF Key', species.gbif_key)}
            {renderRow('Avibase ID', species.avibase_id)}
            {renderRow('Order', species.order)}
            {renderRow('Family', species.family)}
            {renderRow('Genus', species.genus)}
          </>
        ))}

        {renderSection('Morphology', (
          <>
            {renderRow('Body Mass', formatNumber(species.morphology?.body_mass_g, 'g'))}
            {renderRow('Body Length', formatNumber(species.morphology?.body_length_cm, 'cm'))}
            {renderRow('Wingspan', formatNumber(species.morphology?.wingspan_cm, 'cm'))}
            {renderRow('Bill Length', formatNumber(species.morphology?.bill_length_mm, 'mm'))}
            {renderRow('Tarsus Length', formatNumber(species.morphology?.tarsus_length_mm, 'mm'))}
            {renderRow('Wing Length', formatNumber(species.morphology?.wing_length_mm, 'mm'))}
            {renderRow('Tail Length', formatNumber(species.morphology?.tail_length_mm, 'mm'))}
          </>
        ), species.morphology && Object.keys(species.morphology).length > 0)}

        {renderSection('Distribution', (
          <>
            {renderRow('Breeding Range', species.distribution?.breeding_range || '—')}
            {renderRow('Non-breeding Range', species.distribution?.non_breeding_range || '—')}
            {renderArray('Biogeographic Realms', species.distribution?.biogeographic_realms)}
            {renderRow('Island Endemic', species.distribution?.island_endemic ? 'Yes' : 'No')}
            {renderRow('Endemic Region', species.distribution?.endemic_region || '—')}
          </>
        ), species.distribution && Object.keys(species.distribution).length > 0)}

        {renderSection('Habitat', (
          <>
            {renderRow('Primary Habitat', species.habitat?.primary || '—')}
            {renderArray('Secondary Habitats', species.habitat?.secondary)}
            {renderRow('Habitat Breadth', species.habitat?.habitat_breadth || '—')}
            {renderRow('Elevation Range', formatRange(
              species.habitat?.elevational_min_m,
              species.habitat?.elevational_max_m,
              'm'
            ))}
            {renderArray('Habitat Types', species.habitat?.habitat_types)}
            {renderRow('Microhabitat', species.habitat?.microhabitat || '—')}
          </>
        ), species.habitat && Object.keys(species.habitat).length > 0)}

        {renderSection('Diet & Foraging', (
          <>
            {renderRow('Primary Diet', species.diet?.primary || '—')}
            {renderRow('Diet Breadth', species.diet?.diet_breadth || '—')}
            {renderRow('Foraging Strategy', species.diet?.foraging_strategy || '—')}
            {species.diet?.categories && (
              <View style={styles.dietGrid}>
                {Object.entries(species.diet.categories).map(([cat, val]) => (
                  <View key={cat} style={styles.dietItem}>
                    <Text style={styles.dietLabel}>{cat}</Text>
                    <Text style={styles.dietValue}>{(val * 100).toFixed(0)}%</Text>
                  </View>
                ))}
              </View>
            )}
          </>
        ), species.diet && Object.keys(species.diet).length > 0)}

        {renderSection('Behavior', (
          <>
            {renderRow('Sociality', species.behavior?.sociality || '—')}
            {renderRow('Flock Size', species.behavior?.flock_size || '—')}
            {renderRow('Territoriality', species.behavior?.territoriality || '—')}
            {renderRow('Migration Status', species.behavior?.migration_status || '—')}
            {renderRow('Movement Type', species.behavior?.movement_type || '—')}
            {renderRow('Dispersal Distance', formatNumber(species.behavior?.dispersal_distance_km, 'km'))}
            {renderRow('Activity Pattern', species.behavior?.activity_pattern || '—')}
          </>
        ), species.behavior && Object.keys(species.behavior).length > 0)}

        {renderSection('Reproduction', (
          <>
            {renderRow('Clutch Size', formatRange(
              species.reproduction?.clutch_size_min,
              species.reproduction?.clutch_size_max,
              ''
            ))}
            {renderRow('Mean Clutch', formatNumber(species.reproduction?.clutch_size_mean))}
            {renderRow('Egg Size', species.reproduction?.egg_length_mm && species.reproduction?.egg_width_mm
              ? `${species.reproduction.egg_length_mm}×${species.reproduction.egg_width_mm} mm`
              : '—')}
            {renderRow('Incubation', formatNumber(species.reproduction?.incubation_days, 'days'))}
            {renderRow('Fledging', formatNumber(species.reproduction?.fledging_days, 'days'))}
            {renderRow('Broods/Year', species.reproduction?.broods_per_year || '—')}
            {renderRow('Nest Type', species.reproduction?.nest_type || '—')}
            {renderRow('Nest Placement', species.reproduction?.nest_placement || '—')}
            {renderArray('Nest Material', species.reproduction?.nest_material)}
            {renderRow('Mating System', species.reproduction?.mating_system || '—')}
            {renderRow('Parental Care', species.reproduction?.parental_care || '—')}
          </>
        ), species.reproduction && Object.keys(species.reproduction).length > 0)}

        {renderSection('Demography', (
          <>
            {renderRow('Generation Length', formatNumber(species.demography?.generation_length_years, 'years'))}
            {renderRow('Max Longevity', formatNumber(species.demography?.max_longevity_years, 'years'))}
            {renderRow('Adult Survival', species.demography?.annual_survival_adult 
              ? `${(species.demography.annual_survival_adult * 100).toFixed(1)}%` 
              : '—')}
            {renderRow('Juvenile Survival', species.demography?.annual_survival_juvenile 
              ? `${(species.demography.annual_survival_juvenile * 100).toFixed(1)}%` 
              : '—')}
            {renderRow('Population Trend', species.demography?.population_trend || '—')}
            {renderRow('Population Size', species.demography?.population_size || '—')}
            {renderRow('Density', formatNumber(species.demography?.density_individuals_per_km2, '/km²'))}
          </>
        ), species.demography && Object.keys(species.demography).length > 0)}

        {renderSection('Conservation', (
          <>
            {renderRow('IUCN Status', species.conservation?.iucn_status || species.iucn_status)}
            {renderRow('Population Trend', species.conservation?.population_trend || '—')}
            {renderArray('Threats', species.conservation?.threats)}
            {renderArray('Conservation Actions', species.conservation?.conservation_actions)}
          </>
        ), species.conservation && Object.keys(species.conservation).length > 0)}

        {renderSection('Veterinary Care', (
          <>
            {renderArray('Common Diseases', species.veterinary?.common_diseases)}
            {renderArray('Vaccination Schedule', species.veterinary?.vaccination_schedule)}
            {renderRow('Deworming Frequency', formatNumber(species.veterinary?.deworming_frequency_months, 'months'))}
            {renderRow('Health Check Frequency', formatNumber(species.veterinary?.health_check_frequency_months, 'months'))}
            {renderArray('Zoonotic Risks', species.veterinary?.zoonotic_risks)}
            {renderArray('Emergency Signs', species.veterinary?.emergency_signs)}
            {renderRow('Specialist Type', species.veterinary?.vet_specialist_type || '—')}
          </>
        ), species.veterinary && Object.keys(species.veterinary).length > 0)}

        {renderSection('Enrichment & Training', (
          <>
            {renderArray('Foraging Toys', species.enrichment?.foraging_toys)}
            {renderRow('Social Enrichment', species.enrichment?.social_enrichment || '—')}
            {renderArray('Cognitive Toys', species.enrichment?.cognitive_toys)}
            {renderRow('Bathing', species.enrichment?.bathing || '—')}
            {renderRow('Target Training', species.enrichment?.training?.target_training ? 'Yes' : 'No')}
            {renderRow('Recall Training', species.enrichment?.training?.recall_training ? 'Yes' : 'No')}
            {renderRow('Harness Training', species.enrichment?.training?.harness_training || '—')}
            {renderArray('Play Behaviors', species.enrichment?.play_behaviors)}
            {renderArray('Environmental Enrichment', species.enrichment?.environmental_enrichment)}
          </>
        ), species.enrichment && Object.keys(species.enrichment).length > 0)}

        {renderSection('Sources & Quality', (
          <>
            {renderRow('Sources', species.sources?.join(', ') || '—')}
            {renderRow('Data Quality', species.data_quality || '—')}
            {renderRow('Last Updated', species.last_updated || '—')}
          </>
        ))}
      </View>
    </ScrollView>
  );
}

function getIUCNColor(status: string): string {
  const colors: Record<string, string> = {
    'LC': '#4CAF50',
    'NT': '#FFC107',
    'VU': '#FF9800',
    'EN': '#F44336',
    'CR': '#D32F2F',
    'EW': '#9E9E9E',
    'EX': '#616161',
    'DD': '#2196F3',
  };
  return colors[status] || '#757575';
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    paddingBottom: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#999',
    marginTop: 12,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    fontSize: 16,
    color: '#F44336',
    marginTop: 12,
  },
  retryButton: {
    marginTop: 16,
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: '#007AFF',
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  header: {
    padding: 20,
    backgroundColor: '#fafafa',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  headerMain: {
    maxWidth: '100%',
  },
  commonName: {
    fontSize: 28,
    fontWeight: '700',
    color: '#000',
    marginBottom: 4,
  },
  scientificName: {
    fontSize: 18,
    fontStyle: 'italic',
    color: '#666',
    marginBottom: 16,
  },
  badgeRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  badge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#fff',
  },
  card: {
    padding: 16,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#000',
    marginBottom: 12,
    paddingBottom: 8,
    borderBottomWidth: 2,
    borderBottomColor: '#007AFF',
  },
  sectionContent: {
    gap: 10,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  rowLabel: {
    fontSize: 14,
    color: '#666',
    flex: 1,
    marginRight: 16,
  },
  rowValue: {
    fontSize: 14,
    fontWeight: '500',
    color: '#000',
    textAlign: 'right',
    flex: 1,
  },
  chipContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginTop: 4,
  },
  chip: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    backgroundColor: '#f0f0f0',
    borderRadius: 12,
  },
  chipText: {
    fontSize: 12,
    color: '#333',
  },
  dietGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginTop: 8,
  },
  dietItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#f0f0f0',
    borderRadius: 12,
  },
  dietLabel: {
    fontSize: 12,
    color: '#666',
    marginRight: 8,
  },
  dietValue: {
    fontSize: 12,
    fontWeight: '600',
    color: '#007AFF',
  },
});