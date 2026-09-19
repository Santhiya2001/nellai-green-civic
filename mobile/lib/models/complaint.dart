import 'category.dart';

class ComplaintListItem {
  final String id;
  final String complaintNumber;
  final String categoryCode;
  final String description;
  final String severity;
  final String status;
  final double latitude;
  final double longitude;
  final DateTime createdAt;
  final DateTime? deadlineAt;

  ComplaintListItem({
    required this.id,
    required this.complaintNumber,
    required this.categoryCode,
    required this.description,
    required this.severity,
    required this.status,
    required this.latitude,
    required this.longitude,
    required this.createdAt,
    required this.deadlineAt,
  });

  factory ComplaintListItem.fromJson(Map<String, dynamic> json) {
    return ComplaintListItem(
      id: json['id'] as String,
      complaintNumber: json['complaint_number'] as String,
      categoryCode: json['category_code'] as String,
      description: json['description'] as String,
      severity: json['severity'] as String,
      status: json['status'] as String,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      createdAt: DateTime.parse(json['created_at'] as String),
      deadlineAt: json['deadline_at'] != null ? DateTime.parse(json['deadline_at'] as String) : null,
    );
  }
}

class ComplaintDetail {
  final String id;
  final String complaintNumber;
  final ComplaintCategory category;
  final String description;
  final String? imageUrl;
  final double latitude;
  final double longitude;
  final String? addressText;
  final String severity;
  final String status;
  final String? aiCategoryCode;
  final double? aiConfidence;
  final DateTime? deadlineAt;
  final int escalationLevel;
  final String? rejectionReason;
  final DateTime createdAt;

  ComplaintDetail({
    required this.id,
    required this.complaintNumber,
    required this.category,
    required this.description,
    required this.imageUrl,
    required this.latitude,
    required this.longitude,
    required this.addressText,
    required this.severity,
    required this.status,
    required this.aiCategoryCode,
    required this.aiConfidence,
    required this.deadlineAt,
    required this.escalationLevel,
    required this.rejectionReason,
    required this.createdAt,
  });

  factory ComplaintDetail.fromJson(Map<String, dynamic> json) {
    return ComplaintDetail(
      id: json['id'] as String,
      complaintNumber: json['complaint_number'] as String,
      category: ComplaintCategory.fromJson(json['category'] as Map<String, dynamic>),
      description: json['description'] as String,
      imageUrl: json['image_url'] as String?,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      addressText: json['address_text'] as String?,
      severity: json['severity'] as String,
      status: json['status'] as String,
      aiCategoryCode: json['ai_category_code'] as String?,
      aiConfidence: (json['ai_confidence'] as num?)?.toDouble(),
      deadlineAt: json['deadline_at'] != null ? DateTime.parse(json['deadline_at'] as String) : null,
      escalationLevel: json['escalation_level'] as int,
      rejectionReason: json['rejection_reason'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}
