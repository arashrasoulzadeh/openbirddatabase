'use client';

import React from 'react';
import { 
  View, 
  Text, 
  FlatList, 
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Species } from '@/lib/types';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { useSettingsStore } from '@/store/providers';

export default function FamilyScreen() {
  const { family } = useLocalSearchParams<{ family: string }>();
  const router = useRouter();
  const { language } = useSettingsStore();

  const { data, isLoading, error } = useQuery({
    queryKey: ['family', family],
    queryFn: () => api.getSpeciesByFamily(family!),
    enabled: !!family,
    staleTime: 10 * 60 * 1000,
  });

  const getCommonName = (species: Species) => {
    if (language === 'fa' && species.common_name_fa) return species.common_name_fa;
    if (language === 'ar' && species.common_name_ar) return species.common_name_ar;
    return species.common_name_en;
  };

  const renderItem = ({ item }: { item: Species }) => (
    <TouchableOpacity 
      style={styles.listItem}
      onPress={() => router.push(`/species/${encodeURIComponent(item.scientific_name)}`)}
    >
      <View style={styles.listItemContent}>
        <Text style={styles.commonName}>{getCommonName(item)}</Text>
        <Text style={styles.scientificName}>{item.scientific_name}</Text>
        <View style={styles.metaRow}>
          <Text style={[
            styles.metaText, 
            styles.iucnBadge,
            { backgroundColor: getIUCNColor(item.iucn_status) }
          ]}>
            {item.iucn_status}
          </Text>
        </View>
      </View>
      <Ionicons name="chevron-forward" size={20} color="#999" />
    </TouchableOpacity>
  );

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading species...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Failed to load family</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()}>
          <Ionicons name="chevron-back" size={28} color="#000" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{family}</Text>
        <Text style={styles.headerSubtitle}>{data?.length || 0} species</Text>
      </View>
      
      <FlatList
        data={data || []}
        renderItem={renderItem}
        keyExtractor={(item) => item.scientific_name}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Ionicons name="bird" size={64} color="#ccc" />
            <Text style={styles.emptyText}>No species found</Text>
          </View>
        }
      />
    </View>
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
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  headerTitle: {
    flex: 1,
    fontSize: 22,
    fontWeight: '700',
    color: '#000',
    marginLeft: 12,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#999',
    marginLeft: 12,
  },
  listContent: {
    padding: 8,
  },
  listItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  listItemContent: {
    flex: 1,
    marginRight: 12,
  },
  commonName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#000',
    marginBottom: 4,
  },
  scientificName: {
    fontSize: 14,
    fontStyle: 'italic',
    color: '#666',
    marginBottom: 8,
  },
  metaRow: {
    flexDirection: 'row',
    gap: 8,
  },
  metaText: {
    fontSize: 12,
    color: '#999',
    backgroundColor: '#f5f5f5',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  iucnBadge: {
    color: '#fff',
    fontWeight: '600',
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
    padding: 16,
  },
  errorText: {
    color: '#F44336',
    fontSize: 16,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyText: {
    fontSize: 18,
    color: '#999',
    marginTop: 16,
    fontWeight: '500',
  },
});