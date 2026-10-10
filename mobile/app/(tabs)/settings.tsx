'use client';

import React from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity,
  Switch,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSettingsStore, useThemeStore } from '@/store/providers';
import { useColorScheme } from 'react-native';

export default function SettingsScreen() {
  const colorScheme = useColorScheme();
  const { theme, setTheme } = useThemeStore();
  const { language, setLanguage, units, setUnits } = useSettingsStore();

  const themeOptions = [
    { value: 'light', label: 'Light', icon: 'sunny' },
    { value: 'dark', label: 'Dark', icon: 'moon' },
    { value: 'system', label: 'System', icon: 'device' },
  ];

  const languageOptions = [
    { value: 'en', label: 'English', native: 'English' },
    { value: 'fa', label: 'Persian', native: 'فارسی' },
    { value: 'ar', label: 'Arabic', native: 'العربية' },
  ];

  const unitsOptions = [
    { value: 'metric', label: 'Metric (kg, cm, m)' },
    { value: 'imperial', label: 'Imperial (lb, in, ft)' },
  ];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Appearance</Text>
        
        <View style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>Theme</Text>
            <Text style={styles.settingDescription}>
              {themeOptions.find(t => t.value === theme)?.label}
            </Text>
          </View>
        </View>
        
        {themeOptions.map(option => (
          <TouchableOpacity
            key={option.value}
            style={[
              styles.themeOption,
              theme === option.value && styles.themeOptionSelected
            ]}
            onPress={() => setTheme(option.value as any)}
          >
            <Ionicons name={option.icon} size={24} color={theme === option.value ? '#007AFF' : '#999'} />
            <Text style={[
              styles.themeOptionLabel,
              theme === option.value && styles.themeOptionLabelSelected
            ]}>
              {option.label}
            </Text>
            {theme === option.value && (
              <Ionicons name="checkmark-circle" size={24} color="#007AFF" />
            )}
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Language & Region</Text>
        
        {languageOptions.map(option => (
          <TouchableOpacity
            key={option.value}
            style={[
              styles.languageOption,
              language === option.value && styles.languageOptionSelected
            ]}
            onPress={() => setLanguage(option.value as any)}
          >
            <View style={styles.languageInfo}>
              <Text style={styles.languageLabel}>{option.label}</Text>
              <Text style={styles.languageNative}>{option.native}</Text>
            </View>
            {language === option.value && (
              <Ionicons name="checkmark-circle" size={24} color="#007AFF" />
            )}
          </TouchableOpacity>
        ))}

        <TouchableOpacity style={styles.settingRow} onPress={() => {}}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>Units</Text>
            <Text style={styles.settingDescription}>
              {unitsOptions.find(u => u.value === units)?.label}
            </Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#999" />
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Data & Privacy</Text>
        
        <TouchableOpacity style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>Clear Cache</Text>
            <Text style={styles.settingDescription}>Remove cached images and data</Text>
          </View>
          <Ionicons name="trash" size={24} color="#F44336" />
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>Export My Data</Text>
            <Text style={styles.settingDescription}>Download your favorites and settings</Text>
          </View>
          <Ionicons name="download" size={24} color="#007AFF" />
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        
        <View style={styles.aboutRow}>
          <Text style={styles.aboutLabel}>Version</Text>
          <Text style={styles.aboutValue}>1.0.0</Text>
        </View>
        
        <TouchableOpacity style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>OpenBird Database</Text>
            <Text style={styles.settingDescription}>Global bird database with 11,000+ species</Text>
          </View>
          <Ionicons name="open" size={20} color="#999" />
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>Source Code</Text>
            <Text style={styles.settingDescription}>View on GitHub</Text>
          </View>
          <Ionicons name="logo-github" size={20} color="#999" />
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>Data Sources</Text>
            <Text style={styles.settingDescription}>BirdNET, BIRDBASE, AVONICHE, BirdFYI</Text>
          </View>
          <Ionicons name="book" size={20} color="#999" />
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          OpenBird is open source. Data licensed under CC-BY 4.0.
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    paddingBottom: 40,
  },
  section: {
    paddingHorizontal: 16,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#999',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 12,
    marginLeft: 4,
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 14,
    paddingHorizontal: 16,
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  settingInfo: {
    flex: 1,
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#000',
  },
  settingDescription: {
    fontSize: 13,
    color: '#999',
    marginTop: 2,
  },
  themeOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 14,
    paddingHorizontal: 16,
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  themeOptionSelected: {
    backgroundColor: '#E8F0FE',
    borderWidth: 1,
    borderColor: '#007AFF',
  },
  themeOptionLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#000',
    marginLeft: 12,
    flex: 1,
  },
  themeOptionLabelSelected: {
    color: '#007AFF',
  },
  languageOption: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 14,
    paddingHorizontal: 16,
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  languageOptionSelected: {
    backgroundColor: '#E8F0FE',
    borderWidth: 1,
    borderColor: '#007AFF',
  },
  languageInfo: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 12,
  },
  languageLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#000',
  },
  languageNative: {
    fontSize: 14,
    color: '#999',
    marginLeft: 8,
  },
  aboutRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 14,
    paddingHorizontal: 16,
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  aboutLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#000',
  },
  aboutValue: {
    fontSize: 16,
    color: '#999',
  },
  footer: {
    padding: 20,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
  },
});