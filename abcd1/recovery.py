from __future__ import annotations

import sqlite3


def retry_failed(conn: sqlite3.Connection, logical_run_id: int, reason: str) -> int:
    original = conn.execute(
        "SELECT spec_id, attempt FROM logical_runs WHERE id=?",
        (logical_run_id,),
    ).fetchone()
    if not original:
        raise ValueError("Logical run not found")
    if original["attempt"] >= 100:
        raise ValueError("Maximum retry limit reached")
    cur = conn.execute(
        "INSERT INTO logical_runs(spec_id, status, reason, attempt) VALUES(?,?,?,?)",
        (int(original["spec_id"]), "queued", reason, int(original["attempt"]) + 1),
    )
    conn.commit()
    return int(cur.lastrowid)


def reconcile_abandoned(conn: sqlite3.Connection, logical_run_id: int, reason: str = "host restart recovery") -> int | None:
    run = conn.execute(
        "SELECT spec_id, attempt FROM logical_runs WHERE id=? AND status IN ('queued','running')",
        (logical_run_id,),
    ).fetchone()
    if not run:
        return None
    conn.execute(
        "UPDATE logical_runs SET status='abandoned', reason=?, finished_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?",
        (reason, logical_run_id),
    )
    conn.commit()
    return retry_failed(conn, logical_run_id, "retry after crash reconciliation")


def stale_artifact(conn: sqlite3.Connection, logical_run_id: int) -> bool:
    result = conn.execute(
        "SELECT artifact_path, artifact_sha256 FROM results WHERE logical_run_id=? ORDER BY id DESC LIMIT 1",
        (logical_run_id,),
    ).fetchone()
    if not result or not result["artifact_path"]:
        return False
    return not _artifact_unchanged(str(result["artifact_path"]), str(result["artifact_sha256"]))


def _artifact_unchanged(path: str, expected_sha256: str) -> bool:
    import hashlib
    from pathlib import Path
    p = Path(path)
    if not p.is_file():
        return False
    return hashlib.sha256(p.read_bytes()).hexdigest() == expected_sha256
