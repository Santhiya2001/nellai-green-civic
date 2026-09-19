/// Build-time API base URL. Override per-flavor with:
///   flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
///   flutter build apk --dart-define=API_BASE_URL=https://api.nellaigreencivic.org/api/v1
///
/// Defaults to the Android emulator's alias for the host machine's
/// localhost (10.0.2.2) so `flutter run` against a local backend works out
/// of the box during development. A production build MUST pass a real
/// --dart-define; this default must never ship in a release build.
class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1',
  );

  static String get uploadsBaseUrl => baseUrl.replaceAll(RegExp(r'/api/v1/?$'), '');
}
