import 'api_client.dart';

class VolunteerEventItem {
  final String id;
  final String title;
  final String activityType;
  final DateTime startAt;

  VolunteerEventItem({required this.id, required this.title, required this.activityType, required this.startAt});

  factory VolunteerEventItem.fromJson(Map<String, dynamic> json) {
    return VolunteerEventItem(
      id: json['id'] as String,
      title: json['title'] as String,
      activityType: json['activity_type'] as String,
      startAt: DateTime.parse(json['start_at'] as String),
    );
  }
}

class VolunteerService {
  final _api = ApiClient.instance;

  Future<List<VolunteerEventItem>> listEvents() async {
    final data = await _api.get('/modules/volunteer/events') as List;
    return data.map((e) => VolunteerEventItem.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<void> register(String eventId) async {
    await _api.post('/modules/volunteer/events/$eventId/register');
  }
}
