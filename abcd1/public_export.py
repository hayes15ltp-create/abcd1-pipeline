from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def export_observatory_snapshot(conn: sqlite3.Connection, source_project: Path, output_project: Path) -> dict:
    source_project = source_project.resolve()
    output_project = output_project.resolve()
    source_data = json.loads((source_project / "dist/data/project.json").read_text(encoding="utf-8"))

    cohort_rows = conn.execute(
        """
        SELECT COUNT(*) AS count FROM cohorts c
        JOIN cohort_memberships cm ON cm.cohort_id=c.id
        WHERE c.active=1 AND cm.state='included'
        """
    ).fetchone()
    run_rows = conn.execute(
        """
        SELECT COUNT(DISTINCT lr.id) AS count
        FROM logical_runs lr JOIN results r ON r.logical_run_id=lr.id
        WHERE lr.status='succeeded' AND r.status='succeeded' AND r.quality_status='reviewed'
        """
    ).fetchone()

    # The public tracker remains planning-only until a reviewed result exists.
    source_data["cohort"]["imported"] = False
    source_data["cohort"]["variantCount"] = None
    source_data["runs"] = []
    source_data["automation"]["active"] = False
    source_data.setdefault("automation", {})["mode"] = "inactive"

    destination = output_project / "dist/data/project.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(source_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "active_cohort_variants": int(cohort_rows["count"]),
        "reviewed_successful_runs": int(run_rows["count"]),
        "published_runs": 0,
        "path": str(destination),
    }
