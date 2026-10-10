'use client';

import React, { useState } from 'react';
import { 
  View, 
  Text, 
  FlatList, 
  TouchableOpacity,
  StyleSheet,
  SectionList,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { TaxonomyNode } from '@/lib/types';
import { useRouter } from 'expo-router';
import { useSettingsStore } from '@/store/providers';

export default function TaxonomyScreen() {
  const [expandedOrders, setExpandedOrders] = useState<Set<string>>(new Set());
  const router = useRouter();
  const { language } = useSettingsStore();

  const { data, isLoading, error } = useQuery({
    queryKey: ['taxonomy'],
    queryFn: () => api.getTaxonomy(),
    staleTime: 10 * 60 * 1000,
  });

  const toggleOrder = (orderName: string) => {
    setExpandedOrders(prev => {
      const next = new Set(prev);
      if (next.has(orderName)) {
        next.delete(orderName);
      } else {
        next.add(orderName);
      }
      return next;
    });
  };

  const renderOrderHeader = ({ section }: { section: TaxonomyNode }) => (
    <TouchableOpacity 
      style={styles.orderHeader}
      onPress={() => toggleOrder(section.name)}
    >
      <View style={styles.orderHeaderContent}>
        <Ionicons 
          name={expandedOrders.has(section.name) ? 'chevron-down' : 'chevron-forward'} 
          size={20} 
          color="#999"
          style={styles.chevron}
        />
        <Text style={styles.orderName}>{section.name}</Text>
        <Text style={styles.orderCount}>{section.count} families</Text>
      </View>
    </TouchableOpacity>
  );

  const renderFamily = ({ item }: { item: TaxonomyNode }) => (
    <TouchableOpacity 
      style={styles.familyItem}
      onPress={() => router.push(`/taxonomy/family/${encodeURIComponent(item.name)}`)}
    >
      <View style={styles.familyContent}>
        <Text style={styles.familyName}>{item.name}</Text>
        <Text style={styles.familyCount}>{item.count} species</Text>
      </View>
      <Ionicons name="chevron-forward" size={20} color="#999" />
    </TouchableOpacity>
  );

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading taxonomy...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Failed to load taxonomy</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Taxonomy Browser</Text>
        <Text style={styles.headerSubtitle}>
          Browse {data?.length || 0} orders and their families
        </Text>
      </View>
      
      <SectionList
        sections={data || []}
        renderSectionHeader={renderOrderHeader}
        renderItem={renderFamily}
        keyExtractor={(item) => item.name}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
        SectionSeparatorComponent={() => <View style={styles.sectionSeparator} />}
        contentContainerStyle={styles.listContent}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    padding: 20,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: '#000',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#999',
    marginTop: 4,
  },
  listContent: {
    padding: 8,
    paddingBottom: 20,
  },
  orderHeader: {
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: '#fafafa',
    marginBottom: 4,
    borderRadius: 8,
  },
  orderHeaderContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  chevron: {
    marginRight: 12,
  },
  orderName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#000',
    flex: 1,
  },
  orderCount: {
    fontSize: 14,
    color: '#999',
  },
  familyItem: {
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
  familyContent: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginRight: 12,
  },
  familyName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#000',
  },
  familyCount: {
    fontSize: 13,
    color: '#999',
  },
  separator: {
    height: 1,
    backgroundColor: '#f0f0f0',
    marginHorizontal: 16,
  },
  sectionSeparator: {
    height: 8,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#999',
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
});