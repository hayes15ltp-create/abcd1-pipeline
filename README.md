# ABCD1 Research Pipeline

This repository is a zero-cost baseline implementation for source-gated ABCD1 research. It combines a SQLite registry, Pathogenic-only cohort importer, canonical run fingerprinting, scheduling/recovery primitives, a bounded scheduler starter, public-snapshot export, a small Snakemake workflow, and an optional local Streamlit browser.

## Hard eligibility rule

Only variants explicitly classified `Pathogenic` in a dated, accessible snapshot of the [ABCD1 Variant Registry](https://adrenoleukodystrophy.info/mutations-and-variants-in-abcd1) can enter the active cohort. Other classifications are excluded. Missing, unresolved, or ambiguous classifications are held. ClinVar or another resource may annotate an included variant but cannot expand eligibility.

The live registry page requires a structured export or verified browser/API path before a real cohort manifest can be imported. A plain HTML fetch does not establish variant rows. This repository therefore does not invent registry records.

## Quick start

```powershell
python -m pip install pytest
python -m pytest -q
python -m abcd1.cli --db data/abcd1.sqlite3 import-cohort tests/fixtures/cohort_a.json --date 2026-10-30 --release TEST-SNAPSHOT
python -m abcd1.cli --db data/abcd1.sqlite3 members
python -m abcd1.cli --db data/abcd1.sqlite3 export-cohort data/exports
python -m abcd1.scheduler --db data/abcd1.sqlite3 --once
```

The fixture is explicitly synthetic. It exercises software gates only and must never be presented as a scientific registry cohort.

## Automatic verification database updates

Every push to `main`, manual workflow dispatch, and the Monday 12:00 UTC schedule runs the pipeline tests and adds 10 synthetic AAV software-verification records to `data/verify.sqlite3`.

The GitHub Actions workflow `.github/workflows/autoupdate-verify.yml` commits the updated SQLite file back to `main`. The commit message includes `[skip ci]`, preventing database-update commits from recursively triggering another run. Streamlit deployments attached to the repository receive the committed database when they rebuild or refresh from `main`.

These records are planning-only synthetic test data. The workflow does not import scientific registry variants or publish research evidence.

## Proof-of-concept commands

```powershell
uv run --with pytest python -m pytest -q
python -m abcd1.cli --db data/poc.sqlite3 import-cohort tests/fixtures/cohort_a.json --date 2026-10-30 --release POC-SYNTHETIC
python -m abcd1.scheduler --db data/poc.sqlite3 --once
```

## Optional interfaces

```powershell
python -m pip install "streamlit>=1.49,<2" pandas
python -m streamlit run streamlit_app.py
```

The browser defaults to `data/verify.sqlite3`, which is the verification snapshot. It also
provides read-only access to tables and a download button. Select a different SQLite path in
the sidebar if needed.

Snakemake is optional:

```powershell
python -m pip install "snakemake>=9,<10"
python -m snakemake -s workflow/Snakefile --cores 1
```

## Scheduling

The scheduler reports `hourly` when actionable queued/work-failure state exists and `daily` otherwise. It does **not** activate a persistent Windows job or background process. Persistent activation requires a host-specific task/service setup after a manual proof run.

Schedule state is zone-aware for `America/New_York` and recovery actions remain records in SQLite.

## Public observatory

The existing static observatory under `abcd1-observatory/dist` remains planning-only until a scientifically reviewed, public-safe snapshot exporter supplies publishable records. Public exports preserve the rule that planning milestones are not research results and that reused/repeated evidence is not independent evidence.

## Verification

- `tests/test_pipeline.py`: duplicate reuse, queued deduplication, tool-version change, eligibility rejection, retry records.
- `tests/test_public.py`: planning-only public snapshot and no run leak.
- `abcd1-observatory/scripts/check.mjs`: static-site integrity.
