from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from abcd1.db import connect
from abcd1.runs import complete_run, schedule_run


def update_database(db_path: Path, count: int, batch_id: str) -> dict:
    conn = connect(db_path)
    try:
        method = conn.execute(
            "SELECT id FROM delivery_methods WHERE id=?",
            ("AAV-UNSPECIFIED",),
        ).fetchone()
        if not method:
            conn.execute(
                """
                INSERT INTO delivery_methods(id, family, name, version, aliases, source_url, active)
                VALUES(?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    "AAV-UNSPECIFIED",
                    "viral",
                    "Adeno-associated virus (AAV)",
                    "unspecified",
                    '["AAV"]',
                    "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/human-gene-therapy-products-incorporating-human-genome-editing",
                ),
            )
            conn.commit()

        active_cohort = conn.execute(
            "SELECT id FROM cohorts WHERE active=1 LIMIT 1"
        ).fetchone()
        if not active_cohort:
            raise RuntimeError(
                f"{db_path} has no active cohort; workflow verification records were not added"
            )

        logical_run_ids: list[int] = []
        for test_number in range(1, count + 1):
            spec = {
                "immutable_id": "SYNTHETIC-FIXTURE-A-001",
                "question_id": f"AAV-AUTO-{batch_id}-{test_number:03d}",
                "question": "Verify AAV software pipeline test case",
                "endpoint": "software_verification",
                "phenotype": "planning-only synthetic fixture",
                "method_id": "AAV-UNSPECIFIED",
                "tool_name": "github-actions-test-adapter",
                "tool_version": "1.0",
                "assembly": "GRCh37",
                "transcript": "NM_000033.3",
                "biological_context": "AAV workstream planning-only verification",
                "parameters": {
                    "batch_id": batch_id,
                    "test_number": test_number,
                    "synthetic_only": True,
                },
                "code_revision": f"github-actions:{batch_id}",
            }
            scheduled = schedule_run(conn, spec, "automated synthetic workflow verification")
            logical_run_id = int(scheduled["logical_run_id"])
            if scheduled["status"] == "scheduled":
                complete_run(
                    conn,
                    logical_run_id,
                    "succeeded",
                    {
                        "test": "AAV software verification",
                        "batch_id": batch_id,
                        "test_number": test_number,
                        "planning_only": True,
                        "scientific_claim": False,
                        "subject_variant": "synthetic software fixture",
                    },
                )
            logical_run_ids.append(logical_run_id)

        return {
            "database": str(db_path),
            "batch_id": batch_id,
            "count": count,
            "logical_run_ids": logical_run_ids,
        }
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=Path("data/verify.sqlite3"))
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--batch-id", default=os.environ.get("GITHUB_RUN_ID", "local"))
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be at least 1")

    result = update_database(args.db, args.count, args.batch_id)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
