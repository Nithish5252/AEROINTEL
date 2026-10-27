# AeroIntel — Project Build Brief and AI Coding Instructions

> **Project title:** AeroIntel: Flight Anomaly Detection and Incident Analysis Using NLP  
> **Goal:** Build the strongest feasible, runnable, clearly documented project prototype under a very short deadline.  
> **Priority:** A working end-to-end demo with honest limitations is better than a large collection of incomplete features.

---

## 1. Instructions for the AI coding agent

You are the senior engineer responsible for implementing this project inside the existing workspace.

### Mandatory working rules

1. **Inspect the existing workspace first.** List the files, identify the current framework and environment, and preserve any useful existing work.
2. **Build and run the project, not just describe it.** Create the files, install only necessary dependencies, run the application and tests where the environment permits, and fix errors.
3. **Prioritize an end-to-end working MVP.** Do not spend the deadline designing an elaborate architecture or implementing advanced ML before the basic flow works.
4. **Never fake success.** Do not claim tests, API access, downloads, deployment, or model performance were verified unless they were actually verified.
5. **Do not invent data or source access.** Clearly label demo/synthetic data. Use real data only when it can be obtained legally and reliably. If a live API needs credentials, is rate-limited, or is unavailable, provide a clearly marked demo mode.
6. **Keep the application usable without API credentials or internet access.** The local demo must work using a small, clearly labeled sample dataset.
7. **Use robust, understandable code.** Add input validation, helpful errors, logging, sensible defaults and clear module boundaries. Avoid unnecessary complexity.
8. **Protect secrets.** Read credentials from environment variables or `.env`; include `.env.example`; never commit secrets.
9. **Preserve evidence and uncertainty.** Never present a detected anomaly as proof of an emergency, accident, mechanical failure, or cause. Never generate incident facts unsupported by source data.
10. **Work in small phases.** After each phase, run relevant checks and keep the app working. If a dependency or external service fails, switch to a documented fallback rather than blocking the whole project.
11. **Use the existing workspace's appropriate conventions.** Prefer a simple Python application unless the workspace already contains a useful, functioning stack.
12. **At completion, provide exact run commands, a file summary, test results, known limitations, and a short demo script.**

### Deadline strategy

Build in this order:

- **P0 — Required:** runnable dashboard, sample data, flight map or geographic visualization, anomaly detection, preliminary report, incident text processing, search/filtering, tests, README.
- **P1 — If time allows:** real API integration, incident dataset import, semantic search, persistent database, report lifecycle/history.
- **P2 — Only after P0/P1 work:** advanced ML, automated source monitoring, sophisticated correlation scoring, cloud deployment.

Do not sacrifice a working application to implement a speculative advanced feature.

---

## 2. Project overview

AeroIntel is an aviation intelligence prototype with two independent analysis pipelines and a shared report/evidence layer.

### Module A — Flight tracking and anomaly detection

- Ingest available aircraft state/telemetry data from a configured flight-data source when access is available.
- Include a **demo mode** that works immediately from clearly labeled sample data.
- Display aircraft observations on a geographic map or, if mapping dependencies cannot be installed, provide a functional geographic scatter/map-like fallback.
- Support a configurable center point and radius in kilometres where feasible.
- Show available aircraft identifier, observation timestamp, latitude, longitude, altitude, speed, heading/track and vertical rate. Handle missing fields safely.
- Detect unusual observations with transparent rules, such as a large altitude change across consecutive observations, unusually large speed change, or missing/stale observations.
- Add an Isolation Forest option only if there is sufficient data and it can be evaluated sensibly. Do not claim the model detects real aviation emergencies.
- Save each alert with its observation window, rule/model used, threshold or score, data source, timestamp, and quality warnings.
- Generate a preliminary report automatically when an alert is created.

### Module B — Aviation incident NLP

