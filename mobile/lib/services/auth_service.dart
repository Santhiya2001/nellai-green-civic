import '../models/user.dart';
import 'api_client.dart';
import 'token_store.dart';

class AuthService {
  final _api = ApiClient.instance;

  Future<void> login(String email, String password) async {
    final data = await _api.post('/auth/login', body: {'email': email, 'password': password});
    await TokenStore.instance.save(accessToken: data['access_token'], refreshToken: data['refresh_token']);
  }

  Future<void> register({
    required String fullName,
    required String email,
    String? phone,
    required String password,
  }) async {
    await _api.post('/auth/register', body: {
      'full_name': fullName,
      'email': email,
      'phone': phone,
      'password': password,
    });
    await login(email, password);
  }

  Future<AppUser> me() async {
    final data = await _api.get('/auth/me');
    return AppUser.fromJson(data as Map<String, dynamic>);
  }

  Future<void> logout() async {
    await TokenStore.instance.clear();
  }

  Future<void> deleteAccount() async {
    await _api.delete('/users/me');
    await TokenStore.instance.clear();
  }

  Future<bool> isLoggedIn() async {
    return await TokenStore.instance.accessToken != null;
  }
}
