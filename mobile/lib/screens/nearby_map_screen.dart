import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../models/complaint.dart';
import '../services/complaint_service.dart';
import '../services/location_service.dart';
import 'complaint_detail_screen.dart';

const _tirunelveliCenter = LatLng(8.7139, 77.7567);

class NearbyMapScreen extends StatefulWidget {
  const NearbyMapScreen({super.key});

  @override
  State<NearbyMapScreen> createState() => _NearbyMapScreenState();
}

class _NearbyMapScreenState extends State<NearbyMapScreen> {
  final _complaintService = ComplaintService();
  final _locationService = LocationService();

  List<ComplaintListItem> _complaints = [];
  LatLng _center = _tirunelveliCenter;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final position = await _locationService.getCurrentLocation();
      _center = LatLng(position.latitude, position.longitude);
    } catch (_) {
      // Fall back to the Tirunelveli town center if location isn't available.
    }
    try {
      final complaints = await _complaintService.nearby(latitude: _center.latitude, longitude: _center.longitude);
      setState(() => _complaints = complaints);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nearby Issues'), actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _load)]),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Stack(
              children: [
                FlutterMap(
                  options: MapOptions(initialCenter: _center, initialZoom: 14),
                  children: [
                    TileLayer(
                      urlTemplate: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                      subdomains: const ['a', 'b', 'c'],
                      userAgentPackageName: 'org.nellaigreencivic.nellai_green_civic',
                    ),
                    MarkerLayer(
                      markers: [
                        for (final c in _complaints)
                          Marker(
                            point: LatLng(c.latitude, c.longitude),
                            width: 40,
                            height: 40,
                            child: GestureDetector(
                              onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => ComplaintDetailScreen(complaintId: c.id))),
                              child: const Icon(Icons.location_pin, color: Colors.red, size: 36),
                            ),
                          ),
                      ],
                    ),
                  ],
                ),
                if (_error != null)
                  Positioned(
                    bottom: 16,
                    left: 16,
                    right: 16,
                    child: Card(
                      color: Colors.red.shade50,
                      child: Padding(padding: const EdgeInsets.all(12), child: Text(_error!)),
                    ),
                  ),
              ],
            ),
    );
  }
}
