import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/complaint.dart';
import '../services/complaint_service.dart';
import '../widgets/badges.dart';
import 'complaint_detail_screen.dart';

class MyComplaintsScreen extends StatefulWidget {
  const MyComplaintsScreen({super.key});

  @override
  State<MyComplaintsScreen> createState() => _MyComplaintsScreenState();
}

class _MyComplaintsScreenState extends State<MyComplaintsScreen> {
  final _service = ComplaintService();
  late Future<List<ComplaintListItem>> _future;

  @override
  void initState() {
    super.initState();
    _future = _service.myComplaints();
  }

  Future<void> _refresh() async {
    setState(() => _future = _service.myComplaints());
    await _future;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Complaints')),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: FutureBuilder<List<ComplaintListItem>>(
          future: _future,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return ListView(children: [Padding(padding: const EdgeInsets.all(24), child: Text('Error: ${snapshot.error}'))]);
            }
            final complaints = snapshot.data ?? [];
            if (complaints.isEmpty) {
              return ListView(children: const [Padding(padding: EdgeInsets.all(24), child: Text('No complaints yet. Tap Report to file your first one.'))]);
            }
            return ListView.separated(
              itemCount: complaints.length,
              separatorBuilder: (context, index) => const Divider(height: 1),
              itemBuilder: (context, index) {
                final c = complaints[index];
                return ListTile(
                  title: Text(c.complaintNumber, style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text('${c.categoryCode} · ${DateFormat.yMMMd().format(c.createdAt)}'),
                  trailing: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      StatusBadge(status: c.status),
                      const SizedBox(height: 4),
                      SeverityBadge(severity: c.severity),
                    ],
                  ),
                  onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => ComplaintDetailScreen(complaintId: c.id))).then((_) => _refresh()),
                );
              },
            );
          },
        ),
      ),
    );
  }
}
