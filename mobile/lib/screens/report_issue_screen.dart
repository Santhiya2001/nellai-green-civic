import 'dart:io';

import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:image_picker/image_picker.dart';

import '../models/category.dart';
import '../services/complaint_service.dart';
import '../services/location_service.dart';

class ReportIssueScreen extends StatefulWidget {
  const ReportIssueScreen({super.key});

  @override
  State<ReportIssueScreen> createState() => _ReportIssueScreenState();
}

class _ReportIssueScreenState extends State<ReportIssueScreen> {
  final _complaintService = ComplaintService();
  final _locationService = LocationService();
  final _descriptionController = TextEditingController();
  final _addressController = TextEditingController();

  List<ComplaintCategory> _categories = [];
  ComplaintCategory? _selectedCategory;
  Position? _position;
  File? _photo;
  bool _locating = false;
  bool _submitting = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadCategories();
  }

  Future<void> _loadCategories() async {
    try {
      final categories = await _complaintService.listCategories();
      setState(() => _categories = categories);
    } catch (e) {
      setState(() => _error = 'Could not load categories: $e');
    }
  }

  Future<void> _captureLocation() async {
    setState(() {
      _locating = true;
      _error = null;
    });
    try {
      final position = await _locationService.getCurrentLocation();
      setState(() => _position = position);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _locating = false);
    }
  }

  Future<void> _pickPhoto(ImageSource source) async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: source, maxWidth: 1600, imageQuality: 85);
    if (picked != null) {
      setState(() => _photo = File(picked.path));
    }
  }

  Future<void> _submit() async {
    if (_selectedCategory == null) {
      setState(() => _error = 'Please select a category.');
      return;
    }
    if (_descriptionController.text.trim().length < 5) {
      setState(() => _error = 'Please describe the issue (at least 5 characters).');
      return;
    }
    if (_position == null) {
      setState(() => _error = 'Please capture your location.');
      return;
    }

    setState(() {
      _submitting = true;
      _error = null;
    });

    try {
      final complaint = await _complaintService.create(
        categoryCode: _selectedCategory!.code,
        description: _descriptionController.text.trim(),
        latitude: _position!.latitude,
        longitude: _position!.longitude,
        addressText: _addressController.text.trim(),
        photo: _photo,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Complaint ${complaint.complaintNumber} submitted.')),
      );
      setState(() {
        _selectedCategory = null;
        _descriptionController.clear();
        _addressController.clear();
        _position = null;
        _photo = null;
      });
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final groupedByModule = <String, List<ComplaintCategory>>{};
    for (final c in _categories) {
      groupedByModule.putIfAbsent(c.moduleId, () => []).add(c);
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Report an Issue')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            DropdownButtonFormField<ComplaintCategory>(
              initialValue: _selectedCategory,
              decoration: const InputDecoration(labelText: 'Category', border: OutlineInputBorder()),
              items: [
                for (final entry in groupedByModule.entries) ...[
                  DropdownMenuItem<ComplaintCategory>(enabled: false, child: Text(entry.key.toUpperCase(), style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.grey))),
                  for (final c in entry.value) DropdownMenuItem(value: c, child: Text('  ${c.name}')),
                ],
              ],
              onChanged: (v) => setState(() => _selectedCategory = v),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _descriptionController,
              maxLines: 4,
              decoration: const InputDecoration(labelText: 'Description', hintText: 'Describe the issue...', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: _locating ? null : _captureLocation,
              icon: const Icon(Icons.my_location),
              label: Text(_locating
                  ? 'Locating...'
                  : _position != null
                      ? 'Captured: ${_position!.latitude.toStringAsFixed(5)}, ${_position!.longitude.toStringAsFixed(5)}'
                      : 'Capture current GPS location'),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _addressController,
              decoration: const InputDecoration(labelText: 'Address / landmark (optional)', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _pickPhoto(ImageSource.camera),
                    icon: const Icon(Icons.camera_alt),
                    label: const Text('Camera'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _pickPhoto(ImageSource.gallery),
                    icon: const Icon(Icons.photo_library),
                    label: const Text('Gallery'),
                  ),
                ),
              ],
            ),
            if (_photo != null) ...[
              const SizedBox(height: 12),
              ClipRRect(borderRadius: BorderRadius.circular(8), child: Image.file(_photo!, height: 160, fit: BoxFit.cover)),
            ],
            if (_error != null) ...[
              const SizedBox(height: 12),
              Text(_error!, style: const TextStyle(color: Colors.red)),
            ],
            const SizedBox(height: 24),
            FilledButton(
              onPressed: _submitting ? null : _submit,
              child: _submitting ? const CircularProgressIndicator() : const Text('Submit Complaint'),
            ),
          ],
        ),
      ),
    );
  }
}