- Accept a local CSV or JSON incident dataset and/or provide a small illustrative sample dataset that is clearly marked **synthetic/demo data**.
- Preserve source text and source identifiers.
- Normalize text and handle missing or duplicated records.
- Implement incident text search and category filtering.
- Implement a baseline classifier only if labelled training data is available. Prefer a transparent TF-IDF + Logistic Regression baseline before a Transformer.
- Implement entity extraction using spaCy or a simpler clearly documented fallback if model downloads are unavailable.
- Provide concise summaries. Start with extractive or source-grounded summaries; do not invent causes, outcomes, injuries or aircraft details.
- If feasible, add semantic search using sentence-transformers. The app must still work if the model cannot download.
- Display each record's source, date and available metadata. Do not imply that voluntary reports are independently verified findings.

### Shared module — Report lifecycle and evidence

- Store preliminary reports and preserve their original contents.
- Support statuses such as `Detected`, `Preliminary`, `Under Review`, `Enriched`, `Confirmed by Source`, and `Closed`.
- Record source references, report updates and timestamps.
- Treat “Confirmed by Source” as “a cited source explicitly supports this statement,” not as independent verification of every aspect of an incident.
- Allow a possible link between a telemetry alert and an incident report only when supported by available evidence.
- Show match rationale, evidence and limitations. If evidence is insufficient, display “No supported link found” or “Needs review.”
- Never merge records solely because they have a similar aircraft type, nearby time, or similar wording.
- Keep telemetry facts, detector outputs, source-reported facts, model-generated text and unknowns clearly separate.

---

## 3. Suggested user interface

Create a polished, professional dashboard with a consistent layout, sensible typography, readable charts, and clear status labels. Avoid decorative complexity that harms readability.

### Page 1 — Overview

Show:
- Total observations loaded
- Alerts detected
- Preliminary reports
- Incident records loaded
- Latest data timestamp / freshness
- Current mode: `DEMO` or `LIVE DATA`
- Source/API health, if applicable

### Page 2 — Flight Monitor

Show:
- Interactive aircraft map when available
- Center latitude/longitude and radius controls
- Aircraft table and selection
- Available telemetry and observation history
- Clear indication of missing or stale data
- A button or action to analyze sample/current observations

### Page 3 — Anomaly Center

Show:
- Alerts with time, type, status and detector
- Alert detail with supporting measurements
- Timeline or altitude/speed plot where data supports it
- Thresholds and a human-readable explanation
- Link to the preliminary report

### Page 4 — Incident Intelligence

Show:
- Search box
- Category and date filters where data supports them
- Original narrative/source text
- Generated summary clearly marked as AI/system-generated
- Extracted entities and classification, when available
- Source reference and data provenance

### Page 5 — Reports and Investigation

Show:
- Report list and detail
- Lifecycle status
- Original evidence and later additions
- Revision/source history
- Potential incident associations, with rationale and uncertainty

### Page 6 — Evaluation / About

Show:
- Data-source and demo-data explanations
- Current model/rule configuration
- Test/evaluation metrics only when actually measured
- Limitations and responsible-use notes

If a six-page UI is too much for the deadline, combine pages into fewer tabs. The priority is completeness of the core workflows, not the number of pages.

---

## 4. Data source research and safe integration

Potential sources to investigate, verifying current access and terms before use:

- OpenSky API documentation: https://openskynetwork.github.io/opensky-api/rest.html
- OpenSky API repository/docs: https://github.com/openskynetwork/opensky-api
- NASA ASRS database: https://asrs.arc.nasa.gov/search/database.html
- NTSB aviation safety data: https://www.ntsb.gov/safety/data/pages/data_stats.aspx
- NTSB aviation data files: https://data.ntsb.gov/avdata/FileDirectory/

Important:
- Do not assume a source offers an unrestricted API, complete historical data, all telemetry fields, or unrestricted redistribution.
- Do not scrape a source if its terms or technical constraints do not permit it.
- Use explicit timeouts, rate-limit handling, retries with backoff, and user-friendly error messages.
- Cache results where appropriate and permitted.
- Make the demo usable without any external service.
- Show a source and retrieval timestamp for live data.
- Do not represent synthetic examples as actual aircraft or incidents.

---

