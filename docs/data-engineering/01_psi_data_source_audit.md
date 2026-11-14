# FlameLens — NASA PSI Data Source Audit (Stage 1)

| Field | Value |
| :--- | :--- |
| **Status** | COMPLETED — awaiting explicit approval before Stage 2 |
| **Audit date** | 2026-11-14 |
| **PSI API snapshot captured** | 2026-11-14T04:26:41Z |
| **Inventories generated** | 2026-11-14T04:54:57Z |
| **Scope** | 7 pilot investigations in full (description + datasets + every file); all 26 combustion investigations for description metadata |
| **Download policy** | `MAX_FILE_SIZE_MB=100` (104,857,600 bytes) |
| **Scientific files downloaded** | **0** |
| **Salma research documents** | Not opened, read, summarized, or modified |
| **Database / RAG / frontend** | Not implemented or modified in this stage |

This report is the human-readable deliverable of **STAGE 1 — NASA PSI Data Source Audit**. The machine-readable companions are:

- `data/metadata/investigations_inventory.json`
- `data/metadata/datasets_inventory.json`
- `data/metadata/files_inventory.json`
- `data/metadata/storage_summary.json`

They are generated reproducibly by `scripts/audit_psi_source.py` from the versioned API snapshot in `data/metadata/psi_api/`. Download accessibility is re-verified by `scripts/probe_psi_download.py`, which requests only one byte per sampled file.

> **Unit convention.** All `*_human` sizes use binary units: 1 KB = 1,024 B, 1 MB = 1,024² B, 1 GB = 1,024³ B, 1 TB = 1,024⁴ B. Exact byte values are always provided alongside.

---

## Executive Summary

FlameLens now has a verified, reproducible picture of what NASA PSI actually exposes for microgravity combustion research.

**What was established**

1. The official PSI **JSON API** is a reliable replacement for the Playwright HTML scraper. It returns all 26 combustion investigations with complete description text, including the three investigations that previously failed scraping.
2. The **7 pilot investigations** expose **1,520 current files** totalling **492,609,577,604 bytes (458.778 GB)** across **13 file extensions** and **6 format categories**.
3. PSI's own `totalFileSize` sums to **509,540,592,871 bytes (474.547 GB)**. The 16.93 GB difference is almost entirely one investigation: **PSI-99 exposes only 2 files (12.5 KB) while PSI reports 16,931,016,137 bytes (15.77 GB)**. Excluding PSI-99, the inventory reconciles to within **11,642 bytes (0.000002%)** of PSI's reported total.
4. Under the 100 MiB policy, **1,056 files (14.337 GB, 3.12% of bytes)** are eligible for automatic download and **464 files (444.442 GB, 96.88% of bytes)** are over limit. The bytes are concentrated in two opaque formats: **539 ZIP archives = 416.163 GB (90.7%)** and **420 MP4 videos = 41.163 GB (9.0%)**. Together they are **99.68%** of all bytes.
5. The download path is verified: `GET /geode-py/ws/studies/{id}/download?...&redirect=false` returns a **short-lived signed S3 URL**; S3 answers `Range: bytes=0-0` with **HTTP 206** and the exact inventory size. `HEAD` returns **403** and must not be used as a size probe.
6. The legacy per-file `remote_url` values are unusable: **1,506 point at the dead `psi.ndc.nasa.gov` host** and **14 are relative `/datamanager/...` paths that return 404**.
7. PSI exposes **no dataset entity and no dataset-level descriptions**. The 383 “datasets” in this audit are deterministic FlameLens groupings derived from the top-level filename category plus the PSI `subcategory` run label. They must always be labelled **derived**, never as PSI-issued datasets.
8. **Nothing has been downloaded**, so local storage is **0 B**. Remote inventory size and local downloaded size are kept strictly separate in every artifact.

**The most important planning consequence**

The four investigations originally proposed for Stage 5 validation (PSI-25, PSI-26, PSI-98, PSI-100) are precisely the four with the least automatically accessible data by byte share: 2.98%, 0.83%, 11.10% and 4.76% respectively. Their raw science is locked inside multi-gigabyte ZIPs and videos. By contrast, **PSI-101 (SAME-R)** exposes 38.95% of its bytes within the limit (334 files, 2.288 GB) and **PSI-102 (SAME)** exposes 53.11% (103 files, 333.075 MB). Stage 4/5 should either prioritise SAME/SAME-R for end-to-end validation or introduce an explicit manual-approval workflow for selected large files.

**Key metrics**

| Metric | Value |
| :--- | ---: |
| Combustion investigations discovered | 26 |
| Pilot investigations fully audited | 7 |
| Investigations with description metadata | 26 |
| Derived dataset groups | 383 |
| Current files inventoried | 1,520 |
| Current remote inventory size | 492,609,577,604 B (458.778 GB) |
| PSI-reported total size (7 pilots) | 509,540,592,871 B (474.547 GB) |
| Inventory minus reported | −16,931,015,267 B (−15.770 GB) |
| Files with known remote size | 1,520 (100%) |
| Files with unknown remote size | 0 |
| Files within 100 MiB | 1,056 (15,393,894,208 B / 14.337 GB) |
| Files over 100 MiB | 464 (477,215,683,396 B / 444.442 GB) |
| Files with size 0 B | 4 |
| Files downloaded | 0 |
| Historical removed files (excluded from totals) | 768 (80,806,437,644 B / 75.257 GB) |
| File extensions observed | 13 |
| Dataset-level descriptions available | 0 |

---

## 1. Existing Repository Assessment

### 1.1 Repository shape

The repository is a working Phase 0/1 skeleton, not a partially built data platform. The architecture documentation, Docker database service, FastAPI shell, React shell and design system are in place. Most domain modules exist as **empty placeholder files**.

```text
flamelens/
├── backend/
│   ├── app/                  # 8 implemented modules + ~64 empty placeholders
│   ├── tests/                # 1 non-empty test file (5 tests)
│   ├── Dockerfile            # implemented
│   └── requirements.txt
├── frontend/
│   ├── src/                  # shell, layout, dashboard, routes, design system
│   ├── package.json
│   └── node_modules/         # present
├── data/
│   ├── metadata/             # PSI descriptions + this audit's inventories
│   ├── knowledge/salma/      # untouched
│   ├── raw/                  # empty
│   ├── processed/            # empty
│   └── samples/              # empty
├── docs/                     # architecture, API contracts, data dictionary, DB schema, deployment, ingestion
├── scripts/                  # empty placeholders + audit/probe scripts
├── docker-compose.yml        # PostgreSQL + pgvector and backend; no frontend service
├── pytest.ini
├── README.md
└── plan.txt                  # absent; authoritative plan supplied as plan.md outside the repo
```

### 1.2 Backend

Implemented modules (non-empty):

| File | Bytes | Role |
| :--- | ---: | :--- |
| `backend/app/main.py` | 2,253 | FastAPI app, lifespan, CORS, exception handlers |
| `backend/app/config.py` | 2,130 | Pydantic settings, CORS parsing, database/AI placeholders |
| `backend/app/dependencies.py` | 203 | Shared dependencies |
| `backend/app/api/router.py` | 189 | `/api/v1` router |
| `backend/app/api/v1/health.py` | 601 | Health endpoint |
| `backend/app/core/logging.py` | 828 | Logging setup |
| `backend/app/core/exceptions.py` | 4,005 | Error envelope and handlers |
| `backend/app/data_pipeline/psi_scraper.py` | 13,454 | Existing Playwright scraper |

Everything else under `backend/app` is a 0-byte placeholder: AI/RAG modules, models, schemas, scientific modules, services, parsers, the future PSI client, downloader, inventory, pipeline, validator and the investigation/dataset/comparison/analytics/chatbot API routes.

**Verification executed**

```text
backend\.venv\Scripts\python.exe -m pytest -q
.....                                                                    [100%]
5 passed in 3.14s
```

The global Python interpreter lacks FastAPI, so the project virtual environment is required. This is an environment fact, not a test failure.

### 1.3 Frontend

The frontend shell is implemented and builds successfully:

| Area | State |
| :--- | :--- |
| Layout / sidebar / header | Implemented |
| Dashboard | Implemented, 15,103 B |
| Investigations list | Implemented, 1,031 B |
| Investigation details | Placeholder, 1,460 B |
| Comparison / Assistant | Placeholders |
| API service | `services/api.ts` implemented (1,734 B); `investigationService.ts` is 0 B |
| Health hook | `hooks/useHealth.ts` implemented |
| Types | `types/index.ts` (914 B) |
| Charts / comparison / investigation components | Empty placeholders |

**Verification executed**

```text
npm run build
vite v6.4.6 building for production...
✓ 1601 modules transformed.
dist/assets/index-B-O9vpid.css   23.69 kB │ gzip: 5.00 kB
dist/assets/index-BMZT_uCR.js   228.66 kB │ gzip: 71.98 kB
✓ built in 6.88s
```

