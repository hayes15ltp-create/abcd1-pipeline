from __future__ import annotations

import argparse
import sqlite3
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from .db import connect

TZ = ZoneInfo("America/New_York")


def register_state(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO scheduler_state(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now')",
        (key, value),
    )
    conn.commit()


def run_bounded_cycle(conn: sqlite3.Connection, max_seconds: int = 300) -> dict:
    started = datetime.now(TZ)
    register_state(conn, "last_cycle_started", started.isoformat())
    register_state(conn, "cycle_status", "running")

    queued = conn.execute("SELECT COUNT(*) AS count FROM logical_runs WHERE status='queued'").fetchone()["count"]
    eligible = conn.execute(
        """
        SELECT COUNT(*) AS count FROM cohorts c
        JOIN cohort_memberships cm ON cm.cohort_id=c.id
        WHERE c.active=1 AND cm.state='included'
        """
    ).fetchone()["count"]
    failed = conn.execute("SELECT COUNT(*) AS count FROM logical_runs WHERE status='failed'").fetchone()["count"]

    actionable = int(queued) > 0 or (int(eligible) > 0 and int(failed) > 0)
    cadence = "hourly" if actionable else "daily"
    register_state(conn, "cadence", cadence)
    register_state(conn, "active", "false")
    register_state(conn, "cycle_status", "idle" if not actionable else "actionable")
    register_state(conn, "last_cycle_finished", datetime.now(TZ).isoformat())
    return {
        "started": started.isoformat(),
        "queued": int(queued),
        "eligible_variants": int(eligible),
        "failed_runs": int(failed),
        "actionable": actionable,
        "cadence": cadence,
        "max_seconds": max_seconds,
        "activated": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/abcd1.sqlite3")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    conn = connect(args.db)
    if args.once:
        print(run_bounded_cycle(conn))
    else:
        raise SystemExit("Persistent scheduler activation requires explicit host configuration and is deliberately not enabled by this starter")
