#!/bin/sh
# Production container entrypoint: migrate, seed, then serve. A real shell
# script (not an inline "sh -c ..." string) because not every host that
# runs this Docker image wraps its command override in a shell -- Render's
# dockerCommand field, for one, execs the given string as a literal
# argv[0] rather than passing it through /bin/sh.
set -e

alembic upgrade head
python -m app.db.seed
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
