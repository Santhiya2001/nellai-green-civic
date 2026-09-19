import 'package:flutter/material.dart';

Color severityColor(String severity) {
  switch (severity) {
    case 'CRITICAL':
      return const Color(0xFF7A1622);
    case 'HIGH':
      return const Color(0xFFC0392B);
    case 'MEDIUM':
      return const Color(0xFFD9822B);
    default:
      return const Color(0xFF2E8B57);
  }
}

class SeverityBadge extends StatelessWidget {
  final String severity;
  const SeverityBadge({super.key, required this.severity});

  @override
  Widget build(BuildContext context) {
    final color = severityColor(severity);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: color.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(999)),
      child: Text(severity, style: TextStyle(color: color, fontWeight: FontWeight.w600, fontSize: 12)),
    );
  }
}

class StatusBadge extends StatelessWidget {
  final String status;
  const StatusBadge({super.key, required this.status});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: const Color(0xFF2C4BB0).withValues(alpha: 0.10), borderRadius: BorderRadius.circular(999)),
      child: Text(status, style: const TextStyle(color: Color(0xFF2C4BB0), fontWeight: FontWeight.w600, fontSize: 12)),
    );
  }
}
