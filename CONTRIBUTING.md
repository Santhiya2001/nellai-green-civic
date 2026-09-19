# Contributing to Nellai Green & Civic

Thank you for considering a contribution. This project exists to become a
community-maintained civic/environmental platform, not a closed application
— your module, bug fix, or doc improvement is exactly the kind of thing it's
built to support.

## Ground rules

- Be respectful — see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
- Open an issue before starting large or architectural changes, so we can
  agree on direction before you invest time.
- Small fixes (typos, obvious bugs, doc corrections) can go straight to a PR.

## Development workflow

1. Fork the repo, create a branch: `git checkout -b feature/my-change`.
2. `cp .env.example .env` and follow [docs/installation.md](docs/installation.md).
3. Make your change. If it's a new module, follow
   [docs/module-development.md](docs/module-development.md).
4. Add/update tests. Run them:
   ```bash
   docker compose run --rm backend pytest
   ```
5. Commit with a clear message explaining *why*, not just *what*.
6. Push and open a PR against `main`. Fill in the PR template (what changed,
   why, how you tested it).

## What CI checks

`.github/workflows/ci.yml` runs on every PR:

- Backend lint + `pytest`
- Web build + lint
- Every `modules/*/module.json` validated against the required schema

A PR with failing CI will not be merged.

## Code style

- Python: standard library typing, no unused abstractions, docstrings only
  where the *why* isn't obvious from the code.
- TypeScript/React: functional components, explicit prop types, no
  unnecessary state libraries — this project intentionally avoids adding a
  dependency where `useState`/`useEffect` + the existing `AuthContext`
  already does the job.

## Submitting a new module

New modules are the easiest, highest-leverage contribution. A working
example that touches core tables, its own tables, GIS, and file upload is
`modules/water/` — read it before starting your own.

## Questions

Open a GitHub issue with the `question` label.
