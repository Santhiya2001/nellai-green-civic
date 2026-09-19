# Android Production Release Checklist

Status key: **Done** = already configured in this repo. **You do** = a step
that needs your own credentials/accounts and can't be done for you.

## Application identity

- **Done** — Package name: `org.nellaigreencivic.nellai_green_civic`
  (`mobile/android/app/build.gradle.kts`).
- **Done** — App display name: "Nellai Green & Civic"
  (`AndroidManifest.xml` `android:label`).
- **You do** — App icon: replace the placeholder icons under
  `mobile/android/app/src/main/res/mipmap-*/ic_launcher.png` with your real
  icon. Easiest path: add `flutter_launcher_icons` as a dev dependency,
  drop a 1024x1024 PNG at `mobile/assets/icon.png`, configure it in
  `pubspec.yaml`, then run `flutter pub run flutter_launcher_icons`.
- **You do** — Splash screen: the default Flutter launch screen is in place
  (`android/app/src/main/res/drawable/launch_background.xml`); customize its
  color/logo, or add `flutter_native_splash` for a themed splash.

## Permissions

- **Done** — `AndroidManifest.xml` requests only `INTERNET`, `CAMERA`,
  `ACCESS_FINE_LOCATION`, `ACCESS_COARSE_LOCATION`, `READ_MEDIA_IMAGES` --
  nothing unused. `LocationService` (`lib/services/location_service.dart`)
  requests location permission just-in-time (when reporting an issue), not
  at launch, and explains why via the OS permission dialog's rationale.

## Signing

- **Done** — `build.gradle.kts` reads a release signing config from
  `android/key.properties` (gitignored) if present, falling back to the
  debug key otherwise so local `flutter run --release` still works.
- **You do**:
  1. Generate a release keystore (do this once, back it up somewhere safe --
     losing it means you can never update the app on Play Store again):
     ```bash
     keytool -genkey -v -keystore ~/nellai-green-civic-release.jks \
       -keyalg RSA -keysize 2048 -validity 10000 -alias nellai-green-civic
     ```
  2. Copy `mobile/android/key.properties.example` to
     `mobile/android/key.properties` and fill in the real values (this file
     is gitignored -- never commit it or the `.jks`).
  3. Build the release bundle:
     ```bash
     cd mobile
     flutter build appbundle --release \
       --dart-define=API_BASE_URL=https://api.yourdomain.org/api/v1
     ```
     The output `.aab` is what you upload to Play Console -- **not** a
     debug/dev API URL. `ApiConfig` (`lib/config/api_config.dart`) defaults
     to the Android emulator's localhost alias specifically so a forgotten
     `--dart-define` fails loudly against `10.0.2.2` in production rather
     than silently working against your laptop.

## Crash reporting

- **You do** — Not wired up yet (avoiding a hard dependency on a specific
  vendor). Firebase Crashlytics or Sentry both work; add the SDK, initialize
  it in `main.dart` before `runApp`, and wrap it around
  `FlutterError.onError` / `PlatformDispatcher.instance.onError`.

## Play Console listing

- **You do** — All of the below require your own Google Play Developer
  account ($25 one-time fee) and can't be done on your behalf:
  - App name, short/full description, screenshots (phone + optional
    tablet), feature graphic
  - **Content rating** questionnaire (this app has no mature content --
    expect an "Everyone" rating)
  - **Data safety** section: declare what's collected --
    - Location (precise): collected, used for app functionality (routing
      complaints), not shared with third parties
    - Photos: collected, used for app functionality (complaint evidence),
      not shared
    - Email/name/phone: collected, used for account functionality, not shared
    - Users can request deletion in-app (Profile -> Delete my account, wired
      to `DELETE /api/v1/users/me`)
  - Privacy policy URL: publish `docs/privacy-policy.md` somewhere public
    (a GitHub Pages page, or your own site) and link it in Play Console --
    Play Store requires a live URL, not a repo file.
  - Upload the `.aab`, complete the release rollout (internal testing track
    first is strongly recommended before production).

## What's deliberately NOT done for you

Publishing to Play Store is an action with real-world consequences (money,
a public listing under your name/organization, a binding developer
agreement) that only you can take with your own Google account. This
checklist gets the app itself to "upload-ready" -- the actual upload and
listing is yours to complete.
