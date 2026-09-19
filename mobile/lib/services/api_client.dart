import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import 'token_store.dart';

class ApiException implements Exception {
  final int statusCode;
  final String message;
  ApiException(this.statusCode, this.message);

  @override
  String toString() => message;
}

/// Thin REST client: attaches the bearer token, retries once with a
/// refreshed access token on a 401, and surfaces backend error `detail`
/// messages instead of raw exceptions.
class ApiClient {
  ApiClient._();
  static final ApiClient instance = ApiClient._();

  Uri _uri(String path, [Map<String, dynamic>? query]) {
    final normalized = path.startsWith('/') ? path : '/$path';
    final base = Uri.parse(ApiConfig.baseUrl);
    return base.replace(
      path: base.path + normalized,
      queryParameters: query?.map((k, v) => MapEntry(k, v.toString())),
    );
  }

  Future<Map<String, String>> _headers({bool json = true}) async {
    final token = await TokenStore.instance.accessToken;
    return {
      if (json) 'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Future<bool> _tryRefresh() async {
    final refreshToken = await TokenStore.instance.refreshToken;
    if (refreshToken == null) return false;
    final response = await http.post(
      _uri('/auth/refresh'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'refresh_token': refreshToken}),
    );
    if (response.statusCode != 200) return false;
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    await TokenStore.instance.save(accessToken: data['access_token'], refreshToken: data['refresh_token']);
    return true;
  }

  dynamic _decode(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isEmpty) return null;
      return jsonDecode(response.body);
    }
    String message = 'Request failed (${response.statusCode})';
    try {
      final body = jsonDecode(response.body);
      if (body is Map && body['detail'] != null) message = body['detail'].toString();
    } catch (_) {
      // Non-JSON error body -- keep the generic message.
    }
    throw ApiException(response.statusCode, message);
  }

  Future<dynamic> get(String path, {Map<String, dynamic>? query}) async {
    var response = await http.get(_uri(path, query), headers: await _headers());
    if (response.statusCode == 401 && await _tryRefresh()) {
      response = await http.get(_uri(path, query), headers: await _headers());
    }
    return _decode(response);
  }

  Future<dynamic> delete(String path) async {
    var response = await http.delete(_uri(path), headers: await _headers());
    if (response.statusCode == 401 && await _tryRefresh()) {
      response = await http.delete(_uri(path), headers: await _headers());
    }
    return _decode(response);
  }

  Future<dynamic> post(String path, {Map<String, dynamic>? body}) async {
    var response = await http.post(_uri(path), headers: await _headers(), body: body != null ? jsonEncode(body) : null);
    if (response.statusCode == 401 && await _tryRefresh()) {
      response = await http.post(_uri(path), headers: await _headers(), body: body != null ? jsonEncode(body) : null);
    }
    return _decode(response);
  }

  /// multipart/form-data POST, used for complaint creation (image upload).
  Future<dynamic> postMultipart(
    String path, {
    required Map<String, String> fields,
    File? file,
    String fileField = 'image',
  }) async {
    Future<http.StreamedResponse> send() async {
      final request = http.MultipartRequest('POST', _uri(path));
      request.headers.addAll(await _headers(json: false));
      request.fields.addAll(fields);
      if (file != null) {
        request.files.add(await http.MultipartFile.fromPath(fileField, file.path));
      }
      return request.send();
    }

    var streamed = await send();
    if (streamed.statusCode == 401 && await _tryRefresh()) {
      streamed = await send();
    }
    final response = await http.Response.fromStream(streamed);
    return _decode(response);
  }
}