## 5. Recommended implementation approach

Use the simplest compatible stack for a reliable prototype:

- Python 3.11+ (or the version already supported in the workspace)
- Streamlit for the initial dashboard
- pandas and NumPy for data handling
- Plotly for charts
- Folium/streamlit-folium for a map if compatible and installable
- scikit-learn for rule-assisted analytics and optional Isolation Forest / TF-IDF classifier
- spaCy for NLP if a suitable model is already installed or can be downloaded
- sentence-transformers only if time, connectivity and compute allow it
- SQLite for local persistence if needed
- pytest for tests
- python-dotenv for local configuration if needed

Do not install every package automatically. First inspect the workspace, then select a small compatible set. Pin working versions in the dependency file after verification.

### Suggested repository structure

Adapt to the existing workspace; do not force this structure if the project already has a working layout.

```text
aerointel/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── data/
│   ├── demo_flights.csv
│   └── demo_incidents.csv
├── aerointel/
│   ├── config.py
│   ├── data/
│   │   ├── loaders.py
│   │   └── validation.py
│   ├── flight/
│   │   ├── source.py
│   │   ├── geo.py
│   │   ├── features.py
│   │   ├── detector.py
│   │   └── reports.py
│   ├── incidents/
│   │   ├── ingest.py
│   │   ├── classify.py
│   │   ├── entities.py
│   │   ├── summarize.py
│   │   └── search.py
│   ├── shared/
│   │   ├── models.py
│   │   ├── lifecycle.py
│   │   └── evidence.py
│   └── ui/
│       ├── overview.py
│       ├── flights.py
│       ├── anomalies.py
│       └── incidents.py
└── tests/
    ├── test_geo.py
    ├── test_detector.py
    ├── test_incident_processing.py
    └── test_reports.py
```

For a tight deadline, a smaller modular structure is acceptable. Avoid overengineering.

---

## 6. Data and model requirements

### Demo flight data

Create a small, coherent, fictional dataset with multiple time-stamped observations per fictional aircraft. Include normal sequences and a few deliberately injected unusual patterns for demonstrating the detector. Mark every record as synthetic. Do not use real-world aircraft identifiers in a way that implies the synthetic event actually happened.

Required columns can include:

```text
aircraft_id,timestamp,latitude,longitude,altitude_ft,ground_speed_kt,heading_deg,vertical_rate_fpm,source,is_synthetic
```

Use realistic units and document them. Do not calculate a change unless there are suitable consecutive observations and valid timestamps.

### Demo incident data

Create a small set of clearly fictional narratives across several categories. Include fields such as:

```text
report_id,event_date,location,category,narrative,source_name,source_url,is_synthetic
```

Do not use fabricated source URLs. For synthetic examples, use a blank URL or a clearly labeled internal demo reference.

### Data validation

- Validate latitude in `[-90, 90]` and longitude in `[-180, 180]`.
- Parse timestamps safely and standardize internally to UTC where possible.
- Check for duplicate records and impossible/missing values.
- Handle out-of-order observations before calculating rates of change.
- Never treat missing telemetry as zero.
- Do not infer an incident cause from an anomaly score.
- Do not present a synthetic model score as validated operational risk.

### Anomaly rules

Start with interpretable rules and document their thresholds. Thresholds are demonstration settings, not aviation safety standards. Use consecutive observations for the same aircraft and sensible time gaps. Include unit tests for normal sequences, anomaly sequences, missing data, duplicate timestamps, out-of-order data, and large gaps.

### NLP evaluation

- Do not train a classifier on unlabelled narratives.
- Do not report F1/accuracy unless computed on a valid held-out dataset.
- If no suitable labelled dataset exists, demonstrate search, entity extraction and source-grounded summaries, and label classification as unavailable or illustrative.
- Separate generated outputs from original narratives.

---

## 7. Preliminary report schema

Every alert report should capture as many of these fields as available:

