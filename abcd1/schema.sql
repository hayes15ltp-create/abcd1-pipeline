PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS cohorts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    registry_release TEXT,
    active INTEGER NOT NULL DEFAULT 0 CHECK (active IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    immutable_id TEXT NOT NULL UNIQUE,
    original_representation TEXT NOT NULL,
    hgvs TEXT NOT NULL,
    assembly TEXT NOT NULL DEFAULT 'GRCh37',
    transcript TEXT NOT NULL DEFAULT 'NM_000033.3',
    source_record_id TEXT,
    source_url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cohort_memberships (
    cohort_id INTEGER NOT NULL REFERENCES cohorts(id),
    variant_id INTEGER NOT NULL REFERENCES variants(id),
    source_classification TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('included', 'excluded', 'held')),
    row_reference TEXT,
    excluded_reason TEXT,
    included_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    PRIMARY KEY(cohort_id, variant_id)
);

CREATE TABLE IF NOT EXISTS outside_annotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_id INTEGER NOT NULL REFERENCES variants(id),
    source TEXT NOT NULL,
    classification TEXT,
    accession TEXT,
    snapshot_date TEXT,
    raw_sha256 TEXT,
    conflicts_with_registry INTEGER NOT NULL DEFAULT 0 CHECK(conflicts_with_registry IN (0, 1))
);

CREATE TABLE IF NOT EXISTS delivery_methods (
    id TEXT PRIMARY KEY,
    family TEXT NOT NULL,
    name TEXT NOT NULL,
    version TEXT,
    aliases TEXT NOT NULL DEFAULT '[]',
    source_url TEXT,
    active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0, 1)),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS therapy_candidates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    strategy TEXT NOT NULL,
    cargo_type TEXT,
    aliases TEXT NOT NULL DEFAULT '[]',
    source_url TEXT
);

CREATE TABLE IF NOT EXISTS candidate_methods (
    candidate_id TEXT NOT NULL REFERENCES therapy_candidates(id),
    method_id TEXT NOT NULL REFERENCES delivery_methods(id),
    PRIMARY KEY(candidate_id, method_id)
);

CREATE TABLE IF NOT EXISTS studies (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    evidence_type TEXT NOT NULL,
    phenotype TEXT,
    stage TEXT,
    publication_date TEXT,
    source_url TEXT NOT NULL,
    source_checksum TEXT,
    review_status TEXT NOT NULL DEFAULT 'proposed',
    limitations TEXT
);

CREATE TABLE IF NOT EXISTS study_methods (
    study_id TEXT NOT NULL REFERENCES studies(id),
    method_id TEXT NOT NULL REFERENCES delivery_methods(id),
    PRIMARY KEY(study_id, method_id)
);

CREATE TABLE IF NOT EXISTS research_questions (
    id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    endpoint TEXT,
    phenotype TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS run_specs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fingerprint TEXT NOT NULL UNIQUE,
    cohort_id INTEGER NOT NULL REFERENCES cohorts(id),
    question_id TEXT NOT NULL REFERENCES research_questions(id),
    subject_variant_id INTEGER NOT NULL REFERENCES variants(id),
    method_id TEXT REFERENCES delivery_methods(id),
    tool_name TEXT NOT NULL,
    tool_version TEXT NOT NULL,
    model_checkpoint TEXT,
    dataset_snapshot TEXT,
    dataset_sha256 TEXT,
    assembly TEXT,
    transcript TEXT,
    biological_context TEXT,
    parameters TEXT NOT NULL DEFAULT '{}',
    code_revision TEXT,
    canonical_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS logical_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spec_id INTEGER NOT NULL REFERENCES run_specs(id),
    status TEXT NOT NULL CHECK(status IN ('queued', 'running', 'succeeded', 'failed', 'abandoned')),
    reason TEXT,
    attempt INTEGER NOT NULL DEFAULT 1,
    started_at TEXT,
    finished_at TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE(spec_id, attempt)
);

CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    logical_run_id INTEGER NOT NULL REFERENCES logical_runs(id),
    status TEXT NOT NULL CHECK(status IN ('succeeded', 'failed', 'inconclusive')),
    payload TEXT NOT NULL DEFAULT '{}',
    artifact_path TEXT,
    artifact_sha256 TEXT,
    uncertainty TEXT,
    quality_status TEXT NOT NULL DEFAULT 'unreviewed',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS reuse_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requested_run_id INTEGER NOT NULL REFERENCES logical_runs(id),
    reused_run_id INTEGER NOT NULL REFERENCES logical_runs(id),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS scheduler_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_membership_cohort_state ON cohort_memberships(cohort_id, state);
CREATE INDEX IF NOT EXISTS idx_run_status ON logical_runs(status);
CREATE INDEX IF NOT EXISTS idx_result_status ON results(status, quality_status);
