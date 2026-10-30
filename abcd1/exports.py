from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path


def export_cohort(conn: sqlite3.Connection, directory: str | Path) -> dict:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    members = conn.execute(
        """
        SELECT v.immutable_id, v.original_representation, v.hgvs, v.assembly, v.transcript,
               cm.source_classification, cm.row_reference
        FROM cohorts c
        JOIN cohort_memberships cm ON cm.cohort_id=c.id
        JOIN variants v ON v.id=cm.variant_id
        WHERE c.active=1 AND cm.state='included'
        ORDER BY v.hgvs
        """
    ).fetchall()
    rows = [dict(row) for row in members]
    json_path = directory / "cohort.json"
    json_path.write_text(json.dumps({"variants": rows}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    csv_path = directory / "cohort.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[key for key in rows[0]] if rows else [
            "immutable_id", "original_representation", "hgvs", "assembly", "transcript",
            "source_classification", "row_reference"])
        writer.writeheader()
        writer.writerows(rows)
    return {"json": str(json_path), "csv": str(csv_path), "variant_count": len(rows)}
