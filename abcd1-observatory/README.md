# ABCD1 Research Observatory

A buildless public research-tracker website. The current artifact is local; public deployment is blocked because the Sites creation service is unavailable in this session. No Site project ID or public URL was returned, and no deployment has been claimed.

## Preview

From this directory, run `node scripts/serve.mjs`, then visit `http://127.0.0.1:4173/`. The server binds only to localhost. No package installation or build step is needed. Run `node --check dist/assets/app.js` and `node scripts/check.mjs` for source/snapshot checks.

## What works

- Six navigable sections: overview, vector workstreams, roadmap, tests/predictions, tools, documents/sources.
- Workstream search, delivery-family filtering, and accessible detail dialogs.
- Milestone status filters and tool search/role filters.
- Downloadable project JSON, published-run CSV, and research documents.
- Responsive layout, mobile navigation, keyboard focus, reduced-motion support, and readable empty/error states.

The snapshot records six completed planning checkpoints and eight pending implementation milestones. No variant manifest or run records are imported. The background loop is not active. Existing local research files outside this Site have not been imported or assessed by this website.

## Content and update contract

`dist/data/project.json` is the reviewed public snapshot. It contains no private chat, patient records, credentials, local paths, or unreviewed local variant files. The browser reads this file; visitors cannot modify shared scientific records. Preferences or browser storage are not used as a research database.

For now, update the JSON and publish a new static version. The future pipeline should export an explicit public-data allowlist from its scientific database, validate it, review its evidence state, and publish the snapshot only after integrity/eligibility checks. Updates must never expose the complete private database or imply a run succeeded before evidence is available. Add automated publishing after the research pipeline and scheduled loop are validated.

Variant counts remain `null` with `imported: false` until a dated Pathogenic-only manifest has been imported. Runs remain an empty array until actual records exist. Each run should include a stable ID, eligible variant identity, tool/version, vector method, endpoint, evidence type, status, and source link; detailed provenance belongs in source-linked artifacts. Preserve distinctions between predictions, experiments, clinical observations, and software demonstrations.

Delivery families, therapeutic strategies, cargos, ex vivo/in vivo mode, routes, target cells, and phenotypes are distinct concepts. Multi-method studies share one underlying evidence identity.

## Documents

Public copies of the research specification and tool report are under `dist/documents/`. Regenerate these reviewed copies when the source documents change. Do not copy the workspace or its other research files wholesale into the Site.

## Publish when Sites access is restored

Read `.openai/hosting.json` first. No project ID is currently set. Register once through Sites, immediately persist the exact returned ID, and use its short-lived source credential only through the Sites source helper's stdin. Keep credentials out of files and logs. The user explicitly requested public access: set the Site audience to public through the supported native access tool, push/package the exact source, save that version, deploy it, and verify a successful returned URL. Do not invent an ID, URL, or publication status. The existing source directory should be reused.

The static contents of `dist/` are also portable to a suitable static host. No external hosting account or paid service has been configured.
