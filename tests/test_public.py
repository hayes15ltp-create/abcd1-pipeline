import json
import shutil
from pathlib import Path

from abcd1.cohort import import_snapshot
from abcd1.db import connect
from abcd1.public_export import export_observatory_snapshot


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/cohort_a.json"


def test_public_snapshot_stays_planning_only_and_source_safe(tmp_path):
    source = ROOT / "abcd1-observatory"
    output = tmp_path / "site"
    (output / "dist").mkdir(parents=True)
    (output / "dist/data").mkdir()
    shutil.copytree(source / "dist/assets", output / "dist/assets")
    shutil.copytree(source / "dist/documents", output / "dist/documents")
    shutil.copytree(source / "dist/data", output / "dist/data", dirs_exist_ok=True)
    shutil.copy2(source / "dist/index.html", output / "dist/index.html")

    conn = connect(":memory:")
    import_snapshot(conn, FIXTURE, "2026-10-30", "TEST-SNAPSHOT")
    result = export_observatory_snapshot(conn, source, output)
    assert result["published_runs"] == 0
    assert result["active_cohort_variants"] == 1

    data = json.loads((output / "dist/data/project.json").read_text(encoding="utf-8"))
    assert data["cohort"]["imported"] is False
    assert data["cohort"]["variantCount"] is None
    assert data["runs"] == []
    assert data["automation"]["active"] is False
