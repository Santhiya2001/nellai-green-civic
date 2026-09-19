import 'dart:io';

import '../models/category.dart';
import '../models/complaint.dart';
import 'api_client.dart';

class ComplaintService {
  final _api = ApiClient.instance;

  Future<List<ComplaintCategory>> listCategories() async {
    final data = await _api.get('/categories') as List;
    return data.map((e) => ComplaintCategory.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<ComplaintListItem>> myComplaints() async {
    final data = await _api.get('/complaints', query: {'mine': true}) as List;
    return data.map((e) => ComplaintListItem.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<ComplaintListItem>> nearby({required double latitude, required double longitude, double radiusMeters = 3000}) async {
    final data = await _api.get('/complaints/nearby', query: {
      'latitude': latitude,
      'longitude': longitude,
      'radius_meters': radiusMeters,
    }) as List;
    return data.map((e) => ComplaintListItem.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<ComplaintDetail> getDetail(String id) async {
    final data = await _api.get('/complaints/$id');
    return ComplaintDetail.fromJson(data as Map<String, dynamic>);
  }

  Future<ComplaintDetail> create({
    required String categoryCode,
    required String description,
    required double latitude,
    required double longitude,
    String? addressText,
    File? photo,
  }) async {
    final data = await _api.postMultipart(
      '/complaints',
      fields: {
        'category_code': categoryCode,
        'description': description,
        'latitude': latitude.toString(),
        'longitude': longitude.toString(),
        if (addressText != null && addressText.isNotEmpty) 'address_text': addressText,
      },
      file: photo,
    );
    return ComplaintDetail.fromJson(data as Map<String, dynamic>);
  }

  Future<void> verify(String complaintId, {required bool verified, String? feedback}) async {
    await _api.post('/complaints/$complaintId/verify', body: {'verified': verified, 'feedback': feedback});
  }
}
