# AeroIntel — Flight Anomaly Detection & Incident Analysis Using NLP

> **AeroIntel** is an aviation intelligence prototype featuring two independent analysis pipelines—real-time/historical flight telemetry anomaly detection and aviation safety incident NLP narrative analysis—unified by a shared, evidence-based preliminary reporting and lifecycle layer.

---

## 🛫 System Architecture

```
                    ┌────────────────────────────────────────────────────────┐
                    │            AeroIntel Streamlit Dashboard               │
                    │   (Overview | Flights | Alerts | Incidents | Reports)   │
                    └───────────────────────────┬────────────────────────────┘
                                                │
             ┌──────────────────────────────────┴──────────────────────────────────┐
             ▼                                                                     ▼
   ┌───────────────────────────────────┐                         ┌───────────────────────────────────┐
   │  Module A: Flight Telemetry &     │                         │  Module B: Aviation Incident NLP  │
   │  Anomaly Detection                │                         │                                   │
   │  - Demo & live data loaders       │                         │  - Narrative normalization        │
   │  - Geographic & radius filters    │                         │  - Keyword & semantic search      │
   │  - Rate-of-change feature engine  │                         │  - Extractive summarization       │
   │  - Rule & Isolation Forest alert  │                         │  - Entity extraction (NER)        │
   │  - Automatic preliminary reports  │                         │  - TF-IDF baseline classifier     │
   └─────────────────┬─────────────────┘                         └─────────────────┬─────────────────┘
                     │                                                             │
                     └──────────────────────────┬──────────────────────────────────┘
                                                ▼
                               ┌───────────────────────────────────┐
                               │  Shared Evidence & Report Layer   │
                               │  - Schema-validated reports       │
                               │  - Lifecycle state machine        │
                               │  - Evidence-backed associations   │
                               │  - Provenance & audit history     │
                               └───────────────────────────────────┘
```

---

## 🌟 Key Capabilities & Dashboard Pages

The dashboard is structured into six focused pages:

1. **Page 1 — Overview & Health**: Real-time KPI counters (observations, alerts, reports, incidents), telemetry freshness tracker, operating mode badge (`🟢 DEMO MODE`), and quick workflow guide.
2. **Page 2 — Flight Monitor**: Geographic tracking using Plotly Scattergeo with configurable center coordinates and radius in kilometers, aircraft selector, altitude/speed profiles, and missing/stale telemetry inspection.
3. **Page 3 — Anomaly Center**: Real-time alert feed driven by transparent threshold rules (rate of climb/descent $\ge 3,000$ fpm, speed drop $\ge 45$ kt, signal interruption $\ge 180$ s) and scikit-learn Isolation Forest statistical outliers. Generates Section 7 compliant Preliminary Reports at the click of a button.
4. **Page 4 — Incident Intelligence**: Multi-criteria search (keyword, category, location, date range), extractive source-grounded summarizer (0% hallucination), domain NER (Aircraft, Airports, Altitudes, Runways/Fixes, Avionics, Weather), and TF-IDF baseline classification.
5. **Page 5 — Reports & Investigation**: Formal preliminary report dossier complying with the Section 7 schema, interactive lifecycle state machine (`Detected` $\to$ `Preliminary` $\to$ `Under Review` $\to$ `Enriched` $\to$ `Confirmed by Source` $\to$ `Closed`), audit revision log, and evidence-backed correlation engine.
6. **Page 6 — Evaluation & Transparency**: Transparent data provenance disclosures, active detector threshold inspector, classifier cross-validation metrics, and responsible-use ethics guidelines.

---

## 🚀 Setup & Execution Instructions

### Prerequisites
* Python 3.11 or 3.12 (Tested on Python 3.12.10)
* Windows, macOS, or Linux

### 1. Environment Setup
```bash
# Clone or navigate to the workspace
cd NLP

# Create and activate a virtual environment
python -m venv .venv

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# On Linux / macOS:
# source .venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run app.py
```
The dashboard will open automatically in your browser at `http://localhost:8501`.

### 3. Run Automated Tests
```bash
pytest
```

---

## 🗂️ Project Structure

