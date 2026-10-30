# SQLite data dictionary

## Eligibility and provenance

- `cohorts`: immutable dated registry snapshots, source URL, raw checksum, release identifier, and active flag.
- `variants`: immutable study identity, original representation, normalized HGVS, assembly, transcript, source row identity, and registry URL.
- `cohort_memberships`: snapshot-specific variant state. `included` requires source classification exactly `Pathogenic`; `excluded` preserves another registry class; `held` records unresolved or missing evidence.
- `outside_annotations`: optional non-registry annotations. These records never change eligibility.

## Evidence and delivery taxonomy

- `delivery_methods`: family, method, specific version, aliases, source, and update state.
- `therapy_candidates`: stable candidate identity, therapeutic strategy, cargo, aliases, and source.
- `candidate_methods` and `study_methods`: many-to-many links that avoid duplicating candidate or study records.
- `studies`: unique reported study identity, evidence type, phenotype/stage, date, source, checksum, review and limitations.
- `research_questions`: reusable scientific questions and endpoints.

## Runs and results

- `run_specs`: canonical analysis subject, cohort version, tool/model/data/code versions, context, parameters, and deterministic SHA-256 fingerprint.
- `logical_runs`: reserved or executed logical work with status, attempt, timestamps, reason, and retry history.
- `results`: prediction, observation, or failure outcome with payload, artifact checksum, uncertainty and quality status.
- `reuse_events`: links a reuse request to the original logical run without treating reuse as independent evidence.
- `scheduler_state`: cadence, cycle status, checkpoint timestamps, activation state, and host time information.

## Duplicate and freshness rules

The canonical JSON payload is sorted and compacted before hashing. Variant identity, active cohort, question, tool, version, model checkpoint, dataset checksum, assembly, transcript, delivery method, biological context, parameters, and code revision participate where present. A reviewed successful result with an intact artifact (when declared) may be reused. Missing, corrupt, stale, or unreviewed evidence prevents reuse. Repeated evidence reports remain linked and are not independent scientific counts.
