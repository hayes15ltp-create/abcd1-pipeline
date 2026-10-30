from pathlib import Path

import pytest
import json
import tempfile

from abcd1.cohort import import_snapshot
from abcd1.db import connect
from abcd1.recovery import retry_failed
from abcd1.runs import complete_run, schedule_run


FIXTURE = Path(__file__).parent / "fixtures/cohort_a.json"


def spec(question_id="Q-SYNTH-1", immutable_id="SYNTHETIC-FIXTURE-A-001", tool_version="1"):
    return {
        "immutable_id": immutable_id,
        "question_id": question_id,
        "question": "Synthetic proof-of-concept only",
        "tool_name": "software-test-adapter",
        "tool_version": tool_version,
        "method_id": None,
        "endpoint": "fixture scheduling",
        "phenotype": "synthetic",
        "parameters": {"fixture": True},
    }


def test_duplicate_reuse_and_concurrency():
    conn = connect(":memory:")
    import_snapshot(conn, FIXTURE, "2026-10-30", "TEST-SNAPSHOT")
    first = schedule_run(conn, spec())
    assert first["status"] == "scheduled"
    concurrent = schedule_run(conn, spec(), reason="concurrent equivalent submission")
    assert concurrent["status"] == "deduplicated"
    complete_run(conn, first["logical_run_id"], "succeeded", {"fixture": True})
    conn.execute(
        "UPDATE results SET quality_status='reviewed', artifact_path=NULL, artifact_sha256=NULL WHERE logical_run_id=?",
        (first["logical_run_id"],),
    )
    conn.commit()

    reused = schedule_run(conn, spec(), reason="proof duplicate")
    assert reused["status"] == "reuse"
    duplicate = schedule_run(conn, spec(), reason="concurrent equivalent submission")
    assert duplicate["status"] == "reuse"

    changed = schedule_run(conn, spec(tool_version="2"), reason="meaningful version change")
    assert changed["status"] == "scheduled"


def test_eligibility_refresh_and_retry():
    conn = connect(":memory:")
    import_snapshot(conn, FIXTURE, "2026-10-30", "TEST-SNAPSHOT-A")
    members = conn.execute(
        """
        SELECT COUNT(*) AS count FROM cohorts c
        JOIN cohort_memberships cm ON cm.cohort_id=c.id
        WHERE c.active=1 AND cm.state='included'
        """
    ).fetchone()["count"]
    assert members == 1

    with pytest.raises(ValueError, match="not an active Pathogenic"):
        schedule_run(conn, spec(immutable_id="SYNTHETIC-FIXTURE-X-001"))

    first = schedule_run(conn, spec())
    complete_run(conn, first["logical_run_id"], "failed", {"error": "fixture failure"})
    retried = retry_failed(conn, first["logical_run_id"], "fixture retry")
    assert conn.execute("SELECT attempt FROM logical_runs WHERE id=?", (retried,)).fetchone()["attempt"] == 2

    refresh = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump({"variants": [{
        "immutable_id": "SYNTHETIC-FIXTURE-A-001",
        "source_record_id": "TEST-ROW-001",
        "hgvs": "c.1A>G (software-test fixture)",
        "classification": "VUS",
        "row_reference": "synthetic refreshed row 1",
    }]}, refresh)
    refresh.close()
    import_snapshot(conn, refresh.name, "2026-10-31", "TEST-SNAPSHOT-B")
    active = conn.execute(
        """
        SELECT cm.state FROM cohorts c JOIN cohort_memberships cm ON cm.cohort_id=c.id
        JOIN variants v ON v.id=cm.variant_id
        WHERE c.active=1 AND v.immutable_id='SYNTHETIC-FIXTURE-A-001'
        """
    ).fetchone()["state"]
    assert active == "excluded"
    histories = conn.execute(
        """
        SELECT COUNT(*) AS count FROM cohort_memberships cm
        JOIN variants v ON v.id=cm.variant_id
        WHERE v.immutable_id='SYNTHETIC-FIXTURE-A-001'
        """
    ).fetchone()["count"]
    assert histories == 2