```text
NLP/
├── app.py                      # Main Streamlit dashboard application
├── requirements.txt            # Dependency manifest
├── README.md                   # System documentation & demo guide
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── data/                       # Local datasets
│   ├── demo_flights.csv        # Synthetic flight telemetry with injected anomalies
│   └── demo_incidents.csv      # Synthetic aviation safety incident narratives
├── aerointel/
│   ├── config.py               # Central configuration & demonstration thresholds
│   ├── data/
│   │   ├── generator.py        # High-fidelity synthetic dataset generator
│   │   ├── loaders.py          # Data loaders with automatic fallback
│   │   └── validation.py       # Geographic & schema validation
│   ├── flight/
│   │   ├── geo.py              # Haversine distance, bounding box, radius filters
│   │   ├── features.py         # Rate-of-change and time-delta feature engine
│   │   ├── detector.py         # Rule-based and Isolation Forest detectors
│   │   ├── source.py           # OpenSky Network live connector with demo fallback
│   │   └── reports.py          # Section 7 preliminary report builder
│   ├── incidents/
│   │   ├── ingest.py           # Text normalization and deduplication
│   │   ├── search.py           # Keyword search and multi-field filtering
│   │   ├── summarize.py        # Extractive source-grounded summarizer
│   │   ├── entities.py         # Named Entity Recognition with regex fallback
│   │   └── classify.py         # TF-IDF + Logistic Regression baseline classifier
│   ├── shared/
│   │   ├── models.py           # Pydantic schemas (Section 7 Report, Alert, Incident)
│   │   ├── lifecycle.py        # Lifecycle transition state machine & audit trail
│   │   └── evidence.py         # Conservative evidence-based association engine
│   └── ui/                     # Modular Streamlit page renderers
│       ├── overview.py
│       ├── flights.py
│       ├── anomalies.py
│       ├── incidents.py
│       ├── reports.py
│       └── evaluation.py
└── tests/                      # Automated test suite
    ├── test_geo.py
    ├── test_detector.py
    ├── test_incident_processing.py
    ├── test_reports.py
    └── test_association.py
```

---

## 🎭 3–5 Minute Demonstration Walkthrough

1. **Overview (`Page 1`)**: Open the application. Note the `🟢 DEMO MODE` status indicating the application is 100% functional offline without external API keys.
2. **Flight Monitor (`Page 2`)**: Observe synthetic aircraft tracks in the Northeast US corridor. Adjust the geographic radius slider to 200 km around NYC/BOS. Select aircraft `SYN-FLT-101` and view its altitude profile displaying a sharp drop.
3. **Anomaly Center (`Page 3`)**: Inspect the alerts triggered by `SYN-FLT-101` (Descent rate $\ge 3,800$ fpm) and `SYN-FLT-204` (Speed drop $\ge 60$ kt). Click **"Generate Preliminary Report"** for `SYN-FLT-101`.
4. **Incident Intelligence (`Page 4`)**: Search for `"turbulence"` or `"depressurization"`. Notice the extractive summary (which guarantees zero fabricated causes), the domain entity pills (Airports, Altitudes, Runways, Systems), and the classifier prediction.
5. **Reports & Investigation (`Page 5`)**: Open the newly generated preliminary report. Review the explicit *Unknowns* and *Initial Assessment*. Update the status from `Detected` to `Preliminary` or `Under Review`, add investigation notes, and observe the updated audit log.
6. **Evaluation & Transparency (`Page 6`)**: Review the synthetic data disclosure, threshold parameters, honest classifier metrics, and ethical aviation safety disclaimer.

---

## 🛡️ Responsible Use & Evidence Principles

* **Preserve Evidence and Uncertainty:** A detected rate-of-descent or speed excursion is never evidence of an accident, mechanical failure, or emergency. Operational factors (such as ATC clearances or weather avoidance) frequently explain unusual flight profiles.
* **Zero Uncorroborated Fact Generation:** AeroIntel does not generate incident causes, fatalities, injuries, or mechanical faults unsupported by source documents.
* **Association Discipline:** Telemetry alerts and incident narratives are never merged based solely on coincidental timing or aircraft type.
