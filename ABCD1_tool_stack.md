# Recommended ABCD1 research tool stack

Research checked: October 30, 2026. This is a tool-selection specification; the pipeline, database, and background scheduler have not been implemented or activated.

## Selection and scope

This is my recommended expert research stack for this project's constraints, rather than a claim that one universal ranking fits every gene-therapy program. Selection favors task relevance, original methods and independent evaluation, transparent provenance, practical access, and reproducibility. AI is used for defined prediction or literature tasks. Conventional bioinformatics, statistics, and databases supply essential foundations.

Only variants explicitly labeled **Pathogenic** in a versioned snapshot of the [ABCD1 Variant Registry](https://adrenoleukodystrophy.info/mutations-and-variants-in-abcd1) qualify as study targets. Other resources annotate eligible variants or supply general biological/therapy evidence. They cannot expand the cohort. Published tool benchmarks are background evidence about tools, not additional project study variants. Reference sequences and off-target genomic locations are contextual inputs, not additional therapeutic targets.

## 1. Core scientific resources and tools

| Stage | Selected tool/resource | Project use and rationale | Access and execution |
|---|---|---|---|
| Eligibility | ABCD1 Variant Registry | Dated Pathogenic-only manifest, original HGVS/reference identifiers, references and source classification. | Public catalog; verify actual export and reuse terms before automated collection or redistribution. Never substitute another source for eligibility. |
| Literature retrieval | PubMed E-utilities + Europe PMC REST | Reproducible, versioned searches; PMID/PMCID/DOI identities; article metadata and available open-access full text. | Public APIs, CPU/network only. Observe rate limits and article-level reuse rights. |
| AI literature annotation | NLM PubTator 3.0 | Extract/index genes, variants, diseases and reported relationships to help find relevant evidence. | Hosted precomputed annotations/API; no local language-model training. Treat extraction as candidate annotations to check against the paper. |
| Variant normalization | Mutalyzer 3 | HGVS validation, normalization, and traceable conversions. Preserve original and normalized representations together. | MIT code; public service or local CPU. Benchmark any automated service adapter and retain reference versions/warnings. |
| Consequence annotation | Ensembl VEP + Variant Recoder | Annotate transcript/protein consequences and cross-identifiers for eligible variants. | Apache-2.0 software; web/REST initially. Preserve source assembly/transcript and use matching endpoints/releases; individual annotation sources/plugins have their own terms. |
| Supporting evidence | ClinVar + UniProt | ClinVar assertions, review status, dates/conflicts; curated ABCD1 sequence/function annotations from UniProt. | Public resources. Save accession/release/source and applicable data terms. These annotations do not change cohort eligibility. |
| Structural evidence | RCSB PDB + Mol* viewer | Inspect experimental ABCD1 structures and map eligible variants after sequence/construct checks. | Browser/CPU; PDB archive data CC0. No GPU inference required. |
| Predicted structural context | AlphaFold Protein Structure Database | Retrieve existing reference models where experimental coverage leaves a useful question. | Predicted structure data CC BY 4.0. No local prediction needed. Confidence scores do not establish functional loss, rescue, or clinical response. |
| Clinical/translational evidence | FDA product/assessment documents, current DailyMed labeling, ClinicalTrials.gov API v2 | Track indications, safety changes, study identifiers, status, endpoints and reported results, grouped by delivery method and phenotype. | Public sources; archive retrieval dates, document revisions and result cutoffs. Registration is not proof of efficacy. |

PubMed's standard E-utilities rate is up to three requests/second without an API key; use conservative cached requests and backoff. Full-text availability does not imply permission to redistribute it. [NLM API policy](https://support.nlm.nih.gov/kbArticle/?pn=KA-05510), [Europe PMC REST documentation](https://dev.europepmc.org/RestfulWebService), [ClinicalTrials.gov API v2 announcement](https://www.nlm.nih.gov/pubs/techbull/ma24/ma24_clinicaltrials_api.html).

PubTator has an original methods paper describing its AI entity/relation annotation and programmatic access. Automated relations remain distinct from adjudicated evidence. [PubTator 3.0 original paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11223843/).

Mutalyzer and VEP address identity and consequences; neither determines the preferred therapy. Keep ambiguous build/transcript mappings on hold. [Mutalyzer official source and MIT license](https://github.com/mutalyzer/mutalyzer), [VEP documentation](https://www.ensembl.org/info/docs/tools/vep/index.html), [VEP code/license](https://github.com/Ensembl/ensembl-vep), [original VEP methods paper](https://doi.org/10.1186/s13059-016-0974-4), [ClinVar description](https://www.ncbi.nlm.nih.gov/clinvar/intro/), [UniProt](https://www.uniprot.org/).

ABCD1 has experimental structures; for example, 7SHM is an ATP-bound cryo-EM entry that explicitly contains construct mutations. Inspect its validation report, resolved residues, assembly and experimental state before using it as a reference. [7SHM entry](https://www.rcsb.org/structure/7SHM), [RCSB usage policy](https://www.rcsb.org/pages/usage-policy), [AlphaFold DB access/license](https://alphafold.ebi.ac.uk/).

For this project, retain primary clinical sources alongside study publications. [FDA Skysona page](https://www.fda.gov/vaccines-blood-biologics/skysona), [DailyMed label](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=f189502b-dc44-4289-99a6-cfba36918329).

## 2. Core implementation stack

| Component | Selection | Why it fits / constraints |
|---|---|---|
| Importers, API clients, coordinator | Python, with uv-managed locked dependencies | Native Windows baseline; small, testable adapters and explicit manifests. uv is MIT/Apache-2.0. Keep scientific packages in separate environments where required. |
| Tests/predictions/evidence registry | SQLite through Python | Transactional local database, unique canonical analysis fingerprints, atomic task claims, append-preserving attempts/results, eligibility history, source and artifact provenance. SQLite deliverable code is public domain. |
| Reproducible scientific execution | Snakemake | Dependency-based jobs and resumable workflows. MIT; use the officially documented WSL setup on Windows and Pixi/conda-forge/Bioconda environments as needed. Begin with a small workflow. |
| Source/configuration history | Git | Track code, schemas, manifests, dependency locks and reports. Keep large scientific artifacts outside ordinary Git and store checksummed paths in the registry. GPLv2 software. |
| Vector-centered browsing | Local Streamlit | Search/filter views for delivery family/system, candidate, variant, phenotype, endpoint, evidence type and validation state. Apache-2.0 library; paid hosting is unnecessary. |

These choices are engineering recommendations for a local research system. [uv documentation](https://docs.astral.sh/uv/), [uv source/license](https://github.com/astral-sh/uv), [SQLite architecture](https://www.sqlite.org/about.html), [SQLite public-domain terms](https://www.sqlite.org/copyright.html), [Snakemake installation](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html), [Snakemake license](https://github.com/snakemake/snakemake/blob/main/LICENSE.md), [Snakemake methods paper](https://pubmed.ncbi.nlm.nih.gov/34035898/), [Git license](https://github.com/git/git/blob/master/COPYING), [Streamlit source/license](https://github.com/streamlit/streamlit).

Snakemake caching does not replace scientific duplicate detection. SQLite must distinguish the scientific question, exact relevant inputs, delivery context, model/data/code versions, execution attempts and independent studies. A source refresh date or display-folder change alone must not invalidate otherwise identical analytic work. [Snakemake caching documentation](https://snakemake.readthedocs.io/en/stable/executing/caching.html).

Use the previously agreed hourly-active/daily-idle scheduler policy after a manual validation run. The scheduler invokes the coordinator; Snakemake runs eligible scientific jobs; SQLite records identity, outcomes and checkpoints. Cloud notebook sessions are optional interactive resources, not the persistent scheduler. Free Colab hardware and runtime availability are not guaranteed. [Colab FAQ](https://research.google.com/colaboratory/faq.html).

## 3. Selected AI/ML modules: activate only for a defined question

### Literature screening: ASReview LAB

Use ASReview when the literature set is large enough to justify active-learning prioritization. It learns from reviewer relevance labels and orders records for screening. Use a CPU-compatible model, save labels/model/configuration, and define stopping and recall checks. It does not automatically establish that evidence is correct or that all relevant studies were found. Apache-2.0 software. Zotero is a useful optional desktop reference manager; local attachment storage avoids its free cloud-storage ceiling. [ASReview official source/license](https://github.com/asreview/asreview), [original methods paper](https://www.nature.com/articles/s42256-020-00287-7), [Zotero sync documentation](https://www.zotero.org/support/sync), [Zotero storage limits](https://www.zotero.org/storage/).

### Splice mechanism: Pangolin; SpliceAI as a conditional comparator

Use Pangolin for eligible variants with a concrete splice-effect question, including relevant exonic effects. Repository GPL-3.0; PyTorch implementation. Prefer available traceable scores or small benchmarked batches. GPU may improve performance; do not assume large CPU inference is cheap. SpliceAI is a useful established comparator where access/license conditions permit, but current code is PolyForm Strict and weights are CC BY-NC 4.0; its repository is archived. Treat commercial access and hosted-service terms separately. Agreement between two predictors is not independent RNA validation. [Pangolin source](https://github.com/tkzeng/Pangolin), [Pangolin original study](https://pmc.ncbi.nlm.nih.gov/articles/PMC9022248/), [SpliceAI source and current terms](https://github.com/Illumina/SpliceAI), [independent comparative benchmark](https://pmc.ncbi.nlm.nih.gov/articles/PMC10734170/).

### Missense context: precomputed AlphaMissense

Retrieve existing scores for eligible missense variants when they add a clearly stated mechanistic prioritization feature. Prediction data are CC BY 4.0; code is Apache-2.0 and its repository is archived. No new model training is needed. These variants already meet the project's source eligibility criterion, so another pathogenicity score is secondary and cannot establish phenotype, structure change, functional rescue or therapeutic response. [Official licensing update](https://deepmind.google/blog/a-catalogue-of-genetic-mutations-to-help-pinpoint-the-cause-of-diseases/), [data README](https://storage.googleapis.com/dm_alphamissense/README.pdf), [source/archive status](https://github.com/google-deepmind/alphamissense).

### Regulatory mechanisms: optional AlphaGenome Atlas/API

Use for a specific expression, splicing or chromatin-effect question. Prefer supported precomputed Atlas lookups over local inference. API access requires a key and is free for noncommercial use with dynamic limits; API/client software is Apache-2.0, while outputs/model weights have separate restrictions. The service's reference is hg38, so mapping from source hg19 records must be validated. Local research inference recommends H100-class hardware and is outside the baseline. Output restrictions include limits on training other models, with specific artifact exceptions; retain applicable terms with results. It is not a clinical-outcome or gene-therapy-success model. [Official API/Atlas repository](https://github.com/google-deepmind/alphagenome), [output terms FAQ](https://google-deepmind-alphagenome.readthedocs-hosted.com/faqs.html#what-terms-of-use-apply-to-alphagenome-outputs), [research implementation](https://github.com/google-deepmind/alphagenome_research), [original Nature paper](https://www.nature.com/articles/s41586-025-10014-0).

### Omics: DESeq2 and Scanpy first; scvi-tools conditionally

Only activate an omics branch after identifying a suitable public dataset and a valid design. Use GEO processed counts/metadata, CELLxGENE slices for cell context, and GTEx open summaries for reference tissue context. Public access does not imply availability of genotype or eligible variant labels; GTEx protected individual-level data are outside the baseline. These datasets cannot expand the therapeutic-target cohort. [GEO overview](https://www.ncbi.nlm.nih.gov/geo/info/overview.html), [CELLxGENE Census selective queries](https://chanzuckerberg.github.io/cellxgene-census/cellxgene_census_docsite_quick_start.html), [GTEx protected-data access](https://gtexportal.org/home/protectedDataAccess).

Use DESeq2 for appropriately designed bulk or donor-level pseudobulk count comparisons (LGPL >=3) and Scanpy/AnnData for single-cell QC/exploration (BSD-3-Clause). Modest processed data can use CPU; benchmark memory before importing large atlases. Cells are not independent donor replicates. Add scvi-tools/scVI (BSD-3-Clause) only for an actual integration/reference-mapping need and sufficient data/compute. Validate preservation of disease effects; no integration result establishes therapeutic rescue. [DESeq2 package/license](https://bioconductor.org/packages/release/bioc/html/DESeq2.html), [DESeq2 original paper](https://doi.org/10.1186/s13059-014-0550-8), [Scanpy documentation](https://scanpy.readthedocs.io/en/stable/), [Scanpy license](https://github.com/scverse/scanpy/blob/main/LICENSE), [scvi-tools installation](https://docs.scvi-tools.org/en/latest/installation.html), [scvi-tools license](https://github.com/scverse/scvi-tools/blob/main/LICENSE).

## 4. Later-stage or restricted tools

| Tool | Use only when | Material condition |
|---|---|---|
| VariantValidator | An independent check is useful for a difficult HGVS/reference mapping. | Hosted REST currently requires approved account credentials; anonymous background access must not be assumed. |
| UCSF ChimeraX | Desktop structural review adds value beyond Mol*. | Noncommercial license; commercial licensing separate. Open-Source PyMOL is a source-based alternative, distinct from the paid PyMOL bundle. |
| ColabFold | Existing experimental and reference models cannot answer a concrete structural question. | MIT wrapper; weights separately licensed. Pin exact model/checkpoint/MSA/template provenance and confirm compute. |
| CRISPOR | An editing research branch has been selected and candidate assessment is justified. | Academic/nonprofit free-use terms; commercial licensing separate. Third-party scoring dependencies have separate conditions. |
| Cas-OFFinder 2 stable release | Computational off-target nomination is needed. | BSD-3-Clause, OpenCL runtime/device and genome storage required. The current development branch warns that version 3 is not production ready; pin a validated stable version 2. Candidate sites do not establish safety. |
| CRISPRitz | Variant-aware off-target work is justified by suitable contextual data. | Academic-free/commercial-paid terms, Linux execution and potentially substantial indexing resources. |
| CRISPResso2 | Actual editing sequencing data are available for outcome quantification. | Current source license is academic/noncommercial restricted; no unconditional free commercial/clinical use. This is an outcome-analysis tool, not a therapy-efficacy predictor. |

These are selection-level recommendations; no construct sequences, guide sequences, experimental recipes or dosing are generated here. [VariantValidator current REST access](https://openvar.github.io/variantValidator/rest-vv/rest_VariantValidator.html), [ChimeraX terms/source](https://github.com/RBVI/ChimeraX), [Open-Source PyMOL license](https://github.com/schrodinger/pymol-open-source/blob/master/LICENSE), [ColabFold license](https://github.com/sokrypton/ColabFold/blob/main/LICENSE), [ColabFold model-license separation](https://github.com/sokrypton/ColabFold/blob/main/pyproject.toml), [CRISPOR source/terms](https://github.com/maximilianh/crisporWebsite), [Cas-OFFinder source/version warning](https://github.com/snugel/cas-offinder), [CRISPRitz license](https://github.com/pinellolab/CRISPRitz/blob/master/LICENSE), [CRISPResso2 authoritative license](https://raw.githubusercontent.com/pinellolab/CRISPResso2/master/LICENSE.txt).

## 5. Tools I would defer

Evo 2 is a serious general genomic research model with Apache-2.0 code/checkpoints, but current local implementations require compatible CUDA GPUs; some variants require Hopper/FP8 and the largest requires multiple H100s. A durable free hosted allowance was not verified. Add it only if a defined question, access and a relevant benchmark justify the expense/complexity. [Official repository and requirements](https://github.com/arcinstitute/evo2), [7B model card](https://huggingface.co/arcinstitute/evo2_7b).

Do not make scGPT/Geneformer mandatory. A 2025 independent zero-shot evaluation found simpler methods could outperform these models in some tested settings. This is a task-specific result, not a conclusion about every foundation model. Require added value against the project's baseline before adoption. [Original independent evaluation](https://doi.org/10.1186/s13059-025-03574-x).

Do not use generic vector-AI rankings as established human CNS-delivery or ABCD1 efficacy evidence. Published capsid models have particular training/validation domains; assess transferability rather than assigning a universal therapy-success score. Fit4Function is an example of important multi-trait capsid research, not a ready-made ABCD1 therapy evaluator. [Original Fit4Function study](https://www.nature.com/articles/s41467-024-50555-y).

## 6. Deployment and decision rules

Start with the registry importer, Mutalyzer/VEP adapters, evidence retrieval, SQLite, small Snakemake workflow, Git/uv and local Streamlit views. Reuse published structural data. Add each optional AI module only when its result could change a stated research decision. No new foundation-model training is required.

Before enabling an adapter, record the actual tested software release/model/checkpoint, dependency lock, source/data release, input/output schema, checksum, license/access conditions, runtime/resource measurements, validation cases and failure/retry behavior. Hosted responses must preserve enough raw provenance for later audit; public endpoints do not promise immutable results or availability. Pin verified compatible versions during implementation rather than copying untested version numbers from a recommendation document.

The $0 baseline applies to required tool/service fees, not electricity, hardware, storage, model-account usage, biological experiments, manufacturing or clinical development. Restricted tools remain disabled unless the intended use qualifies. Keep source eligibility, exact scientific deduplication, vector organization, and the hourly-active/daily-idle checkpoint policy intact when modules change.