### 1.4 Docker and configuration

- `docker-compose.yml` defines PostgreSQL with the `pgvector/pgvector:pg16` image and a FastAPI backend built from `backend/Dockerfile`.
- The database has a health check and a persistent `postgres_data` volume.
- There is **no frontend service** in Compose and the root `Dockerfile` is empty.
- `.env.example` exists and is preserved.
- The backend configuration currently has no `MAX_FILE_SIZE_MB`; it will be added in the ingestion stage, not here.

### 1.5 What this audit did not change

- No existing backend module was modified.
- No frontend file was modified.
- No existing PSI metadata file was overwritten or deleted.
- No file under `data/knowledge/salma/` was read or touched.
- No database table, migration, parser, embedding or RAG component was created.
- Nothing was committed or pushed.

**Assessment:** the existing foundation is coherent and should be preserved. Stage 1 only adds a data-engineering audit layer on top of it.

---

## 2. Existing Scraper Assessment

### 2.1 What the scraper does

`backend/app/data_pipeline/psi_scraper.py` is a 519-line Playwright scraper:

- Opens `https://psi.nasa.gov/physci/repo/search?q=combustion&data_source=psi&data_type=investigation`.
- Launches **visible Chrome** (`headless=False`, `channel="chrome"`).
- Paginates by clicking the Angular Material next button and comparing link signatures.
- Expands `mat-expansion-panel` sections.
- Extracts the `description-panel`: project table rows plus sections with `h3` headings.
- Appends one JSON record per investigation to `data/metadata/psi_descriptions.jsonl`.
- Rewrites `psi_descriptions_numbered.md` and `psi_failed_ids.json` after each investigation.
- Retries each investigation twice with a 2-second delay.

### 2.2 Historical and current results

| Metric | Value |
| :--- | ---: |
| Investigations discovered | 26 |
| JSONL records written | 24 |
| Unique investigations in JSONL | 23 |
| Failed investigations | 3 |
| Duplicate record | PSI-117 (two byte-identical records) |
| Missing investigations | PSI-10, PSI-23, PSI-39 |

The duplicate arises because the JSONL is opened in append mode and the scraper has no idempotency check. The three failures are recorded in `psi_failed_ids.json`; the root cause was not diagnosed in the historical run.

### 2.3 Limitations

1. **Description-only.** The scraper has no concept of datasets, files, sizes, download URLs, MIME types or storage analytics.
2. **DOM-coupled.** It depends on `description-panel`, `div.ng-star-inserted`, `.indent`, `.contact-container`, `.tooltip` and Angular Material classes. A UI refresh breaks it silently.
3. **Not headless.** It requires a visible Chrome session, which is unsuitable for repeatable server-side ingestion.
4. **No idempotency.** Re-running appends duplicates instead of upserting.
5. **No provenance.** It does not record API version, retrieval timestamp, payload hash or field-level source.
6. **Partial field capture.** The project table has no DOI, keywords, related investigations, structured publications or contact roles.

### 2.4 Comparison with the official JSON API

| Capability | Playwright scraper | Official JSON API |
| :--- | :--- | :--- |
| Discovery of 26 combustion investigations | Yes, via UI pagination | Yes, `search?term=combustion&size=100` |
| Full descriptions | Yes, 23/26 | Yes, 26/26 |
| Structured contacts and roles | Partial | Yes |
| DOI, keywords, related investigations | No | Yes |
| File inventory and sizes | No | Yes |
| Dataset metadata | No | No dataset entity exists |
| Headless / server-side | No | Yes |
| Reproducible snapshot | No | Yes, stored under `data/metadata/psi_api/` |

**Assessment:** the Playwright scraper should be **retained as a fallback and manual verification tool**, but it must not remain the primary ingestion mechanism. Stage 4 should use the JSON API. No change was made to the scraper during Stage 1.

---

## 3. Existing Metadata Assessment

### 3.1 Files inspected

| File | Bytes | Contents |
| :--- | ---: | :--- |
| `data/metadata/psi_descriptions.jsonl` | 117,507 | 24 records, 23 unique investigations |
| `data/metadata/psi_descriptions_numbered.md` | 105,690 | Human-readable rendering of the same records |
| `data/metadata/psi_failed_ids.json` | 399 | PSI-10, PSI-39, PSI-23 |

### 3.2 Coverage

- Existing coverage: **23 of 26** investigations.
- Missing: **PSI-10, PSI-23, PSI-39**.
- The three missing investigations are available through the JSON API and are included in the new investigation inventory. The old failure is therefore no longer a blocker.
- All **7 pilots** are present.
- Every JSONL record has Objectives, Approach, Research Impacts and Contact(s); Hypothesis is missing for one record (PSI-108).
- Project tables contain between 4 and 7 fields. Common fields are Project Type, Sponsoring Agency, NASA Center, Investigation Start/End Date, Flight Platform and Proposal Title.

Section-level coverage across the 24 records:

| Section | Records |
| :--- | ---: |
| Objectives | 24 |
| Approach | 24 |
| Research Impacts/Earth Benefits | 24 |
| Contact(s) | 24 |
| Hypothesis | 23 |

### 3.3 Quality checks

- **Duplicate:** PSI-117 appears twice; the two records are byte-identical. It is harmless for reading but violates uniqueness.
- **Encoding:** the JSONL is valid UTF-8. Smart quotes, en dashes and bullets are preserved as proper Unicode (`U+2019`, `U+2013`, `U+2022`, etc.); there are no `U+FFFD` replacement characters.
- **Cross-source agreement:** for all 7 pilots, the normalized Objectives, Approach, Hypothesis and Research Impacts text in the JSONL is **character-for-character identical** to the official live API payload. The descriptions are trustworthy.
- **Missing structured fields:** the JSONL has no DOI, keywords, related investigations, publication records, contact emails or contact roles.
- **No file data:** the JSONL contains nothing about datasets, files, sizes or downloads.

### 3.4 Reuse decision

| Decision | Rationale |
| :--- | :--- |
| **Preserve** all existing files unchanged | They are valid historical artifacts and remain readable. |
| **Do not treat them as canonical** | They are incomplete (23/26), duplicated and missing structured fields. |
| **Use the official API as canonical** | Versioned snapshots under `data/metadata/psi_api/` provide 26/26 coverage and field-level provenance. |
| **Reuse descriptions later if needed** | The pilot text matches the API exactly, so no scientific information is lost. |

---

## 4. Investigation Inventory

### 4.1 Discovery

`GET https://psi.nasa.gov/geode-py/ws/repo/search?term=combustion&size=100` returns exactly **26** investigation records (`total = 26`, `n_hits = 26`). A full investigation payload is available at:

```text
GET https://psi.nasa.gov/geode-py/ws/repo/investigations/{PSI-ID}
```

The search payload and the per-investigation payload agree on every description field for all 7 pilots. The audit therefore treats the search payload as authoritative for the 19 non-pilot descriptions and the full payload as authoritative for the 7 pilots.

### 4.2 All 26 combustion investigations

