class AppUser {
  final String id;
  final String fullName;
  final String email;
  final String? phone;
  final List<String> roles;
  final bool isActive;
  final bool isVerified;

  AppUser({
    required this.id,
    required this.fullName,
    required this.email,
    required this.phone,
    required this.roles,
    required this.isActive,
    required this.isVerified,
  });

  factory AppUser.fromJson(Map<String, dynamic> json) {
    return AppUser(
      id: json['id'] as String,
      fullName: json['full_name'] as String,
      email: json['email'] as String,
      phone: json['phone'] as String?,
      roles: (json['roles'] as List).map((e) => e.toString()).toList(),
      isActive: json['is_active'] as bool,
      isVerified: json['is_verified'] as bool,
    );
  }

  bool hasRole(String role) => roles.contains(role);
}
