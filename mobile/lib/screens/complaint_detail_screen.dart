import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../config/api_config.dart';
import '../models/complaint.dart';
import '../services/complaint_service.dart';
import '../widgets/badges.dart';

class ComplaintDetailScreen extends StatefulWidget {
  final String complaintId;
  const ComplaintDetailScreen({super.key, required this.complaintId});

  @override
  State<ComplaintDetailScreen> createState() => _ComplaintDetailScreenState();
}

class _ComplaintDetailScreenState extends State<ComplaintDetailScreen> {
  final _service = ComplaintService();
  late Future<ComplaintDetail> _future;
  bool _submittingVerification = false;

  @override
  void initState() {
    super.initState();
    _future = _service.getDetail(widget.complaintId);
  }

  Future<void> _verify(bool verified) async {
    setState(() => _submittingVerification = true);
    try {
      await _service.verify(widget.complaintId, verified: verified);
      if (!mounted) return;
      setState(() => _future = _service.getDetail(widget.complaintId));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    } finally {
      if (mounted) setState(() => _submittingVerification = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Complaint Detail')),
      body: FutureBuilder<ComplaintDetail>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }
          final c = snapshot.data!;
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(c.complaintNumber, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Wrap(spacing: 8, children: [StatusBadge(status: c.status), SeverityBadge(severity: c.severity)]),
                const SizedBox(height: 16),
                if (c.imageUrl != null)
                  ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: Image.network('${ApiConfig.uploadsBaseUrl}${c.imageUrl}', height: 200, width: double.infinity, fit: BoxFit.cover),
                  ),
                const SizedBox(height: 16),
                Text(c.description),
                const SizedBox(height: 16),
                _infoRow('Category', c.category.name),
                if (c.addressText != null) _infoRow('Address', c.addressText!),
                _infoRow('Reported', DateFormat.yMMMd().add_jm().format(c.createdAt)),
                if (c.deadlineAt != null) _infoRow('Deadline', DateFormat.yMMMd().format(c.deadlineAt!)),
                if (c.escalationLevel > 0) _infoRow('Escalation level', c.escalationLevel.toString()),
                if (c.rejectionReason != null) _infoRow('Rejection reason', c.rejectionReason!),
                if (c.aiCategoryCode != null) _infoRow('AI suggested category', '${c.aiCategoryCode} (${((c.aiConfidence ?? 0) * 100).toStringAsFixed(0)}% confidence)'),
                if (c.status == 'VERIFICATION') ...[
                  const SizedBox(height: 24),
                  const Text('Has this been resolved?', style: TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: FilledButton(
                          onPressed: _submittingVerification ? null : () => _verify(true),
                          child: const Text('Yes, Resolved'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: OutlinedButton(
                          onPressed: _submittingVerification ? null : () => _verify(false),
                          child: const Text('No, Reopen'),
                        ),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(width: 130, child: Text(label, style: const TextStyle(color: Colors.grey))),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}