| ID | Acronym | Title | Sub-research area | Platform | Start | End | Audit level |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| PSI-22 | ACME E-FIELD Flames | Advanced Combustion via Microgravity Experiments Electric-Field Effects on Laminar Diffusion Flames | Laminar Flames | ISS | 2016-11-18 | 2020-11-17 | description only |
| PSI-10 | ACME/Flame Design | Advanced Combustion via Microgravity Experiments / Flame Design | Flames of Gaseous Fuels | ISS | 1999-01-14 | 2025-04-30 | description only |
| PSI-159 | ACME CFI-G | Advanced Combustion via Microgravity Experiments / Cool Flames Investigation with Gases | Flames of Gaseous Fuels | ISS | — | — | description only |
| PSI-107 | SPICE | Smoke Point In Co-flow Experiment | Fire Safety | ISS | — | — | description only |
| PSI-106 | SLICE | Structure and Liftoff In Combustion Experiment | — | ISS | — | — | description only |
| PSI-100 | SAFFIRE-III | Spacecraft Fire Experiment-III | Spacecraft Fire Safety | ISS | 2017-04-18 | — | **full audit** |
| PSI-102 | SAME | Smoke and Aerosol Measurement Experiment | Spacecraft Fire Safety | ISS | 2001-03-02 | 2008-02-28 | **full audit** |
| PSI-69 | FLEX | Flame Extinguishment Experiment | Spacecraft Fire Safety | ISS | 2007-08-01 | 2016-07-31 | description only |
| PSI-39 | CFI | Cool Flames Investigation | Droplets | ISS | 2020-10-01 | 2021-10-20 | description only |
| PSI-21 | ACME CLD Flame | Advanced Combustion via Microgravity Experiments / Coflow Laminar Diffusion Flame | Flames of gaseous fuel | ISS | 2006-10-01 | 2022-05-31 | description only |
| PSI-68 | FLEX-2 | Flame Extinguishment Experiment - 2 | Spacecraft Fire Safety | ISS | 2016-08-12 | 2019-09-30 | description only |
| PSI-26 | BASS | Burning and Suppression of Solids | Spacecraft Fire Safety | ISS | 2009-10-01 | 2013-06-30 | **full audit** |
| PSI-117 | — | Effect of External Thermo-Convective Perturbation on Cool Flame Dynamics: A Multidimensional Multi-Physics CFD Analysis | Droplet | — | 2017-02-15 | 2022-02-14 | description only |
| PSI-23 | ACME s-Flame | Advanced Combustion via Microgravity Experiments-Structure and Response of Spherical Diffusion Flames | Flames of gaseous fuels | ISS | 2015-02-05 | 2019-11-24 | description only |
| PSI-20 | ACME BRE | Advanced Combustion via Microgravity Experiments - Burning Rate Emulator | Flames of Gaseous Fuels | ISS | 2010-01-01 | 2025-02-08 | description only |
| PSI-142 | — | Quantitative Studies of Cool Flame Transitions at Radiation / Stretch Extinction Using Counterflow Flames | Spacecraft Fire Safety | Not Applicable | 2016-08-01 | 2021-07-31 | description only |
| PSI-60 | — | Computational and Experimental Analysis of SPICE Data Sets | Gaseous | — | 2019-06-05 | 2022-08-29 | description only |
| PSI-62 | — | Concurrent Flame Spread Modeling using Flamelet Generated Manifolds in Microgravity with Comparison to BASS Experiments using Two-Color Tomography | Spacecraft Fire Safety | — | 2019-05-01 | 2021-04-30 | description only |
| PSI-99 | SAFFIRE-II | Spacecraft Fire Experiment-II | Surface Combustion | Cygnus | 2016-09-30 | 2017-04-01 | **full audit** |
| PSI-25 | BASS-II | Burning and Suppression of Solids - II | Spacecraft Fire Safety | ISS | 2010-01-01 | 2022-12-31 | **full audit** |
| PSI-115 | — | Utilization of the Smoke Aerosol Measurement Experiment Data for Advanced Modeling and Simulation of Smoke Generation in Micro-Gravity | Smoke Aerosol, Combustion Simulation | Not Applicable | 2017-01-30 | 2019-12-31 | description only |
| PSI-47 | DAFT / DAFT-2 | Dust and Aerosol Measurement Feasibility Test / Dust and Aerosol Measurement Feasibility Test-2 | Spacecraft Fire Safety | ISS | 2003-03-01 | 2009-06-01 | description only |
| PSI-98 | SAFFIRE-I | Spacecraft Fire Safety Experiment-I | Spacecraft Fire, Smoke Distribution | ISS | 2001-03-02 | 2008-02-28 | **full audit** |
| PSI-181 | — | Structure and Properties of Pb-Sn and Pb-free Sn-Ag-Cu Solders Produced in Terrestrial vs. Microgravity Environments under Extremes of Elevated and Cryo Temperatures | Microstructural Characterization, Terrestrial vs Microgravity Effects, Solder Joints | ISS | 2020-01-01 | 2022-12-31 | description only |
| PSI-108 | STDCE-1 | Surface Tension Driven Convection Experiment-1 | — | Space Shuttle | — | — | description only |
| PSI-101 | SAME-R | Smoke Aerosol Measurement Experiment-Reflight | Spacecraft Fire Safety | ISS | 2010-07-01 | 2010-09-30 | **full audit** |

Note: the search is a full-text “combustion” search. It includes PSI-181 (materials science) and PSI-108 (fluid physics) because their text matches the term, even though their research area is not Combustion Science. They are retained because PSI returned them, but the Data Contract should allow filtering by `research_area`.

### 4.3 Field completeness across all 26

| Field | Present | Notes |
| :--- | ---: | :--- |
| Title | 26/26 | Complete |
| Research area | 26/26 | Mostly Combustion Science; two exceptions |
| Objectives | 26/26 | Complete |
| Approach | 26/26 | Complete |
| Research impacts | 26/26 | Complete |
| Keywords | 26/26 | Delimited by multiple spaces; parsed into lists |
| Sponsoring agency / monitoring center | 26/26 | Complete |
| Project type | 26/26 | Microgravity or ground investigation |
| Hypothesis | 25/26 | Missing for PSI-108 |
| Sub-research area | 24/26 | Missing for PSI-106 and PSI-108 |
| Publication titles (structured or raw) | 24/26 | Missing for PSI-142 and PSI-181 |
| Flight platform | 23/26 | Missing for PSI-60, PSI-62, PSI-117 |
| Start date | 22/26 | Missing for PSI-106, PSI-107, PSI-108, PSI-159 |
| End date | 21/26 | Missing for PSI-100 and the four above |
| Related investigations | 16/26 | 21 internal edges plus one external target (PSI-77) |
| Experiment hardware | 20/26 | Structured name/link only for pilots and some others |
| Proposal title | 12/26 | Often empty even when a publication title exists |
| Acronym | 20/26 | Six investigations have no acronym |
| DOI | 7/26 | Present only on fully audited pilots |
| Contacts | 7/26 | Full contact records only on pilots |

### 4.4 Relationship graph

The 26 investigations expose **21 internal related-investigation edges** and one external target (PSI-77, which is outside the combustion search result). The Saffire, BASS and SAME families are internally connected:

```text
PSI-98  ↔ PSI-99, PSI-100, PSI-26
PSI-99  ↔ PSI-100
PSI-100 ↔ PSI-98, PSI-99
PSI-25  ↔ PSI-26
PSI-101 ↔ PSI-102
PSI-115 → PSI-102
PSI-47  → PSI-102
PSI-106 → PSI-107
PSI-39  → PSI-69
PSI-117 → PSI-69, PSI-142
PSI-142 → PSI-69
PSI-22  → PSI-23
PSI-62  → PSI-25, PSI-26
PSI-60  → PSI-107
```

These edges are stored as `relationships` in `investigations_inventory.json`. They are PSI-reported and should not be inferred or expanded by FlameLens without a provenance flag.

### 4.5 Pilot scientific profiles

The following summaries are grounded in the PSI description fields. Raw text is preserved verbatim in the inventory.

#### PSI-25 — BASS-II (Burning and Suppression of Solids - II)

- **DOI:** `10.60555/4qc4-de67` · **Hardware:** Microgravity Science Glovebox (MSG) · **Platform:** ISS · **Dates:** 2010-01-01 → 2022-12-31
- **Objectives:** improve combustion models used for fire detection and suppression; study ignition, flame growth, spread and extinction limits of solid fuels in low-velocity forced flow; bridge NASA-STD-6001 Test #1, ground microgravity tests and actual microgravity flammability; provide preliminary data for SoFIE; test realistic thicker fuels in slabs, cylinders and spherical sections. Primary variables: forced-flow speed and direction, ambient oxygen concentration, sample geometry.
- **Approach:** ISS tests in a small wind tunnel inside MSG, with airflow up to 40 cm/s and oxygen reduced below 21% by nitrogen vitiation; opposed and concurrent flow; flame appearance, growth and spread measured.
- **Hypothesis:** materials in microgravity with adequate ventilation burn as well as or better than in normal gravity under otherwise identical conditions; normal-gravity upward burning may not be conservative for space.
- **Data profile:** 695 files, 122 derived dataset groups, 255.770 GB; 296 MP4, 265 ZIP, 127 PDF; 276 files over limit (248.137 GB), 419 eligible (7.633 GB).

#### PSI-26 — BASS (Burning and Suppression of Solids)

- **DOI:** `10.60555/58h4-dy80` · **Hardware:** Microgravity Science Glovebox · **Platform:** ISS · **Dates:** 2009-10-01 → 2013-06-30
- **Objectives:** bridge normal-gravity NASA-STD-6001 Test #1, ground microgravity tests and actual microgravity flammability using longer flight times and realistic thick fuels, including wake flames; assess a gaseous extinguishing agent on different materials, geometries, preheating and flows.
- **Approach:** ISS MSG; cotton/fiberglass fabric, Nomex and Ultem samples; Kanthal igniter; variable-speed fan up to 40 cm/s; concurrent and opposed flow; flame size, shape, colour, spread rate and quenching recorded.
- **Hypothesis:** materials in microgravity with adequate ventilation burn as well as or better than in normal gravity; testing thicker materials requires long microgravity exposure.
- **Data profile:** 212 files, 42 dataset groups, 152.319 GB; 114 MP4, 60 ZIP, 32 PDF; 124 over limit (151.057 GB), 88 eligible (1.262 GB); contains the largest single file (8.380 GB ZIP).

#### PSI-98 — SAFFIRE-I (Spacecraft Fire Safety Experiment-I)

