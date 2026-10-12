class Constants {
  // Set at build time from the repo-root .env domains:
  //   flutter build apk --dart-define=API_BASE_URL=https://api.example.org \
  //                     --dart-define=SITE_URL=https://example.org
  static const String apiBaseUrl =
      String.fromEnvironment('API_BASE_URL', defaultValue: 'http://localhost:8000');
  static const String websiteUrl =
      String.fromEnvironment('SITE_URL', defaultValue: 'https://openbird.org');
  static const String githubUrl = 'https://github.com/arashrasoulzadeh/openbirddatabase';
}