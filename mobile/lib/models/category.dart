class ComplaintCategory {
  final String id;
  final String code;
  final String name;
  final String moduleId;
  final String defaultSeverity;
  final String icon;

  ComplaintCategory({
    required this.id,
    required this.code,
    required this.name,
    required this.moduleId,
    required this.defaultSeverity,
    required this.icon,
  });

  factory ComplaintCategory.fromJson(Map<String, dynamic> json) {
    return ComplaintCategory(
      id: json['id'] as String,
      code: json['code'] as String,
      name: json['name'] as String,
      moduleId: json['module_id'] as String,
      defaultSeverity: json['default_severity'] as String,
      icon: json['icon'] as String,
    );
  }
}