- **DOI:** `10.60555/0t15-1z43` · **Hardware:** Saffire 1 enclosure in Cygnus · **Platform:** ISS/Cygnus · **Dates reported:** 2001-03-02 → 2008-02-28 (**anomalous**, see GAP-008)
- **Objectives:** determine how rapidly a large-scale fire grows in low gravity and investigate low-g flammability limits relative to NASA's normal-gravity screening test.
- **Approach:** experiment on the uncrewed Cygnus after departure from ISS; SIBAL fabric (75% cotton, 25% fibreglass) approximately 0.94 m × 0.4 m; 20 cm/s airflow; two cameras, thermocouples, radiometers, pressure/CO₂/O₂ sensors and anemometers; data compressed and downlinked.
- **Hypothesis:** terrestrial fire standards carry unacceptable uncertainty for spacecraft; large-scale microgravity fire data are needed for fire-safe design.
- **Data profile:** 76 files, 16 dataset groups, 11.409 GB; 62 ZIP, 6 PDF, 4 XLSX; 19 over limit (10.143 GB), 57 eligible (1.266 GB); 85 historical removed files.

#### PSI-99 — SAFFIRE-II (Spacecraft Fire Experiment-II)

- **DOI:** `10.60555/2chp-m469` · **Hardware:** Cygnus Pressurized Cargo Module, SAFFIRE · **Platform:** Cygnus · **Dates:** 2016-09-30 → 2017-04-01
- **Objectives:** same core objectives as Saffire-I: large-scale fire growth and low-g flammability limits relative to normal-gravity screening.
- **Approach:** Cygnus flight after departure; nine samples (SIBAL, silicone, structure PMMA, flat PMMA, PMMA with Nomex), each 5 cm × 29 cm; 20 or 30 cm/s concurrent or opposed flow; two cameras, thermocouples, radiometers, pressure/CO₂/O₂ sensors, anemometers.
- **Hypothesis:** terrestrial fire standards are insufficient for spacecraft; large-scale microgravity fire data are required.
- **Data profile:** **only 2 files exposed** (experimental table CSV + metadata ZIP), 12.219 KB, although PSI reports 16,931,016,137 bytes. **This is the single major inventory gap.**

#### PSI-100 — SAFFIRE-III (Spacecraft Fire Experiment-III)

- **DOI:** `10.60555/040q-4h36` · **Hardware:** Saffire III enclosure in Cygnus · **Platform:** ISS/Cygnus · **Dates:** 2017-04-18 → *(missing)*
- **Objectives:** determine large-scale fire growth in low gravity and low-g flammability limits compared with normal-gravity screening.
- **Approach:** follow-on to Saffire-I using SIBAL at 30 cm/s (versus 20 cm/s), concurrent or opposed flow; same sensor suite; data compressed and downlinked.
- **Hypothesis:** terrestrial fire standards are insufficient for spacecraft; large-scale microgravity fire data are required.
- **Data profile:** 87 files, 16 dataset groups, 32.793 GB; 68 ZIP, 7 PDF, 6 XLSX, 3 CSV; 34 over limit (31.231 GB), 53 eligible (1.561 GB); 97 historical removed files.

#### PSI-101 — SAME-R (Smoke Aerosol Measurement Experiment-Reflight)

- **DOI:** `10.60555/2np7-jv14` · **Hardware:** Comparative Soot Diagnostic Hardware · **Platform:** ISS · **Dates:** 2010-07-01 → 2010-09-30
- **Objectives:** quantify liquid-smoke particle sizes in low gravity and relate droplet-size distribution to smoke generation and transport; improve on SAME after TEM grids were contaminated.
- **Approach:** SAME hardware with modifications: Pyrell intumescent foam replacing DBP, broader heating conditions (including no-flow during heating), and the in-house M-pass instrument replacing one Commercial Diagnostic Enclosure; 66 test points between 2010-07-16 and 2010-09-09; three post-flight ground tests to validate the lognormal assumption.
- **Hypothesis:** microgravity smoke particles grow larger than in 1 g because of higher vapour concentration and longer residence time; this changes detector response and may cause missed alarms.
- **Data profile:** 343 files, 136 dataset groups, 5.875 GB; 79 ZIP, 77 XLS, 76 PPTX, 45 CSV, 36 PDF, 8 MP4; 9 over limit (3.587 GB), 334 eligible (2.288 GB). **Best pilot for immediate end-to-end work.**

#### PSI-102 — SAME (Smoke and Aerosol Measurement Experiment)

- **DOI:** `10.60555/gd4k-8h62` · **Hardware:** Comparative Soot Diagnostic Hardware · **Platform:** ISS · **Dates:** 2001-03-02 → 2008-02-28
- **Objectives:** quantify smoke particulate sizes in low gravity and relate droplet-size distribution to generation and transport; develop a numerical code predicting smoke droplet growth from pyrolysis rate, thermodynamic properties and flow.
- **Approach:** crew-installed near-field hardware in the Glovebox, far-field box and video cameras; detector self-tests; 15–60 s igniter; thermophoretic soot samplers; ~2 min combustion events; post-flight TEM analysis, mass-loss weighing and 1 g matching.
- **Hypothesis:** microgravity smoke particles grow larger than in 1 g, reducing number density and potentially preventing smoke detectors from alarming.
- **Data profile:** 105 files, 49 dataset groups, 627.144 MB; 55 XLS, 27 PDF, 6 XLSX, 4 XML, 4 ZIP, 3 PPT, 2 PPTX, 2 MP4; 2 over limit (294.069 MB), 103 eligible (333.075 MB); 4 zero-byte XML files.

### 4.6 Investigation-level data quality findings

| Finding | Detail | Handling |
| :--- | :--- | :--- |
| PSI-98 date anomaly | Same start/end as PSI-102 (2001-03-02 → 2008-02-28), conflicting with the 2016 Saffire-I flight | Preserve PSI values; flag unverified; do not use for chronology |
| PSI-100 end date missing | Start 2017-04-18, no end date | Store `null`, never infer |
| Missing hypotheses | PSI-108 only | `null`; do not generate text |
| Missing platform | PSI-60, PSI-62, PSI-117 | `null` |
| Non-combustion results | PSI-181 (Materials Science), PSI-108 (Fluid Physics) | Keep, filter by research area in UI |
| No DOI / contacts for 19 | API search payload does not carry them | `null`; do not backfill from uncontrolled sources |

---

## 5. Dataset Inventory

### 5.1 Important definition

**NASA PSI does not expose a dataset entity.** The investigation payload has `added`, `experimentalTable`, `images`, `modified` and `removed` file arrays, but no dataset ID, dataset title, dataset description or dataset-to-file relationship beyond an optional free-text `subcategory`.

FlameLens therefore derives **logical dataset groups** deterministically:

```text
dataset = top-level filename category + PSI subcategory (run label)
dataset_id = "fld_" + first 12 hex chars of SHA-1("PSI-ID|category|subcategory")
```

Examples:

- `Raw Data / Reduced Gravity/Olson/O5`
- `Science Documents`
- `Engineering Documents`
- `Experimental table`
- `metadata`

Rules and caveats:

1. The top-level category is the text between the `<PSI-ID>_` prefix and the next underscore.
2. The PSI `subcategory` is trimmed and whitespace around `/` is collapsed.
3. Dataset IDs are **FlameLens-internal**, stable for a given grouping rule, and must not be presented as PSI-issued identifiers.
4. Dataset descriptions do not exist and must remain `null`.
5. Filename inconsistencies distort the grouping (see GAP-009). Manual corrections belong in the Data Contract, never in the raw PSI snapshot.

### 5.2 Counts

| Investigation | Derived dataset groups | Files | Singletons | Largest group (files) |
| :--- | ---: | ---: | ---: | ---: |
| PSI-25 | 122 | 695 | 5 | 13 |
| PSI-26 | 42 | 212 | 23 | 24 |
| PSI-98 | 16 | 76 | 2 | 14 |
| PSI-99 | 2 | 2 | 2 | 1 |
| PSI-100 | 16 | 87 | 2 | 16 |
| PSI-101 | 136 | 343 | 78 | 25 |
| PSI-102 | 49 | 105 | 29 | 28 |
| **Total** | **383** | **1,520** | **141** | **28** |

Across all 383 groups:

- 141 groups contain a single file.
- 24 groups contain more than 10 files.
- The largest group contains 28 files.
- Median group size is 14,308,288 bytes (13.645 MB).
- The smallest group is 239 bytes.
- 0 groups have a description.

### 5.3 Top-level categories

| Category | Groups | Files |
| :--- | ---: | ---: |
| Raw Data | 291 | 1,243 |
| Analyzed Data | 109 | 149 |
| Science Documents | 7 | 21 |
| Engineering Documents | 7 | 61 |
| Presentations | 4 | 15 |
| Experimental table | 7 | 7 |
| metadata | 6 | 6 |
| Reports | 5 | 6 |
| Reference Data | 3 | 6 |
| Representative Image(s) | 1 | 1 |
| SAME (filename anomaly) | 1 | 1 |
| **Total** | **383** | **1,520** |

