import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import 'login_screen.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final user = auth.user;
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          CircleAvatar(radius: 36, backgroundColor: const Color(0xFF1A7A4C), child: Text(user?.fullName.substring(0, 1).toUpperCase() ?? '?', style: const TextStyle(fontSize: 28, color: Colors.white))),
          const SizedBox(height: 16),
          Text(user?.fullName ?? '', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
          Text(user?.email ?? '', textAlign: TextAlign.center, style: const TextStyle(color: Colors.grey)),
          if (user?.phone != null) Text(user!.phone!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.grey)),
          const SizedBox(height: 8),
          Center(child: Wrap(spacing: 6, children: [for (final r in user?.roles ?? []) Chip(label: Text(r))])),
          const SizedBox(height: 32),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.privacy_tip_outlined),
            title: const Text('Privacy Policy'),
            onTap: () => showDialog(
              context: context,
              builder: (_) => AlertDialog(
                title: const Text('Privacy Policy'),
                content: const SingleChildScrollView(
                  child: Text(
                    'Nellai Green & Civic collects your name, email/phone, and, '
                    'for each complaint you file, a GPS location and optional '
                    'photo. This data is used only to route and track your '
                    'reports and is visible to the assigned authority and '
                    'platform administrators -- never made public with your '
                    'personal details attached. You can delete your account '
                    'at any time from this screen. Full policy: '
                    'docs/privacy-policy.md in the project repository.',
                  ),
                ),
                actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close'))],
              ),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.delete_outline, color: Colors.red),
            title: const Text('Delete my account', style: TextStyle(color: Colors.red)),
            onTap: () => _confirmDeleteAccount(context, auth),
          ),
          ListTile(
            leading: const Icon(Icons.logout),
            title: const Text('Logout'),
            onTap: () async {
              await auth.logout();
              if (context.mounted) {
                Navigator.of(context).pushAndRemoveUntil(MaterialPageRoute(builder: (_) => const LoginScreen()), (route) => false);
              }
            },
          ),
        ],
      ),
    );
  }

  void _confirmDeleteAccount(BuildContext context, AuthProvider auth) {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Delete account?'),
        content: const Text('This deactivates your account and removes your personal details. Your complaint history is retained for civic record-keeping but de-identified. This cannot be undone.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')),
          TextButton(
            onPressed: () async {
              Navigator.pop(dialogContext);
              await auth.deleteAccount();
              if (context.mounted) {
                Navigator.of(context).pushAndRemoveUntil(MaterialPageRoute(builder: (_) => const LoginScreen()), (route) => false);
              }
            },
            child: const Text('Delete', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}
