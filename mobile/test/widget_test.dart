import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:nellai_green_civic/main.dart';

void main() {
  testWidgets('App boots to the splash screen', (WidgetTester tester) async {
    await tester.pumpWidget(const NellaiGreenCivicApp());

    // The splash screen is the initial route while auth state is checked.
    expect(find.text('Nellai Green & Civic'), findsOneWidget);
    expect(find.byIcon(Icons.eco), findsOneWidget);
  });
}