- `report_id`
- `alert_id`
- `created_at_utc`
- `event_start_utc`
- `event_end_utc`
- `aircraft_id` (nullable)
- `event_type`
- `observed_measurements`
- `calculated_changes`
- `detection_method`
- `thresholds_or_model_version`
- `anomaly_score` (nullable; include meaning and calibration status)
- `source_name`
- `source_retrieved_at_utc`
- `data_quality_warnings`
- `evidence_references`
- `initial_assessment`
- `unknowns`
- `lifecycle_status`
- `revision_history`

Example wording:

> “AeroIntel detected a change in recorded altitude that exceeded the configured demonstration threshold during the observed interval. The available telemetry is attached. The cause and operational significance are unknown. This alert is not, by itself, evidence of an emergency or accident.”

Do not call an alert an accident or emergency unless reliable source material explicitly supports that wording.

---

## 8. Testing checklist

Write and run automated tests for the parts that can be tested locally.

### Flight module
- Valid and invalid geographic coordinates
- Radius filtering and distance calculations
- Aircraft with missing optional fields
- Time sorting and duplicate observations
- Normal versus threshold-triggering sequences
- Large time gaps and stale observations
- Report creation and required fields

### Incident NLP module
- CSV/JSON import
- Missing narrative and malformed records
- Deduplication
- Keyword search and filters
- Summary fallback behavior
- Entity extraction when the NLP model is unavailable
- Clear separation of original text and generated outputs

### Shared/report module
- Lifecycle transitions
- Evidence/source references
- Revision history
- No automatic unsupported incident association

### Application
- Starts successfully using demo data
- Works without API credentials
- Shows a useful message when an optional model/API is unavailable
- No hard-coded secrets
- README run commands match the actual project

Never claim a test passed unless it was run and passed. Include a concise test summary in the final response.

---

## 9. Deployment and submission readiness

Before declaring the project complete:

- Confirm the app starts using the documented command.
- Confirm demo data loads from a clean environment.
- Run tests and fix failures.
- Check imports and dependencies.
- Add a clear README with project overview, architecture, setup, run commands, screenshots if available, limitations and future work.
- Add `.gitignore` entries for `.env`, virtual environments, caches, local databases and generated files as appropriate.
- Add `.env.example` with placeholder values only.
- Confirm no credentials or personal data are committed.
- Clearly label `DEMO MODE` and synthetic data in the UI.
- Document any live API features that were not verified.
- Provide a short demo path that works reliably during evaluation.

Do not claim cloud deployment unless the app was actually deployed and checked. If time is insufficient, deliver a working local app with reproducible setup instructions rather than a broken cloud deployment.

---

## 10. Suggested demonstration script

Prepare a 3–5 minute demonstration:

1. Open the app and explain the two independent modules.
2. Show the clearly labeled demo flight observations on the map/table.
3. Select an aircraft and display its observation history.
4. Trigger or inspect a deliberately injected synthetic anomaly.
5. Open the automatically generated preliminary report and explain the evidence and unknowns.
6. Search the incident collection and show a narrative, category, extracted entities and summary.
7. Show the report lifecycle and explain how source-backed enrichment would work.
8. Open the evaluation/limitations section and distinguish measured results from illustrative outputs.

Use only features that actually work in the delivered build.

---

## 11. Final instructions to the coding agent

Start now:

1. Inspect the workspace and report what already exists.
2. Create a short implementation plan ordered by risk and deadline.
3. Implement P0 end to end immediately.
4. Run the app and tests; fix failures before adding features.
5. Add P1 features only when the MVP is stable.
6. If you need to make a decision, choose the simplest safe implementation and document the trade-off instead of pausing for nonessential clarification.
7. At the end, report:
   - What was implemented
   - Exact files created or changed
   - Exact install/run/test commands
   - Which tests actually ran and their results
   - Whether live data/API access was actually verified
   - What is demo/synthetic versus real
   - Known limitations and next steps
   - A concise submission/demo checklist

**Definition of done:** A reviewer can start the application using the README, explore the main flight and NLP workflows without secrets, inspect a preliminary anomaly report, understand the provenance and limitations of each result, and run the available tests.
