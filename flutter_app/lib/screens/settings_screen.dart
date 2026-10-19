import 'package:openbird/l10n/app_localizations.dart';
import 'package:openbird/services/analytics_service.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:openbird/providers/theme_provider.dart';
import 'package:openbird/providers/language_provider.dart';
import 'package:openbird/utils/constants.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  String _version = '1.0.0';

  @override
  void initState() {
    super.initState();
    _loadVersion();
  }

  Future<void> _loadVersion() async {
    final info = await PackageInfo.fromPlatform();
    if (mounted) {
      setState(() {
        _version = '${info.version}+${info.buildNumber}';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final themeProvider = context.watch<ThemeProvider>();
    final languageProvider = context.watch<LanguageProvider>();
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.settings),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildSection(
            l10n.appearance,
            [
              _buildThemeSelector(themeProvider, l10n),
            ],
          ),
          const SizedBox(height: 24),
          _buildSection(
            l10n.languageRegion,
            [
              _buildLanguageSelector(languageProvider, l10n),
              _buildUnitSelector(l10n),
            ],
          ),
          const SizedBox(height: 24),
          _buildSection(
            l10n.dataPrivacy,
            [
              _buildSettingTile(
                icon: Icons.delete_outline,
                title: l10n.clearCache,
                subtitle: l10n.clearCacheSubtitle,
                onTap: _clearCache,
                iconColor: theme.colorScheme.error,
              ),
              SwitchListTile(
                secondary: Icon(Icons.insights, color: theme.colorScheme.primary),
                title: Text(l10n.usageStats),
                subtitle: Text(l10n.usageStatsSubtitle),
                value: AnalyticsService.instance.enabled,
                onChanged: (value) async {
                  await AnalyticsService.instance.setEnabled(value);
                  if (mounted) setState(() {});
                },
              ),
              _buildSettingTile(
                icon: Icons.download,
                title: l10n.exportData,
                subtitle: l10n.exportDataSubtitle,
                onTap: _exportData,
                iconColor: theme.colorScheme.primary,
              ),
            ],
          ),
          const SizedBox(height: 24),
          _buildSection(
            l10n.about,
            [
              _buildSettingTile(
                icon: Icons.info_outline,
                title: l10n.version,
                subtitle: _version,
                trailing: false,
              ),
              _buildSettingTile(
                icon: Icons.public,
                title: l10n.openBirdDatabase,
                subtitle: l10n.openBirdDatabaseSubtitle,
                onTap: () => _launchUrl(Constants.websiteUrl),
              ),
              _buildSettingTile(
                icon: Icons.code,
                title: l10n.sourceCode,
                subtitle: l10n.sourceCodeSubtitle,
                onTap: () => _launchUrl(Constants.githubUrl),
              ),
              _buildSettingTile(
                icon: Icons.science,
                title: l10n.dataSources,
                subtitle: l10n.dataSourcesSubtitle,
                onTap: _showDataSources,
              ),
              _buildSettingTile(
                icon: Icons.article,
                title: l10n.license,
                subtitle: l10n.licenseSubtitle,
                onTap: _showLicense,
              ),
            ],
          ),
          const SizedBox(height: 32),
          Center(
            child: Text(
              l10n.footerText,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _buildSection(String title, List<Widget> children) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 8),
          child: Text(
            title,
            style: theme.textTheme.labelLarge?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        Card(
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: BorderSide(color: theme.colorScheme.outlineVariant),
          ),
          child: Column(children: children),
        ),
      ],
    );
  }

  Widget _buildThemeSelector(ThemeProvider themeProvider, AppLocalizations l10n) {
    return Column(
      children: ThemeMode.values.map((mode) {
        return RadioListTile<ThemeMode>(
          title: Text(_getThemeModeName(mode, l10n)),
          value: mode,
          groupValue: themeProvider.themeMode,
          onChanged: (value) => themeProvider.setThemeMode(value!),
          secondary: Icon(_getThemeModeIcon(mode)),
        );
      }).toList(),
    );
  }

  String _getThemeModeName(ThemeMode mode, AppLocalizations l10n) {
    switch (mode) {
      case ThemeMode.light: return l10n.themeLight;
      case ThemeMode.dark: return l10n.themeDark;
      case ThemeMode.system: return l10n.themeSystem;
    }
  }

  IconData _getThemeModeIcon(ThemeMode mode) {
    switch (mode) {
      case ThemeMode.light: return Icons.light_mode;
      case ThemeMode.dark: return Icons.dark_mode;
      case ThemeMode.system: return Icons.brightness_auto;
    }
  }

  Widget _buildLanguageSelector(LanguageProvider languageProvider, AppLocalizations l10n) {
    return Column(
      children: LanguageProvider.supportedLocales.map((locale) {
        final code = locale.languageCode;
        return RadioListTile<String>(
          title: Text((LanguageProvider.languageNames[code] ?? code)),
          subtitle: Text((LanguageProvider.nativeNames[code] ?? code)),
          value: code,
          groupValue: languageProvider.locale.languageCode,
          onChanged: (value) => languageProvider.setLanguage(value!),
          secondary: Text(code.toUpperCase(), style: const TextStyle(fontWeight: FontWeight.bold)),
        );
      }).toList(),
    );
  }

  Widget _buildUnitSelector(AppLocalizations l10n) {
    return ListTile(
      leading: const Icon(Icons.straighten),
      title: Text(l10n.units),
      subtitle: Text(l10n.metric),
      trailing: const Text('Metric'),
      onTap: () {
        // TODO: Implement unit switching
      },
    );
  }

  Widget _buildSettingTile({
    required IconData icon,
    required String title,
    required String subtitle,
    VoidCallback? onTap,
    Color? iconColor,
    bool trailing = true,
  }) {
    final theme = Theme.of(context);
    return ListTile(
      leading: Icon(icon, color: iconColor ?? theme.colorScheme.primary),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: trailing ? const Icon(Icons.chevron_right) : null,
      onTap: onTap,
    );
  }

  Future<void> _clearCache() async {
    // TODO: Implement cache clearing
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(AppLocalizations.of(context)!.cacheCleared)),
    );
  }

  Future<void> _exportData() async {
    // TODO: Implement data export
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(AppLocalizations.of(context)!.exportStarted)),
    );
  }

  Future<void> _launchUrl(String url) async {
    // no canLaunchUrl check: on Android 11+ it answers "no" unless the manifest lists the link types
    try {
      await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
    } catch (_) {
      // no app can open it
    }
  }

  void _showDataSources() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(AppLocalizations.of(context)!.dataSources),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildDataSource('BirdNET', 'https://birdnet.cornell.edu/', '16,193 species, 434 languages'),
              _buildDataSource('BIRDBASE 2025', 'https://doi.org/10.6084/m9.figshare.27051040', '11,589 species, 78 traits'),
              _buildDataSource('AVONICHE 2025', 'https://datadryad.org/dataset/doi:10.5061/dryad.1zcrjdg56', '10,981 species, 32 foraging niches'),
              _buildDataSource('BirdFYI API', 'https://birdfyi.com/api/v1/', '11,251 species, habitat/behavior'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(AppLocalizations.of(context)!.close),
          ),
        ],
      ),
    );
  }

  Widget _buildDataSource(String name, String url, String description) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
          Text(url, style: const TextStyle(fontSize: 12, color: Colors.blue)),
          Text(description, style: const TextStyle(fontSize: 12)),
        ],
      ),
    );
  }

  void _showLicense() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(AppLocalizations.of(context)!.license),
        content: const SingleChildScrollView(
          child: Text(
            'OpenBird Mobile App - MIT License\n\n'
            'Data Sources:\n'
            '• BirdNET Taxonomy - CC-BY 4.0\n'
            '• BIRDBASE 2025 - CC-BY 4.0\n'
            '• AVONICHE 2025 - CC-BY 4.0\n'
            '• BirdFYI API - CC-BY 4.0\n\n'
            'Third-party licenses available in the app settings.',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(AppLocalizations.of(context)!.close),
          ),
        ],
      ),
    );
  }
}