# Biodiversity

Species catalog and citizen-submitted sighting observations for
Tirunelveli's flora and fauna.

Categories: `WILDLIFE_SIGHTING`, `HABITAT_DAMAGE` (routed through the core
complaint engine, for reportable problems -- distinct from the sighting
log below, which is citizen-science data collection, not a complaint).

## Own entities

- `Species` -- reference catalog (common/scientific name, category,
  conservation status)
- `BiodiversityObservation` -- a dated sighting, optionally linked to a
  catalog species or a free-text name, with an admin-verifiable flag

## API (`/api/v1/modules/biodiversity/...`)

- `POST/GET /species`
- `POST /observations`, `GET /observations/nearby`,
  `POST /observations/{id}/verify`

A "school environmental monitoring" community module (spec section 40)
could reuse this module's `Species` catalog and observation pattern
directly rather than duplicating it.
