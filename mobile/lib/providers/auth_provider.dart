import 'package:flutter/foundation.dart';

import '../models/user.dart';
import '../services/auth_service.dart';

enum AuthStatus { unknown, authenticated, unauthenticated }

class AuthProvider extends ChangeNotifier {
  final _authService = AuthService();

  AuthStatus status = AuthStatus.unknown;
  AppUser? user;
  String? lastError;

  Future<void> bootstrap() async {
    if (await _authService.isLoggedIn()) {
      try {
        user = await _authService.me();
        status = AuthStatus.authenticated;
      } catch (_) {
        status = AuthStatus.unauthenticated;
      }
    } else {
      status = AuthStatus.unauthenticated;
    }
    notifyListeners();
  }

  Future<bool> login(String email, String password) async {
    lastError = null;
    try {
      await _authService.login(email, password);
      user = await _authService.me();
      status = AuthStatus.authenticated;
      notifyListeners();
      return true;
    } catch (e) {
      lastError = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> register({required String fullName, required String email, String? phone, required String password}) async {
    lastError = null;
    try {
      await _authService.register(fullName: fullName, email: email, phone: phone, password: password);
      user = await _authService.me();
      status = AuthStatus.authenticated;
      notifyListeners();
      return true;
    } catch (e) {
      lastError = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    await _authService.logout();
    user = null;
    status = AuthStatus.unauthenticated;
    notifyListeners();
  }

  Future<void> deleteAccount() async {
    await _authService.deleteAccount();
    user = null;
    status = AuthStatus.unauthenticated;
    notifyListeners();
  }

  bool hasRole(String role) => user?.hasRole(role) ?? false;
}
