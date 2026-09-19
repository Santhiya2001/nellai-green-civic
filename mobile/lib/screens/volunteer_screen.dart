import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../services/volunteer_service.dart';

class VolunteerScreen extends StatefulWidget {
  const VolunteerScreen({super.key});

  @override
  State<VolunteerScreen> createState() => _VolunteerScreenState();
}

class _VolunteerScreenState extends State<VolunteerScreen> {
  final _service = VolunteerService();
  late Future<List<VolunteerEventItem>> _future;

  @override
  void initState() {
    super.initState();
    _future = _service.listEvents();
  }

  Future<void> _register(String eventId) async {
    try {
      await _service.register(eventId);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Registered! See you there.')));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Volunteer Activities')),
      body: FutureBuilder<List<VolunteerEventItem>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          final events = snapshot.data ?? [];
          if (events.isEmpty) {
            return const Center(child: Text('No upcoming events right now.'));
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: events.length,
            separatorBuilder: (context, index) => const SizedBox(height: 12),
            itemBuilder: (context, index) {
              final e = events[index];
              return Card(
                child: ListTile(
                  title: Text(e.title, style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text('${e.activityType.replaceAll('_', ' ')} · ${DateFormat.yMMMd().add_jm().format(e.startAt)}'),
                  trailing: FilledButton(onPressed: () => _register(e.id), child: const Text('Join')),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
