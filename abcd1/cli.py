from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from .cohort import import_snapshot
from .db import connect
from .exports import export_cohort
from .runs import complete_run, schedule_run
from .recovery import retry_failed, reconcile_abandoned


def main() -> None:
    parser = argparse.ArgumentParser(prog="abcd1")
    parser.add_argument("--db", default="data/abcd1.sqlite3")
    sub = parser.add_subparsers(dest="command", required=True)

    imp = sub.add_parser("import-cohort")
    imp.add_argument("source")
    imp.add_argument("--date")
    imp.add_argument("--release")
    imp.add_argument("--no-activate", action="store_true")

    exp = sub.add_parser("export-cohort")
    exp.add_argument("directory")

    schedule = sub.add_parser("schedule")
    schedule.add_argument("spec_json")

    complete = sub.add_parser("complete")
    complete.add_argument("run_id", type=int)
    complete.add_argument("status", choices=["succeeded", "failed", "inconclusive"])
    complete.add_argument("--payload", default="{}")
    complete.add_argument("--artifact")

    retry = sub.add_parser("retry")
    retry.add_argument("run_id", type=int)
    retry.add_argument("--reason", default="manual retry")

    reconcile = sub.add_parser("reconcile")
    reconcile.add_argument("run_id", type=int)
    reconcile.add_argument("--reason", default="host restart recovery")

    backup = sub.add_parser("backup")
    backup.add_argument("destination")

    fetch = sub.add_parser("fetch-registry")
    fetch.add_argument("destination")

    public = sub.add_parser("export-public")
    public.add_argument("source_project")
    public.add_argument("output_project")

    sub.add_parser("members")
    args = parser.parse_args()

    conn = connect(args.db)
    if args.command == "import-cohort":
        print(json.dumps(import_snapshot(conn, args.source, args.date, args.release, not args.no_activate), indent=2))
    elif args.command == "export-cohort":
        print(json.dumps(export_cohort(conn, args.directory), indent=2))
    elif args.command == "schedule":
        print(json.dumps(schedule_run(conn, json.loads(args.spec_json)), indent=2))
    elif args.command == "complete":
        complete_run(conn, args.run_id, args.status, json.loads(args.payload), args.artifact)
        print(json.dumps({"logical_run_id": args.run_id, "status": args.status}))
    elif args.command == "retry":
        print(json.dumps({"new_logical_run_id": retry_failed(conn, args.run_id, args.reason)}))
    elif args.command == "reconcile":
        print(json.dumps({"new_logical_run_id": reconcile_abandoned(conn, args.run_id, args.reason)}))
    elif args.command == "backup":
        import sqlite3
        destination = Path(args.destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        source = sqlite3.connect(args.db)
        target = sqlite3.connect(destination)
        source.backup(target)
        source.close()
        target.close()
        print(json.dumps({"backup": str(destination)}))
    elif args.command == "fetch-registry":
        from .registry import fetch_registry_snapshot
        print(json.dumps(fetch_registry_snapshot(args.destination), indent=2))
    elif args.command == "export-public":
        from .public_export import export_observatory_snapshot
        print(json.dumps(export_observatory_snapshot(conn, Path(args.source_project), Path(args.output_project)), indent=2))
    elif args.command == "members":
        rows = conn.execute(
            """
            SELECT v.hgvs, v.assembly, v.transcript, cm.source_classification, cm.row_reference
            FROM cohorts c
            JOIN cohort_memberships cm ON cm.cohort_id=c.id
            JOIN variants v ON v.id=cm.variant_id
            WHERE c.active=1 AND cm.state='included'
            ORDER BY v.hgvs
            """
        ).fetchall()
        print(json.dumps([dict(row) for row in rows], indent=2))
    conn.close()
