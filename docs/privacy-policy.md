# Privacy Policy

_Template for the Nellai Green & Civic platform. A production deployment
should have this reviewed by someone qualified to advise on applicable law
(e.g. India's DPDP Act) before publishing it as a live policy — this is a
starting point, not legal advice._

**Last updated:** 2026-09-18

## What we collect

| Data | Why | Where it's stored |
|---|---|---|
| Name, email, phone (optional) | Account identity, so we know who filed a report | `users` table |
| Password | Authentication (stored as a bcrypt hash, never plain text) | `users.password_hash` |
| GPS location, per complaint | Route the report to the right authority and place it on the map | `complaints.location` (PostGIS point) |
| Photo, per complaint (optional) | Evidence for the authority resolving it | Local disk or S3-compatible storage (`STORAGE_BACKEND`) |
| Complaint description | The report itself | `complaints.description` |

## Who sees it

- **Assigned authority**: sees the complaint (location, photo, description)
  needed to resolve it, and the reporting citizen's name is visible to them
  in the same way a paper complaint would be.
- **Administrators**: can see all complaints for platform operation.
- **Other citizens**: see complaints on the public map (location, category,
  status) **without** the reporter's name, email, or phone. The public map
  view never exposes personal contact information (spec section 29).
- **Nobody else.** We do not sell or share this data with third parties.
  The AI classification service (`ai/`) receives only the description text
  and a reference to the image for the purpose of suggesting a category --
  it does not receive the reporter's identity.

## How long we keep it

- Active account data: kept while your account is active.
- Complaint records: retained indefinitely as a civic record (this is the
  point of the platform -- a historical record of issues and resolutions
  for a locality), but de-identified on request (see Account Deletion).
- Refresh tokens: expire automatically (`REFRESH_TOKEN_EXPIRE_DAYS`,
  default 14 days) and are revocable.

## Your controls

- **Account deletion**: `DELETE /api/v1/users/me` (also available from the
  web app's Profile menu and the mobile app's Profile tab) deactivates your
  account and replaces your name/email/phone with de-identified
  placeholders. Complaints you filed remain in the system (as public civic
  record) but are no longer linked to your personal details.
- **Data export**: not yet implemented as a self-service feature; contact
  the platform administrator for a copy of your data.

## Location data specifically

Location is captured only when you actively report an issue or use the
"nearby issues" feature (which asks for your position once, not
continuously). The app does not track your location in the background.

## Children's privacy

This platform is intended for general civic use and is not directed at
children under 13. We do not knowingly collect data from children under 13.

## Changes to this policy

Material changes will be reflected in this file's "Last updated" date and,
for the hosted deployment, communicated via an in-app notification.

## Contact

See the repository's `SECURITY.md` / maintainer contact information for how
to reach the platform operator with a privacy question or data request.
