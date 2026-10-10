'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { 
  View, 
  Text, 
  TextInput, 
  FlatList, 
  TouchableOpacity,
  ActivityIndicator,
  StyleSheet,
  Keyboard,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Species } from '@/lib/types';
import { useRouter } from 'expo-router';
import { useSettingsStore } from '@/store/providers';

export default function SearchScreen() {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const router = useRouter();
  const { language } = useSettingsStore();

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  const { data, isLoading, error } = useQuery({
    queryKey: ['search', debouncedQuery],
    queryFn: () => api.searchSpecies(debouncedQuery),
    enabled: debouncedQuery.length >= 2,
    staleTime: 5 * 60 * 1000,
  });

  const handlePress = (species: Species) => {
    Keyboard.dismiss();
    router.push(`/species/${encodeURIComponent(species.scientific_name)}`);
  };

  const getCommonName = (species: Species) => {
    if (language === 'fa' && species.common_name_fa) return species.common_name_fa;
    if (language === 'ar' && species.common_name_ar) return species.common_name_ar;
    return species.common_name_en;
  };

  const renderItem = ({ item }: { item: Species }) => (
    <TouchableOpacity 
      style={styles.listItem}
      onPress={() => handlePress(item)}
    >
      <View style={styles.listItemContent}>
        <Text style={styles.commonName}>{getCommonName(item)}</Text>
        <Text style={styles.scientificName}>{item.scientific_name}</Text>
        <View style={styles.metaRow}>
          <Text style={styles.metaText}>{item.order}</Text>
          <Text style={styles.metaText}>{item.family}</Text>
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

  if (debouncedQuery.length < 2) {
    return (
      <View style={styles.emptyState}>
        <Ionicons name="search" size={64} color="#ccc" />
        <Text style={styles.emptyText}>Search for a bird species...</Text>
        <Text style={styles.emptyHint}>Type at least 2 characters</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <Ionicons 
          name="search" 
          size={24} 
          color="#999" 
          style={styles.searchIcon}
        />
        <TextInput
          style={styles.searchInput}
          placeholder="Search by common or scientific name..."
          value={query}
          onChangeText={setQuery}
          autoCapitalize="none"
          autoCorrect={false}
          placeholderTextColor="#999"
        />
        {query && (
          <TouchableOpacity onPress={() => setQuery('')}>
            <Ionicons name="close-circle" size={24} color="#999" />
          </TouchableOpacity>
        )}
      </View>
      
      {isLoading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
        </View>
      )}
      
      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>Error loading results</Text>
        </View>
      )}
      
      {!isLoading && data && (
        <FlatList
          data={data.species || []}
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
      )}
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
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#f5f5f5',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  searchIcon: {
    marginRight: 12,
  },
  searchInput: {
    flex: 1,
    height: 44,
    fontSize: 16,
    color: '#000',
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
    flexWrap: 'wrap',
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
  emptyHint: {
    fontSize: 14,
    color: '#bbb',
    marginTop: 8,
  },
});