### 5.4 Largest derived groups by size

| Investigation | Dataset group | Files | Bytes | Size |
| :--- | :--- | ---: | ---: | ---: |
| PSI-100 | Raw Data / Reduced Gravity/SAFFIRE-III S1C2 | 16 | 11,469,574,450 | 10.682 GB |
| PSI-26 | Raw Data / Reduced Gravity/2013_04_24 | 15 | 10,518,972,052 | 9.797 GB |
| PSI-100 | Raw Data / Reduced Gravity/SAFFIRE-III S1C1 | 16 | 10,208,845,593 | 9.508 GB |
| PSI-26 | Raw Data / Reduced Gravity/2013_05_18 | 11 | 9,484,772,872 | 8.833 GB |
| PSI-26 | Raw Data / Reduced Gravity/2012_05_12 | 1 | 8,997,566,948 | 8.380 GB |
| PSI-26 | Raw Data / Reduced Gravity/2013_04_27 | 15 | 8,626,326,912 | 8.034 GB |
| PSI-26 | Raw Data / Reduced Gravity/2012_07_12 | 1 | 8,583,694,205 | 7.994 GB |
| PSI-26 | Raw Data / Reduced Gravity/2013_04_10 | 10 | 8,382,537,214 | 7.807 GB |
| PSI-25 | Raw Data / Reduced Gravity/Fernandez-Pello/P3 | 12 | 8,252,691,113 | 7.686 GB |
| PSI-26 | Raw Data / Reduced Gravity/2013_04_13 | 14 | 7,990,394,722 | 7.442 GB |

### 5.5 Missing dataset metadata

| Missing item | Status | Consequence |
| :--- | :--- | :--- |
| PSI dataset identifier | Does not exist | FlameLens IDs are derived |
| Dataset title | Does not exist | Display name is the derived group name |
| Dataset description | Does not exist | UI must show “derived group” and “no PSI description” |
| Dataset-level relationships | Do not exist | Only investigation-level relationships are available |
| Dataset version | Does not exist | File-level `version` is the only version signal |
| Per-file description | Does not exist | Do not invent labels beyond the filename |

**Recommendation:** the Data Contract (Stage 2) must model both `psi_dataset_id` (nullable, for future PSI support) and `flamelens_dataset_id` plus a `derivation` field. The UI must never imply that a derived group is an official PSI dataset.

---

## 6. File Inventory

### 6.1 Inclusion rule

A current file is any file appearing in the investigation payload's `added`, `experimentalTable`, `images` or `modified` arrays. Files are deduplicated by `s3_path` (falling back to `remote_path`, then filename).

- `removed` entries are **historical versions**, not current files. They are excluded from current storage totals and preserved separately under `historical_removed_files`.
- The union is stable and deterministic: ordering follows `added`, `experimentalTable`, `images`, `modified`.
- One duplicate was found: `PSI-25_Representative Image(s)_BASS-II_flame testing.jpg` appears in both `added` and `images`. It is counted once and records both source fields.

Raw array composition:

| Investigation | added | experimentalTable | images | modified | Duplicates | Current union | removed |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| PSI-25 | 694 | 1 | 1 | 0 | 1 | 695 | 131 |
| PSI-26 | 211 | 1 | 0 | 0 | 0 | 212 | 24 |
| PSI-98 | 74 | 1 | 0 | 1 | 0 | 76 | 85 |
| PSI-99 | 0 | 1 | 0 | 1 | 0 | 2 | 0 |
| PSI-100 | 85 | 1 | 0 | 1 | 0 | 87 | 97 |
| PSI-101 | 342 | 1 | 0 | 0 | 0 | 343 | 379 |
| PSI-102 | 104 | 1 | 0 | 0 | 0 | 105 | 52 |
| **Total** | **1,510** | **7** | **1** | **3** | **1** | **1,520** | **768** |

### 6.2 File record schema

Every current file in `files_inventory.json` carries:

| Field | Type | Meaning |
| :--- | :--- | :--- |
| `file_id` | string | Deterministic FlameLens ID: `flf_` + SHA-1(`investigation_id|s3_path`)[:16] |
| `investigation_id` | string | PSI accession, e.g. `PSI-25` |
| `dataset_id` / `dataset_name` | string | Derived dataset group |
| `lifecycle_status` | string | `current` or `removed_historical_version` |
| `filename` | string | Original PSI filename, preserved verbatim |
| `extension` | string | Lower-case suffix, e.g. `.mp4` |
| `mime_type` | string | Deterministic MIME type |
| `format_category` | string | `structured`, `document`, `scientific`, `image`, `video`, `archive`, `other` |
| `psi_subcategory` | string/null | PSI run label |
| `description` | null | PSI provides none |
| `source_fields` | array | Which PSI arrays contained the file |
| `remote_path` | string | PSI path under `/Home/psi-data/...` |
| `s3_path` | string | PSI S3 key, e.g. `psi-data/PSI-25/...` |
| `bucket` | string | PSI S3 bucket when exposed |
| `psi_file_version` | integer | PSI file version used by the download endpoint |
| `size_bytes` | integer | Remote size reported by PSI |
| `size_known` | boolean | `false` when PSI omits a size |
| `empty_file` | boolean | `true` when PSI reports 0 B |
| `download_url` | string | Modern PSI endpoint that returns a signed S3 URL |
| `download_url_requires_signed_redirect` | boolean | Always `true` |
| `legacy_remote_url` | string/null | Dead legacy URL, preserved for traceability |
| `legacy_url_status` | string | `DEAD_HOST_DNS_FAILURE`, `RELATIVE_PATH_404`, `NOT_PROVIDED` or `UNVERIFIED` |
| `download_eligible` | boolean | Size known and ≤ `MAX_FILE_SIZE_MB` |
| `download_status` | string | `PENDING`, `OVER_LIMIT`, `UNKNOWN_SIZE` or `HISTORICAL_REMOVED` |
| `manual_approval_required` | boolean | `true` for over-limit files |
| `downloaded` | boolean | `false` for all files at Stage 1 |
| `local_size_bytes` / `local_path` / `sha256` | null | Populated only after a verified download |
| `parsing_status` | string | `NOT_PARSED` for all files at Stage 1 |
| `restricted` / `visible` | boolean | PSI access flags |
| `psi_created_at_utc` / `psi_modified_at_utc` | string/null | PSI timestamps |
| `discovered_at_utc` | string | Inventory generation timestamp |

### 6.3 Per-investigation file flags

| Investigation | Files | Known size | Unknown size | Zero-byte | Over limit | Eligible | Removed |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| PSI-25 | 695 | 695 | 0 | 0 | 276 | 419 | 131 |
| PSI-26 | 212 | 212 | 0 | 0 | 124 | 88 | 24 |
| PSI-98 | 76 | 76 | 0 | 0 | 19 | 57 | 85 |
| PSI-99 | 2 | 2 | 0 | 0 | 0 | 2 | 0 |
| PSI-100 | 87 | 87 | 0 | 0 | 34 | 53 | 97 |
| PSI-101 | 343 | 343 | 0 | 0 | 9 | 334 | 379 |
| PSI-102 | 105 | 105 | 0 | 4 | 2 | 103 | 52 |
| **Total** | **1,520** | **1,520** | **0** | **4** | **464** | **1,056** | **768** |

Global access flags:

- `restricted = true`: **0**
- `visible = false`: **0**
- Files with unknown size: **0**
- Files with size 0 B: **4** (all in PSI-102, all `.xml`)

### 6.4 Representative records

Eligible file (PSI-25 video):

```json
{
  "file_id": "flf_f183fb4632b87a66",
  "investigation_id": "PSI-25",
  "dataset_name": "Raw Data / Reduced Gravity/Bhattacharjee/B1",
  "filename": "PSI-25_Raw Data_BASS_GMT50_SAMPLE_147_TEST_B1.mp4",
  "extension": ".mp4",
  "mime_type": "video/mp4",
  "format_category": "video",
  "size_bytes": 5803980,
  "size_known": true,
  "download_eligible": true,
  "download_status": "PENDING",
  "legacy_url_status": "DEAD_HOST_DNS_FAILURE",
  "downloaded": false,
  "parsing_status": "NOT_PARSED"
}
```

Over-limit file (PSI-26 archive):

```json
{
  "filename": "PSI-26_Raw Data_2012_05_12_orig.zip",
  "size_bytes": 8997566948,
  "download_eligible": false,
  "download_status": "OVER_LIMIT",
  "manual_approval_required": true
}
```

Zero-byte file (PSI-102 XML):

```json
{
  "filename": "PSI-102_Analyzed Data_16937___9.xml",
  "size_bytes": 0,
  "empty_file": true,
  "download_status": "PENDING"
}
```

### 6.5 Historical removed files

