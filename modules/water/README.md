# Neervalam (Water Resources)

Tracks the Tamirabharani river, lakes, ponds, canals, wells and tanks
around Tirunelveli, and lets citizens log environmental observations
against them (pollution, garbage, encroachment, blockage, illegal dumping,
low water level, damage).

Categories: `LAKE_POLLUTION`, `RIVER_POLLUTION`, `CANAL_BLOCKAGE`,
`WATER_BODY_ENCROACHMENT`, `REDUCED_WATER_LEVEL` (routed through the core
complaint engine same as any other category).

## Own entities

- `WaterBody` -- name, type, geometry (point or polygon), optional capacity
- `WaterObservation` -- a dated observation against a water body, with an
  optional water-level reading and photo

## API (`/api/v1/modules/water/...`)

- `POST/GET /water-bodies`, `GET /water-bodies/nearby`
- `POST /observations`, `GET /water-bodies/{id}/observations`

See `backend/router.py` for the full request/response shapes -- a good
reference implementation for a module with its own PostGIS-backed entities.

## Future integration

IoT water-level sensors: `WaterObservation.water_level_meters` is already
the field a sensor feed would populate; a sensor-ingest module could POST
to `/observations` on a schedule using a service account instead of a
citizen's token.
