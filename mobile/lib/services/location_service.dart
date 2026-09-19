import 'package:geolocator/geolocator.dart';

class LocationPermissionDenied implements Exception {
  final String message;
  LocationPermissionDenied(this.message);
  @override
  String toString() => message;
}

class LocationService {
  /// Captures a single current GPS fix. Requests permission just-in-time
  /// (not at app launch) and explains why, per the spec's permission
  /// guidance: ask only when needed, minimum necessary access.
  Future<Position> getCurrentLocation() async {
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw LocationPermissionDenied('Location services are turned off. Please enable GPS.');
    }

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        throw LocationPermissionDenied('Location permission is required to report an issue at your location.');
      }
    }
    if (permission == LocationPermission.deniedForever) {
      throw LocationPermissionDenied('Location permission was permanently denied. Enable it from Settings.');
    }

    return Geolocator.getCurrentPosition(
      locationSettings: const LocationSettings(accuracy: LocationAccuracy.high),
    );
  }
}