| Investigation | Removed files | Removed bytes |
| :--- | ---: | ---: |
| PSI-25 | 131 | 26,189,378,205 |
| PSI-26 | 24 | 5,889,117 |
| PSI-98 | 85 | 12,265,492,754 |
| PSI-99 | 0 | 0 |
| PSI-100 | 97 | 35,286,706,087 |
| PSI-101 | 379 | 6,624,863,611 |
| PSI-102 | 52 | 434,107,870 |
| **Total** | **768** | **80,806,437,644 (75.257 GB)** |

There is **zero S3-path overlap** between current and removed files. Removed files are preserved in the inventory for traceability but are not part of “total available data.”

---

## 7. File Format Distribution

### 7.1 Global distribution

| Extension | Files | Total bytes | Size | Category |
| :--- | ---: | ---: | ---: | :--- |
| `.zip` | 539 | 446,851,456,715 | 416.163 GB | archive |
| `.mp4` | 420 | 44,198,354,512 | 41.163 GB | video |
| `.pdf` | 235 | 288,680,914 | 275.308 MB | document |
| `.xls` | 132 | 702,551,552 | 670.005 MB | structured |
| `.pptx` | 81 | 277,665,113 | 264.802 MB | document |
| `.csv` | 53 | 34,600,186 | 32.997 MB | structured |
| `.xlsx` | 35 | 150,245,683 | 143.285 MB | structured |
| `.docx` | 10 | 43,545,347 | 41.528 MB | document |
| `.ppt` | 5 | 58,902,528 | 56.174 MB | document |
| `.xml` | 4 | 0 | 0 B | scientific |
| `.tif` | 3 | 1,788,025 | 1.705 MB | image |
| `.doc` | 2 | 1,749,504 | 1.668 MB | document |
| `.jpg` | 1 | 37,525 | 36.646 KB | image |
| **Total** | **1,520** | **492,609,577,604** | **458.778 GB** | |

Category totals:

| Category | Files | Bytes | Share of bytes |
| :--- | ---: | ---: | ---: |
| archive | 539 | 446,851,456,715 | 90.71% |
| video | 420 | 44,198,354,512 | 8.97% |
| structured | 220 | 887,397,421 | 0.18% |
| document | 333 | 670,543,406 | 0.14% |
| image | 4 | 1,825,550 | 0.0004% |
| scientific | 4 | 0 | 0% |

### 7.2 Per-investigation matrix

| Extension | PSI-25 | PSI-26 | PSI-98 | PSI-99 | PSI-100 | PSI-101 | PSI-102 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `.zip` | 265 | 60 | 62 | 1 | 68 | 79 | 4 |
| `.mp4` | 296 | 114 | 0 | 0 | 0 | 8 | 2 |
| `.pdf` | 127 | 32 | 6 | 0 | 7 | 36 | 27 |
| `.xls` | 0 | 0 | 0 | 0 | 0 | 77 | 55 |
| `.pptx` | 1 | 2 | 0 | 0 | 0 | 76 | 2 |
| `.csv` | 1 | 1 | 1 | 1 | 3 | 45 | 1 |
| `.xlsx` | 2 | 2 | 4 | 0 | 6 | 15 | 6 |
| `.docx` | 2 | 1 | 3 | 0 | 3 | 1 | 0 |
| `.ppt` | 0 | 0 | 0 | 0 | 0 | 2 | 3 |
| `.xml` | 0 | 0 | 0 | 0 | 0 | 0 | 4 |
| `.tif` | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| `.doc` | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| `.jpg` | 1 | 0 | 0 | 0 | 0 | 0 | 0 |

### 7.3 Observations

1. **ZIP dominance is the central storage fact.** 35.5% of files hold 90.71% of bytes. ZIP contents are opaque until download and extraction. No claim can be made about the formats inside them at Stage 1.
2. **Video is the second major block.** 420 MP4 files hold 41.163 GB; 410 of them belong to PSI-25 and PSI-26. PSI-98 and PSI-100 expose no standalone MP4 files — their imagery appears to be inside ZIP archives.
3. **Scientific text formats are almost absent.** There is **no HDF5, NetCDF, FITS or JSON**. The only `.xml` files are four zero-byte PSI-102 files. Any scientific workflow that assumes HDF5/NetCDF would be wrong for these pilots.
4. **Structured data is concentrated in SAME/SAME-R.** PSI-101 and PSI-102 hold 192 of the 220 structured files (`.csv`, `.xls`, `.xlsx`). PSI-25/26/98/100 expose only 13 structured files in total.
5. **Images are negligible in the exposed listing.** Only 1 JPG and 3 TIFF files (1.741 MB total). Most imagery is inside ZIPs.
6. **File sizes are extremely skewed.** Median = 12.332 MB, mean = 309.072 MB, 90th percentile = 1,007.396 MB, maximum = 8.380 GB.

---

## 8. Available Remote Storage Size per Investigation

### 8.1 Two different numbers

- **Remote inventory size** — the sum of file sizes that PSI exposes through the API.
- **Local downloaded size** — the sum of files actually downloaded and verified locally.

At Stage 1 the local size is **0 B** for every investigation. No remote number in this section is a local storage measurement.

### 8.2 Per-investigation storage

| Investigation | Files | Remote inventory | PSI reported | Difference | Listing complete? | Over limit | Eligible (≤100 MiB) | Local |
| :--- | ---: | ---: | ---: | ---: | :---: | ---: | ---: | ---: |
| PSI-25 BASS-II | 695 | 274,631,106,141 B (255.770 GB) | 274,631,106,141 | 0 | yes | 276 / 248.137 GB | 419 / 7.633 GB | 0 B |
| PSI-26 BASS | 212 | 163,551,372,412 B (152.319 GB) | 163,551,372,412 | 0 | yes | 124 / 151.057 GB | 88 / 1.262 GB | 0 B |
| PSI-98 SAFFIRE-I | 76 | 12,250,599,959 B (11.409 GB) | 12,250,600,201 | −242 | yes* | 19 / 10.143 GB | 57 / 1.266 GB | 0 B |
| PSI-99 SAFFIRE-II | 2 | 12,512 B (12.219 KB) | 16,931,016,137 | −16,931,003,625 | **no** | 0 / 0 B | 2 / 12.219 KB | 0 B |
| PSI-100 SAFFIRE-III | 87 | 35,210,764,689 B (32.793 GB) | 35,210,765,052 | −363 | yes* | 34 / 31.231 GB | 53 / 1.561 GB | 0 B |
| PSI-101 SAME-R | 343 | 6,308,113,713 B (5.875 GB) | 6,308,124,750 | −11,037 | yes* | 9 / 3.587 GB | 334 / 2.288 GB | 0 B |
| PSI-102 SAME | 105 | 657,608,178 B (627.144 MB) | 657,608,178 | 0 | yes | 2 / 294.069 MB | 103 / 333.075 MB | 0 B |
| **Total** | **1,520** | **492,609,577,604 B (458.778 GB)** | **509,540,592,871** | **−16,931,015,267** | **no** | **464 / 444.442 GB** | **1,056 / 14.337 GB** | **0 B** |

`*` Complete for the exposed listing; the difference is ≤ 1 MiB and is recorded as accounting noise (GAP-004), not as missing files.

### 8.3 Global reconciliation

| Quantity | Bytes | Human |
| :--- | ---: | ---: |
| Sum of current files | 492,609,577,604 | 458.778 GB |
| PSI `totalFileSize` | 509,540,592,871 | 474.547 GB |
| Difference | −16,931,015,267 | −15.770 GB |
| Difference excluding PSI-99 | −11,642 | −11.371 KB |
| PSI-99 gap | 16,931,003,625 | 15.768 GB |

The conclusion is unambiguous: **the six fully listed pilots reconcile almost exactly; PSI-99 is the sole material discrepancy.**

### 8.4 “Remote inventory complete” semantics

`storage_summary.json` separates two ideas:

- `remote_inventory_size_bytes` — the sum of everything PSI listed.
- `remote_inventory_complete` — whether PSI's own reported total agrees with that sum.

For PSI-99, `remote_inventory_complete = false` and `remote_inventory_is_known_size_subtotal = true`. The UI must display a “known-size subtotal” or “incomplete listing” badge for this investigation rather than presenting 12.219 KB as the total available data.

---

## 9. Unknown File Sizes

### 9.1 Per-file unknowns

**There are zero files with unknown remote size among the 1,520 current files.** PSI reports a numeric `file_size` for every exposed file.

This is an unusually clean result, but it does **not** mean every size is trustworthy:

- 4 files report **0 B** (PSI-102 XML files). These are “known but suspicious” rather than “unknown.”
- All 768 historical removed files also have numeric sizes; 4 of them report 0 B.

### 9.2 Listing-level unknowns

PSI-99 is a different kind of unknown. The API exposes only 2 files but reports a 16.93 GB total. FlameLens does not know:

