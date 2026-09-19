# Civic Issue Reporting

Categories: `ROAD_DAMAGE`, `STREETLIGHT_PROBLEM`, `PUBLIC_TOILET_ISSUE`, `OTHER`.

This module has no backend code of its own -- it registers categories onto
the core complaint engine (`backend/app/api/v1/complaints.py`) and relies
entirely on the existing `/api/v1/complaints` endpoints. It exists as the
simplest possible example of "a module that's just categories" (compare to
`modules/water/` for a module with its own entities and routes).

No `backend/router.py` -- nothing to mount beyond the shared complaint API.
