# Agriculture

Crop disease/pest reporting and farm advisories for the Tirunelveli
agricultural belt.

Categories: `CROP_DISEASE`, `CROP_PEST`.

## Own entities

- `FarmAdvisory` -- published guidance for a crop, optionally scoped to a
  region
- `CropReport` -- a farmer's report of a crop issue, with an AI diagnosis
  suggestion from the shared AI service (same `/classify` contract used by
  the core complaint engine)

## API (`/api/v1/modules/agriculture/...`)

- `POST/GET /advisories`
- `POST/GET /crop-reports`

This module deliberately reuses the AI service's text classifier for
`ai_diagnosis` rather than shipping a separate crop-disease model -- a
real crop-disease vision model (e.g. fine-tuned on PlantVillage-style data)
is a natural community contribution: add it as a new endpoint in `ai/` and
call it from here instead.
