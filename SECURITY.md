# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Nellai Green & Civic, please
**do not** open a public GitHub issue. Instead:

1. Open a private security advisory via GitHub ("Security" tab -> "Report a
   vulnerability") on this repository, or
2. Email the maintainers listed in the repository's contact information.

Please include:

- A description of the vulnerability and its impact
- Steps to reproduce (a minimal repro is ideal)
- Any suggested fix, if you have one

We aim to acknowledge reports within 5 business days and to release a fix
or mitigation plan within 30 days for confirmed high-severity issues.

## Supported Versions

Only the `main` branch / latest tagged release receives security fixes.

## Scope

In scope: the backend API, AI service, web app, mobile app, and the core
module loading mechanism. A vulnerability in a community-contributed module
under `/modules` should still be reported here — we'll route it to that
module's listed author/maintainer.

## See Also

[docs/security.md](docs/security.md) documents the current security
implementation (authentication, input validation, rate limiting, known
gaps) for anyone auditing the codebase.
