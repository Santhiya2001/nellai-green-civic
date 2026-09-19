# Green Nellai (Afforestation)

Plantation site mapping, native-species recommendations, tree registration
and survival tracking.

**Important:** `PlantationSite.ownership_status` defaults to `UNVERIFIED`
and the API never sets it to `GOVERNMENT_VERIFIED` automatically -- only an
admin calling `POST /plantation-sites/{id}/verify-ownership` with a
reference to an official document can do that. The platform must never
claim land is government-owned merely from satellite imagery or map data
(spec section 17).

## Own entities

- `PlantationSite` -- candidate/registered planting location, land type,
  ownership status, recommended species, estimated capacity
- `Tree` -- an individual registered tree with species, location, planting
  date, status (`PLANTED` / `HEALTHY` / `NEEDS_MAINTENANCE` / `DAMAGED` /
  `DEAD` / `REPLACED`)
- `TreeMaintenanceLog` -- dated maintenance history per tree

## API (`/api/v1/modules/afforestation/...`)

- `GET /species-recommendations?land_type=...`
- `POST/GET /plantation-sites`, `POST /plantation-sites/{id}/verify-ownership`
- `POST/GET /trees`, `GET /trees/nearby`, `POST /trees/{id}/maintenance`
- `GET /stats/survival-rate`

Category: `FALLEN_TREE` (citizen-reportable hazard, routed through the core
complaint engine -- distinct from the `Tree` registry above, which is for
trees the platform planted/tracks, not hazard reports).
