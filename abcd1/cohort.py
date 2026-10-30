from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from datetime import date
from pathlib import Path
from typing import Iterable

SOURCE_URL = "https://adrenoleukodystrophy.info/mutations-and-variants-in-abcd1"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_snapshot(
    conn: sqlite3.Connection,
    source_path: str | Path,
    snapshot_date: str | None = None,
    registry_release: str | None = None,
    activate: bool = True,
) -> dict:
    source_path = Path(source_path)
    source_bytes = source_path.read_bytes()
    digest = hashlib.sha256(source_bytes).hexdigest()
    snapshot_date = snapshot_date or date.today().isoformat()

    suffix = source_path.suffix.lower()
    if suffix == ".json":
        payload = json.loads(source_bytes)
        rows = payload if isinstance(payload, list) else payload["variants"]
    elif suffix == ".csv":
        with source_path.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
    else:
        raise ValueError("Snapshot must be JSON or CSV")

    cur = conn.execute(
        "INSERT INTO cohorts(name, source_url, snapshot_date, source_sha256, registry_release, active) VALUES(?,?,?,?,?,0)",
        ("ABCD1 registry snapshot", SOURCE_URL, snapshot_date, digest, registry_release),
    )
    cohort_id = int(cur.lastrowid)
    counts = {"included": 0, "excluded": 0, "held": 0}
    exclusion_reasons: dict[str, int] = {}

    required_columns = {"hgvs"}
    for row in rows:
        normalized = {str(k).strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
        if "source_classification" in normalized:
            classification = normalized.get("source_classification")
        else:
            classification = normalized.get("classification")
        hgvs = normalized.get("hgvs") or normalized.get("HGVS")
        if not hgvs:
            counts["held"] += 1
            exclusion_reasons["missing_hgvs"] = exclusion_reasons.get("missing_hgvs", 0) + 1
            continue

        original = normalized.get("original_representation") or hgvs
        immutable_id = normalized.get("immutable_id") or normalized.get("source_record_id") or normalized.get("source_id") or f"registry:{hgvs}"
        assembly = normalized.get("assembly") or "GRCh37"
        transcript = normalized.get("transcript") or "NM_000033.3"
        row_reference = normalized.get("row_reference") or str(normalized.get("source_record_id") or normalized.get("source_id") or "")

        cur = conn.execute(
            "SELECT id FROM variants WHERE immutable_id=?",
            (immutable_id,),
        )
        existing = cur.fetchone()
        if existing:
            variant_id = int(existing["id"])
        else:
            cur = conn.execute(
                "INSERT INTO variants(immutable_id, original_representation, hgvs, assembly, transcript, source_record_id, source_url) VALUES(?,?,?,?,?,?,?)",
                (immutable_id, original, hgvs, assembly, transcript, row_reference, SOURCE_URL),
            )
            variant_id = int(cur.lastrowid)

        if classification == "Pathogenic":
            state = "included"
            counts["included"] += 1
            excluded_reason = None
        elif classification in {"Likely pathogenic", "NBS-associated", "VUS", "Likely benign", "Benign"}:
            state = "excluded"
            counts["excluded"] += 1
            excluded_reason = classification
            exclusion_reasons[classification] = exclusion_reasons.get(classification, 0) + 1
        else:
            state = "held"
            counts["held"] += 1
            excluded_reason = "missing_or_unresolved_classification"
            exclusion_reasons["missing_or_unresolved_classification"] = exclusion_reasons.get("missing_or_unresolved_classification", 0) + 1

        conn.execute(
            "INSERT OR REPLACE INTO cohort_memberships(cohort_id, variant_id, source_classification, state, row_reference, excluded_reason) VALUES(?,?,?,?,?,?)",
            (cohort_id, variant_id, classification or "missing_or_unresolved_classification", state, row_reference, excluded_reason),
        )

    if activate:
        conn.execute("UPDATE cohorts SET active=0 WHERE id<>?", (cohort_id,))
        conn.execute("UPDATE cohorts SET active=1 WHERE id=?", (cohort_id,))
    conn.commit()
    return {
        "cohort_id": cohort_id,
        "snapshot_date": snapshot_date,
        "source_sha256": digest,
        "counts": counts,
        "exclusion_reasons": exclusion_reasons,
    }


def active_members(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(
        conn.execute(
            """
            SELECT v.*, cm.cohort_id, cm.source_classification, cm.row_reference
            FROM cohorts c
            JOIN cohort_memberships cm ON cm.cohort_id=c.id
            JOIN variants v ON v.id=cm.variant_id
            WHERE c.active=1 AND cm.state='included'
            ORDER BY v.hgvs
            """
        )
    )
