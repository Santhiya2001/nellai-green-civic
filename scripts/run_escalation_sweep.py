#!/usr/bin/env python3
"""Run the escalation sweep once. Intended to be invoked on a schedule
(cron, Kubernetes CronJob, etc.) -- every 15-60 minutes is reasonable.

This script must run with the backend's dependencies importable, i.e.
inside the backend container (mounted at /app/scripts, PYTHONPATH=/app):

    docker compose run --rm backend python scripts/run_escalation_sweep.py
"""
import asyncio

from app.db.session import AsyncSessionLocal
from app.services.escalation_engine import run_escalation_sweep


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await run_escalation_sweep(db)
        print(f"Escalation sweep: checked={result['checked']} reminded={result['reminded']} escalated={result['escalated']}")


if __name__ == "__main__":
    asyncio.run(main())
