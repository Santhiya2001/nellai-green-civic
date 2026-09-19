import '../models/notification_item.dart';
import 'api_client.dart';

class AppNotificationService {
  final _api = ApiClient.instance;

  Future<List<NotificationItem>> list() async {
    final data = await _api.get('/notifications') as List;
    return data.map((e) => NotificationItem.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<void> markRead(String id) async {
    await _api.post('/notifications/$id/read');
  }
}
