# Volunteer Nellai

Volunteer profiles and event scheduling/registration for tree planting,
drain cleaning, lake restoration, waste cleanup, awareness campaigns and
biodiversity surveys.

## Own entities

- `VolunteerProfile` -- skills, interests, preferred activity types,
  location, availability (one per user)
- `VolunteerEvent` -- a scheduled activity with location, time window,
  optional capacity
- `VolunteerEventRegistration` -- a user's registration for an event

## API (`/api/v1/modules/volunteer/...`)

- `PUT /profile`
- `POST/GET /events`, `GET /events/recommended`, `GET /events/nearby`
- `POST /events/{id}/register`

`/events/recommended` is a simple content-based match: it ranks upcoming
events by whether their `activity_type` is in the caller's
`preferred_activities`. Replacing this with a smarter recommender (e.g.
factoring in past attendance or location proximity) is a good first
contribution if you want one.