- how many files are missing,
- their names or formats,
- their individual sizes,
- whether the missing files are raw video, archives or documents.

The 12.219 KB exposed size must **never** be presented as PSI-99's total. It is a known-size subtotal of a demonstrably incomplete listing.

### 9.3 Rules adopted

1. Never invent a remote size when PSI omits one.
2. Never infer a size from a filename, a sibling file or a reported total.
3. Preserve `size_bytes = 0` as 0; do not silently convert it to unknown.
4. Label partial totals explicitly as `remote_inventory_is_known_size_subtotal`.
5. Treat “number of files” as incomplete whenever PSI's reported total exceeds the listed total by more than 1 MiB.
6. During downloads, verify the actual `Content-Range` total against the inventory before marking a file complete.

---

## 10. Download Limitations

### 10.1 Policy

| Setting | Value |
| :--- | :--- |
| Environment variable | `MAX_FILE_SIZE_MB` |
| Default | `100` |
| Byte threshold | 104,857,600 B |
| Files over limit | Inventoried, `OVER_LIMIT`, `manual_approval_required = true`, never downloaded automatically |
| Files within limit | `PENDING`, eligible for automatic download |
| Unknown size | `UNKNOWN_SIZE`, no automatic download |
| Partial downloads | Must never be recorded as complete |

### 10.2 Impact of the 100 MiB threshold

| Investigation | Eligible files | Eligible bytes | Byte share eligible | Over-limit files | Over-limit bytes |
| :--- | ---: | ---: | ---: | ---: | ---: |
| PSI-25 | 419 | 8,196,397,466 | 2.98% | 276 | 266,434,708,675 |
| PSI-26 | 88 | 1,355,364,563 | 0.83% | 124 | 162,196,007,849 |
| PSI-98 | 57 | 1,359,474,962 | 11.10% | 19 | 10,891,124,997 |
| PSI-99 | 2 | 12,512 | 100% | 0 | 0 |
| PSI-100 | 53 | 1,676,254,343 | 4.76% | 34 | 33,534,510,346 |
| PSI-101 | 334 | 2,457,135,852 | 38.95% | 9 | 3,850,977,861 |
| PSI-102 | 103 | 349,254,510 | 53.11% | 2 | 308,353,668 |
| **Global** | **1,056** | **15,393,894,208** | **3.12%** | **464** | **477,215,683,396** |

By count, 69.47% of files are eligible. By bytes, only 3.12% are. The limit therefore gives broad **document and table** coverage but very little **raw experiment** coverage for BASS and Saffire.

### 10.3 Verified download mechanism

The audit probed 9 files (one or more per pilot) with `Range: bytes=0-0` only:

| Investigation | File | Endpoint | S3 HEAD | Range | Size returned | Inventory match |
| :--- | :--- | ---: | ---: | ---: | ---: | :---: |
| PSI-25 | Experimental table CSV | 200 | 403 | 206 | 16,590 | yes |
| PSI-25 | Raw Data MP4 | 200 | 403 | 206 | 5,803,980 | yes |
| PSI-25 | Metadata ZIP | 200 | 403 | 206 | 13,439 | yes |
| PSI-26 | Experimental table CSV | 200 | 403 | 206 | 4,726 | yes |
| PSI-98 | Experimental table CSV | 200 | 403 | 206 | 469 | yes |
| PSI-99 | Experimental table CSV | 200 | 403 | 206 | 1,973 | yes |
| PSI-100 | Experimental table CSV | 200 | 403 | 206 | 239 | yes |
| PSI-101 | Experimental table CSV | 200 | 403 | 206 | 5,674 | yes |
| PSI-102 | Experimental table CSV | 200 | 403 | 206 | 331 | yes |

All 9 sizes match the inventory exactly. The signed URLs point at `psi-repo-prod.s3.amazonaws.com` or `psi-curation-prod.s3.amazonaws.com` and carry expiry parameters. Full details are in `data/metadata/psi_api/download_probe.json`.

### 10.4 Legacy URLs are dead

| Legacy status | Files | Meaning |
| :--- | ---: | :--- |
| `DEAD_HOST_DNS_FAILURE` | 1,506 | `psi.ndc.nasa.gov` no longer resolves |
| `RELATIVE_PATH_404` | 14 | `/datamanager/file/...` returns HTTP 404 |
| **Total** | **1,520** | **0 usable legacy URLs** |

Direct S3 or legacy-host downloads must never be implemented. Every transfer must start at the modern endpoint.

### 10.5 Implementation constraints for Stage 4

1. Call the download endpoint per file and follow the returned signed URL immediately.
2. Never persist signed URLs; they expire and contain credentials.
3. Do not use `HEAD` to discover size; S3 returns 403. Use `Range: bytes=0-0` and read `Content-Range`.
4. Verify the `Content-Range` total against the inventory size before and after transfer.
5. Use resumable downloads with retries; re-resolve the signed URL on expiry.
6. Record checksum and local size only after a complete transfer.
7. Mark over-limit files `OVER_LIMIT`; never truncate them.
8. Treat a zero-byte `Content-Range` response as a legitimate but separately flagged result.
9. Keep `remote_size_bytes` and `local_size_bytes` distinct in the database.
10. Recompute storage summaries from current files only; exclude historical removed files and duplicates.

---

## 11. Data Availability Gaps

| ID | Severity | Investigation | Gap | Recommended action |
| :--- | :--- | :--- | :--- | :--- |
| GAP-001 | **High** | PSI-99 | API lists 2 files (12,512 B) but PSI reports 16,931,016,137 B. `added` and `removed` are empty. Raw data, videos and science documents are absent. | Manually inspect the PSI web UI; retry with an authenticated session or report to PSI. Do not present 12.219 KB as the total. |
| GAP-002 | Medium | All | PSI exposes no dataset entity or dataset descriptions. | Model derived datasets explicitly with a `derivation` flag; never label them as PSI datasets. |
| GAP-003 | Medium | All | Legacy per-file URLs are dead (1,506 DNS failures, 14 HTTP 404). | Use only the `/geode-py/ws/studies/{id}/download` endpoint, with fresh signed URLs. |
| GAP-004 | Low | PSI-98, PSI-100, PSI-101 | Small unexplained delta between summed sizes and `totalFileSize` (−242, −363, −11,037 B). | Record in ingestion runs; monitor for growth. |
| GAP-005 | Low | 19 non-pilots | Only 7 investigations have file/dataset inventories. | Extend ingestion to all 26 after the pilot pipeline is validated. |
| GAP-006 | Low | All | PSI provides no per-file descriptions. | Derive display labels from filenames only; do not invent descriptions. |
| GAP-007 | Medium | PSI-102 | Four current XML files report 0 B, plus four historical removed files. | Probe each with `Range: bytes=0-0`; never report a zero-byte download as a successful parse. |
| GAP-008 | Medium | PSI-98 | Start/end dates are identical to PSI-102 and conflict with the 2016 Saffire-I flight. PSI-100 has no end date. | Preserve and flag as unverified; do not use for chronological inference without confirmation. |
| GAP-009 | Low | PSI-25, PSI-101 | Filename inconsistencies create misleading category labels. | Keep the derivation flag; allow manual dataset corrections in the Data Contract. |

### 11.1 Gap priority

1. **GAP-001** blocks any claim that PSI-99 is a usable pilot. It must be resolved or explicitly accepted as a partial pilot.
2. **GAP-002** and **GAP-003** are architectural and must be encoded in the Data Contract before ingestion.
3. **GAP-007** and **GAP-008** are data-quality issues that require explicit handling, not silent normalization.
4. **GAP-004**, **GAP-005**, **GAP-006** and **GAP-009** are manageable technical debt.

---

## 12. Recommended Next Steps

### 12.1 Immediate (before Stage 2)

1. **Approve this audit.** No dependent work should begin until the numbers, definitions and gaps are accepted.
2. **Decide the PSI-99 policy.** Options:
   - manually inspect the PSI UI and retry the API before Stage 2;
   - accept PSI-99 as a partial pilot and exclude it from “complete inventory” claims;
   - defer PSI-99 to a later manual-approval workflow.
3. **Decide the dataset semantics.** Confirm that 383 derived groups are acceptable as the V1 dataset model, or request a coarser grouping (for example, top-level category only) before the Data Contract fixes the IDs.
4. **Decide snapshot retention.** Keep `data/metadata/psi_api/` versioned as the audit's evidence. Re-capture only with an explicit refresh, and record the capture timestamp and hashes.

### 12.2 Stage 2 — Data Contract requirements derived from this audit

The contract must include:

