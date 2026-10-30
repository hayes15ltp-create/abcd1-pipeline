from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any


def canonical_fingerprint(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def schedule_run(conn: sqlite3.Connection, spec: dict[str, Any], reason: str = "initial submission") -> dict[str, Any]:
    active = conn.execute(
        "SELECT id FROM cohorts WHERE active=1"
    ).fetchone()
    if not active:
        raise ValueError("No active cohort snapshot")
    cohort_id = int(active["id"])
    variant = conn.execute(
        """
        SELECT v.id FROM variants v
        JOIN cohort_memberships cm ON cm.variant_id=v.id
        WHERE cm.cohort_id=? AND cm.state='included' AND v.immutable_id=? 
        """,
        (cohort_id, spec["immutable_id"]),
    ).fetchone()
    if not variant:
        raise ValueError("Variant is not an active Pathogenic cohort member")

    canonical_payload = dict(spec)
    canonical_payload["cohort_id"] = cohort_id
    canonical = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    fingerprint = canonical_fingerprint(canonical_payload)

    conn.execute("BEGIN IMMEDIATE")
    try:
        question_id = spec["question_id"]
        conn.execute(
            "INSERT OR IGNORE INTO research_questions(id, question, endpoint, phenotype) VALUES(?,?,?,?)",
            (question_id, spec.get("question", question_id), spec.get("endpoint"), spec.get("phenotype")),
        )
        row = conn.execute(
            "SELECT rs.id FROM run_specs rs WHERE rs.fingerprint=?",
            (fingerprint,),
        ).fetchone()
        if row:
            spec_id = int(row["id"])
        else:
            cur = conn.execute(
                """
                INSERT INTO run_specs(fingerprint, cohort_id, question_id, subject_variant_id, method_id,
                  tool_name, tool_version, model_checkpoint, dataset_snapshot, dataset_sha256,
                  assembly, transcript, biological_context, parameters, code_revision, canonical_json)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    fingerprint, cohort_id, question_id, int(variant["id"]), spec.get("method_id"),
                    spec["tool_name"], spec["tool_version"], spec.get("model_checkpoint"),
                    spec.get("dataset_snapshot"), spec.get("dataset_sha256"), spec.get("assembly"),
                    spec.get("transcript"), spec.get("biological_context"),
                    json.dumps(spec.get("parameters", {}), sort_keys=True),
                    spec.get("code_revision"), canonical,
                ),
            )
            spec_id = int(cur.lastrowid)

        existing = conn.execute(
            """
            SELECT lr.id, lr.status FROM logical_runs lr
            JOIN run_specs rs ON rs.id=lr.spec_id
            WHERE lr.spec_id=? AND lr.status IN ('queued','running')
            ORDER BY lr.id DESC LIMIT 1
            """,
            (spec_id,),
        ).fetchone()
        if existing:
            conn.commit()
            return {"status": "deduplicated", "logical_run_id": int(existing["id"]), "fingerprint": fingerprint}

        successful_candidates = conn.execute(
            """
            SELECT lr.id, r.artifact_path, r.artifact_sha256 FROM logical_runs lr
            JOIN results r ON r.logical_run_id=lr.id
            WHERE lr.spec_id=? AND lr.status='succeeded' AND r.status='succeeded' AND r.quality_status='reviewed'
            ORDER BY lr.id DESC LIMIT 1
            """,
            (spec_id,),
        ).fetchall()
        successful = None
        for candidate in successful_candidates:
            if _result_artifacts_usable(candidate):
                successful = candidate
                break
        if successful:
            max_attempt = conn.execute(
                "SELECT COALESCE(MAX(attempt), 0) AS max_attempt FROM logical_runs WHERE spec_id=?",
                (spec_id,),
            ).fetchone()["max_attempt"]
            cur = conn.execute(
                "INSERT INTO logical_runs(spec_id, status, reason, attempt) VALUES(?,?,?,?)",
                (spec_id, "succeeded", "reuse event; evidence retained from the original logical run", int(max_attempt) + 1),
            )
            requested_id = int(cur.lastrowid)
            conn.execute(
                "INSERT INTO reuse_events(requested_run_id, reused_run_id) VALUES(?,?)",
                (requested_id, int(successful["id"])),
            )
            conn.commit()
            return {
                "status": "reuse",
                "logical_run_id": requested_id,
                "reused_run_id": int(successful["id"]),
                "fingerprint": fingerprint,
            }

        cur = conn.execute(
            "INSERT INTO logical_runs(spec_id, status, reason, attempt) VALUES(?,?,?,1)",
            (spec_id, "queued", reason),
        )
        logical_run_id = int(cur.lastrowid)
        conn.commit()
        return {"status": "scheduled", "logical_run_id": logical_run_id, "fingerprint": fingerprint}
    except Exception:
        conn.rollback()
        raise


def complete_run(conn: sqlite3.Connection, logical_run_id: int, status: str, payload: dict, artifact_path: str | None = None) -> None:
    if status not in accepted_statuses():
        raise ValueError("Invalid result status")
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute(
            "UPDATE logical_runs SET status=?, finished_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?",
            ("succeeded" if status == "succeeded" else "failed", logical_run_id),
        )
        digest = None
        if artifact_path:
            path = Path(artifact_path)
            if path.is_file():
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
        conn.execute(
            "INSERT INTO results(logical_run_id, status, payload, artifact_path, artifact_sha256) VALUES(?,?,?,?,?)",
            (logical_run_id, status, json.dumps(payload, sort_keys=True), artifact_path, digest),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def accepted_statuses() -> tuple[str, ...]:
    return ("succeeded", "failed", "inconclusive")


def _result_artifacts_usable(row: sqlite3.Row) -> bool:
    artifact_path = row["artifact_path"]
    expected = row["artifact_sha256"]
    if not artifact_path:
        return True
    path = Path(artifact_path)
    if not path.is_file() or not expected:
        return False
    return hashlib.sha256(path.read_bytes()).hexdigest() == expected
