import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'package:openbird/providers/app_provider.dart';
import 'package:openbird/providers/theme_provider.dart';
import 'package:openbird/providers/language_provider.dart';
import 'package:openbird/screens/splash_screen.dart';
import 'package:openbird/screens/family_species_screen.dart';
import 'package:openbird/screens/favorites_screen.dart';
import 'package:openbird/screens/search_screen.dart';
import 'package:openbird/screens/settings_screen.dart';
import 'package:openbird/screens/species_detail_screen.dart';
import 'package:openbird/screens/taxonomy_screen.dart';
import 'package:openbird/utils/constants.dart';
import 'package:openbird/l10n/app_localizations.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ThemeProvider()..loadTheme()),
        ChangeNotifierProvider(create: (_) => LanguageProvider()..loadLanguage()),
        ChangeNotifierProxyProvider2<ThemeProvider, LanguageProvider, AppProvider>(
          create: (_) => AppProvider(),
          update: (_, theme, language, app) => app!..initialize(theme, language),
        ),
      ],
      child: const OpenBirdApp(),
    ),
  );
}

class OpenBirdApp extends StatelessWidget {
  const OpenBirdApp({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer2<ThemeProvider, LanguageProvider>(
      builder: (context, themeProvider, languageProvider, _) {
        return MaterialApp(
          title: 'OpenBird',
          debugShowCheckedModeBanner: false,
          theme: themeProvider.lightTheme,
          darkTheme: themeProvider.darkTheme,
          themeMode: themeProvider.themeMode,
          locale: languageProvider.locale,
          supportedLocales: AppLocalizations.supportedLocales,
          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          home: const SplashScreen(),
          routes: {
            '/home': (_) => const HomeScreen(),
            '/search': (_) => const SearchScreen(),
            '/taxonomy': (_) => const TaxonomyScreen(),
            '/favorites': (_) => const FavoritesScreen(),
            '/settings': (_) => const SettingsScreen(),
          },
          onGenerateRoute: (settings) {
            if (settings.name == '/species') {
              final args = settings.arguments as Map<String, String>;
              return MaterialPageRoute(
                builder: (_) => SpeciesDetailScreen(scientificName: args['scientificName']!),
              );
            }
            if (settings.name == '/family') {
              final args = settings.arguments as Map<String, String>;
              return MaterialPageRoute(
                builder: (_) => FamilySpeciesScreen(familyName: args['familyName']!),
              );
            }
            return null;
          },
        );
      },
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    SearchScreen(),
    TaxonomyScreen(),
    FavoritesScreen(),
    SettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) => setState(() => _currentIndex = index),
        destinations: [
          NavigationDestination(
            icon: const Icon(Icons.search),
            label: l10n.search,
          ),
          NavigationDestination(
            icon: const Icon(Icons.account_tree),
            label: l10n.taxonomy,
          ),
          NavigationDestination(
            icon: const Icon(Icons.favorite),
            label: l10n.favorites,
          ),
          NavigationDestination(
            icon: const Icon(Icons.settings),
            label: l10n.settings,
          ),
        ],
      ),
    );
  }
}