- **Investigation:** PSI accession, title, acronym, research area, sub-area, platform, hardware, dates (raw + ISO), DOI, keywords, contacts, publications, related investigations, description fields, provenance and API version.
- **Dataset:** `psi_dataset_id` (nullable), `flamelens_dataset_id`, derivation rule, category, subcategory, description presence flag, file count and totals.
- **Data file:** all fields listed in §6.2, including `empty_file`, `size_known`, legacy URL status, signed-URL requirement, download status and parsing status.
- **Storage summary:** remote vs local, known-size subtotal, listing completeness, over-limit and eligible buckets, historical removed totals, and the exact calculation rules.
- **Ingestion run:** snapshot timestamp, payload hashes, discovery counts, per-stage errors, retries and reconciliation deltas.
- **Quality issue:** GAP IDs, severity, affected entity and resolution status.
- **Provenance:** every derived field must state whether it is PSI-reported, PSI-derived, FlameLens-derived or analyst-provided.

### 12.3 Stage 4 — Ingestion pipeline requirements

- Use the JSON API, not HTML scraping, as the primary client.
- Take the **union** of `added`, `experimentalTable`, `images` and `modified`; deduplicate by `s3_path`.
- Store `removed` separately; exclude it from current totals.
- Preserve original filenames, PSI paths, versions, timestamps and legacy URLs.
- Generate deterministic file and dataset IDs (the audit's hash scheme can be reused).
- Verify every download with `Range` and `Content-Range`; never trust `HEAD`.
- Re-resolve signed URLs on retry or expiry.
- Never claim a partial or zero-byte file is complete.
- Compute checksums for every successful download.
- Reconcile per-investigation totals against `totalFileSize` and record deltas.
- Make the run idempotent and resumable; never append duplicate descriptions.

### 12.4 Stage 5 — Pilot selection recommendation

The original Stage 5 pilot set (PSI-25, PSI-26, PSI-98, PSI-100) is scientifically central but operationally expensive:

- 96.9% of their combined bytes are over the 100 MiB limit.
- Their raw data is overwhelmingly inside multi-gigabyte ZIPs and videos.
- Only 13 structured files are exposed across all four.

Recommended sequence:

1. **Validate the end-to-end pipeline on PSI-101 (SAME-R) and PSI-102 (SAME)** first. They have 334 + 103 eligible files, 2.288 GB + 333.075 MB of accessible data, and 192 structured files.
2. **Then validate PSI-25, PSI-26, PSI-98 and PSI-100 metadata, file inventory and small downloadable files** without attempting the raw archives.
3. **Only after explicit approval**, add a selected-large-file workflow for the raw ZIP/video data and re-run the scientific validation.

This sequence proves download, checksum, parsing, provenance and storage analytics on tractable data before spending bandwidth on tens of gigabytes.

### 12.5 Housekeeping

- The exploratory `_tmp_*` scripts and `_tmp_psi_live/` artifacts remain untracked. They can be removed after approval, but only with explicit permission.
- The stable evidence is now `data/metadata/psi_api/` plus the two audit scripts.
- Recommend a logical commit after approval containing:
  - `docs/data-engineering/01_psi_data_source_audit.md`
  - `data/metadata/investigations_inventory.json`
  - `data/metadata/datasets_inventory.json`
  - `data/metadata/files_inventory.json`
  - `data/metadata/storage_summary.json`
  - `data/metadata/psi_api/` snapshot and probe results
  - `scripts/audit_psi_source.py`
  - `scripts/probe_psi_download.py`

No commit has been made.

---

## Appendix A — Reproducibility

### A.1 Commands

```text
python scripts/audit_psi_source.py --check
python scripts/probe_psi_download.py --write
backend\.venv\Scripts\python.exe -m pytest -q
cd frontend && npm run build
```

### A.2 Audit generator output

```text
PSI Stage 1 audit inventories written
  investigations: 26 (full audit: 7, description only: 19)
  datasets:       383
  current files:  1520 (458.778 GB)
  over limit:     464 (444.442 GB)
  eligible:       1056 (14.337 GB)
  complete:       False

Per investigation:
  ID        files datasets  remote size  over eligible
  PSI-25      695      122   255.770 GB   276      419
  PSI-26      212       42   152.319 GB   124       88
  PSI-98       76       16    11.409 GB    19       57
  PSI-99        2        2    12.219 KB     0        2
  PSI-100      87       16    32.793 GB    34       53
  PSI-101     343      136     5.875 GB     9      334
  PSI-102     105       49   627.144 MB     2      103

Reconciliation checks passed.
```

### A.3 Snapshot

| Artifact | Purpose |
| :--- | :--- |
| `data/metadata/psi_api/investigations/PSI-*.json` | Official payloads for the 7 pilots |
| `data/metadata/psi_api/search_combustion.json` | Official 26-hit combustion search |
| `data/metadata/psi_api/search_accessions.json` | Compact accession list |
| `data/metadata/psi_api/manifest.json` | Capture timestamps, source URLs and byte sizes |
| `data/metadata/psi_api/download_probe.json` | 9-file Range probe evidence |

Per-investigation SHA-256 hashes are stored in `investigations_inventory.json`.

### A.4 Reconciliation checks

The generator verifies:

- unique `file_id` values;
- unique `dataset_id` values;
- exact dataset coverage of the current file set;
- dataset file counts and sizes;
- per-investigation counts and totals against the file inventory;
- global totals against the investigation rows;
- every file has a valid `PENDING` or `OVER_LIMIT` status;
- eligible files are never over limit;
- investigation counts reconcile with storage rows.

All checks passed.

---

## Appendix B — Inventory File Schemas

### B.1 `investigations_inventory.json`

Top-level keys:

- `schema_version`, `generated_at_utc`, `description`
- `source` — endpoints, snapshot directory, capture time, search total
- `counts` — total, full audit, description only, file inventory, structured publications, existing JSONL records
- `field_completeness` — counts per field
- `relationships` — internal related-investigation edges
- `external_relationship_targets` — targets outside the 26
- `investigations` — 26 records

Each investigation record includes identity, scientific fields, contacts, publications, description text, field presence, audit level, provenance and existing-metadata status.

### B.2 `datasets_inventory.json`

Top-level keys:

- `schema_version`, `generated_at_utc`, `description`
- `method` — derivation rule, subcategory normalization, known filename anomalies
- `counts` — total and per-investigation dataset counts
- `datasets` — 383 records with `dataset_id`, name, category, subcategory, file count, size, format distribution and file IDs

### B.3 `files_inventory.json`

Top-level keys:

- `schema_version`, `generated_at_utc`, `description`
- `download_policy`
- `counts`
- `format_distribution` — by extension, category and MIME type
- `files` — 1,520 current records
- `historical_removed_files` — 768 records with `lifecycle_status = removed_historical_version`

### B.4 `storage_summary.json`

Top-level keys:

- `schema_version`, `generated_at_utc`, `description`
- `units` — binary conversion rules
- `download_policy`
- `global` — counts, remote total, reported total, delta, completeness, local total, format distributions
- `investigations` — per-pilot storage rows with file counts, storage buckets, formats, largest files, removed totals and notes
- `investigations_without_file_inventory` — the 19 description-only investigations
- `data_gaps` — GAP-001 through GAP-009

---

## Appendix C — Verification Log

| Check | Command | Result |
| :--- | :--- | :--- |
| Backend tests | `backend\.venv\Scripts\python.exe -m pytest -q` | **5 passed** in 3.14s |
| Frontend build | `npm run build` | **Passed**, 1,601 modules, 6.88s |
| Audit generation | `python scripts/audit_psi_source.py --check` | **Passed**, reconciliation clean |
| JSON parse | parse all four inventories | **Passed** |
| Download probe | `python scripts/probe_psi_download.py --write` | **9/9** endpoint 200, Range 206, sizes match |
| Legacy URL probe | HTTP requests to `psi.ndc.nasa.gov` and relative paths | DNS failure / HTTP 404 |
| Existing JSONL validation | UTF-8, duplicates, cross-source comparison | Valid UTF-8; 1 duplicate; pilot text matches API exactly |

**Not executed in Stage 1:** database migrations, ingestion, parsers, checksum verification of downloaded files, embeddings, RAG, frontend integration. These belong to later stages and were intentionally out of scope.

---

## Appendix D — Deliverables Checklist

| Deliverable | Status |
| :--- | :--- |
| `docs/data-engineering/01_psi_data_source_audit.md` | Created |
| `data/metadata/investigations_inventory.json` | Created, 26 records |
| `data/metadata/datasets_inventory.json` | Created, 383 records |
| `data/metadata/files_inventory.json` | Created, 1,520 current + 768 historical |
| `data/metadata/storage_summary.json` | Created, 7 rows + global + 9 gaps |
| Stable API snapshot | Created under `data/metadata/psi_api/` |
| Reproducible generator | Created at `scripts/audit_psi_source.py` |
| Download probe | Created at `scripts/probe_psi_download.py` + JSON evidence |
| Existing metadata preserved | Yes |
| Salma documents untouched | Yes |
| No database / RAG / frontend changes | Yes |
| No commits or pushes | Yes |

---

**End of Stage 1 audit. Awaiting explicit approval before Stage 2.**
