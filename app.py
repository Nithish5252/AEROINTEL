"""AeroIntel: Flight Anomaly Detection and Incident Analysis Using NLP.

Main Streamlit Application Entrypoint with User-Friendly Design System.
"""

import streamlit as st
import pandas as pd

from aerointel.config import config
from aerointel.data.loaders import load_flight_data, load_incident_data
from aerointel.data.generator import ensure_demo_datasets
from aerointel.flight.features import compute_flight_features
from aerointel.flight.detector import AnomalyDetector
from aerointel.incidents.ingest import preprocess_incidents
from aerointel.incidents.classify import IncidentClassifier

from aerointel.ui.overview import render_overview
from aerointel.ui.flights import render_flights
from aerointel.ui.anomalies import render_anomalies
from aerointel.ui.incidents import render_incidents
from aerointel.ui.reports import render_reports
from aerointel.ui.evaluation import render_evaluation
from aerointel.ui.humanizer import AVIATION_GLOSSARY


# Page configuration
st.set_page_config(
    page_title="AeroIntel — Friendly Aviation Intelligence",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Human-Crafted CSS (eliminates robotic AI aesthetic)
st.markdown("""
<style>
    /* Clean, modern typography and spacing */
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }
    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        letter-spacing: -0.02em;
    }
    
    /* Friendly human badge pills */
    .badge-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .badge-cyan { background-color: #E0F2FE; color: #0369A1; border: 1px solid #BAE6FD; }
    .badge-emerald { background-color: #D1FAE5; color: #065F46; border: 1px solid #A7F3D0; }
    .badge-amber { background-color: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
    .badge-gray { background-color: #F1F5F9; color: #475569; border: 1px solid #E2E8F0; }

    /* Plain-English Callout Box */
    .plain-english-box {
        background: #F0F9FF;
        border-left: 4px solid #0284C7;
        padding: 14px 18px;
        border-radius: 6px;
        margin: 12px 0 16px 0;
        font-size: 0.92rem;
        line-height: 1.5;
        color: #0C4A6E;
    }
    .plain-english-title {
        font-weight: 700;
        color: #0369A1;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Clean Card Styling */
    div[data-testid="stExpander"] {
        border-radius: 8px;
        border: 1px solid #E2E8F0 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.7rem !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_classifier():
    """Cache the baseline incident classifier instance."""
    return IncidentClassifier()


def initialize_session_state():
    """Initialize datasets, detectors, and reports in session state."""
    if "initialized" not in st.session_state:
        ensure_demo_datasets(config.data_dir)

        # 1. Load Telemetry Data
        df_flights, flight_warnings = load_flight_data()
        st.session_state["df_flights"] = df_flights
        st.session_state["flight_warnings"] = flight_warnings

        # 2. Compute Features
        df_features = compute_flight_features(df_flights)
        st.session_state["df_features"] = df_features

        # 3. Detect Anomalies (Rule-based + Isolation Forest)
        detector = AnomalyDetector(config.thresholds)
        rule_alerts = detector.detect_rule_anomalies(df_features)
        ml_alerts = detector.detect_isolation_forest_anomalies(df_features)
        demo_alerts = rule_alerts + ml_alerts
        st.session_state["alerts"] = demo_alerts

        # 4. Load & Preprocess Incidents
        df_incidents, inc_warnings = load_incident_data()
        clean_incidents, prep_warnings = preprocess_incidents(df_incidents)
        st.session_state["df_incidents"] = clean_incidents
        st.session_state["incident_warnings"] = inc_warnings + prep_warnings

        # 5. Train Baseline Classifier on Demo Data
        classifier = get_classifier()
        classifier.train(clean_incidents)
        st.session_state["classifier"] = classifier

        # 6. Reports Store
        st.session_state["reports"] = []

        # Default Audience Setting
        st.session_state["plain_english_mode"] = True

        # 7. OpenSky Network as Primary Surveillance Feed (Indian Airspace)
        st.session_state["data_mode"] = "live"
        try:
            from aerointel.flight.live_service import scan_live_airspace
            latest_df, feat_df, live_alerts, ok, msg, hist = scan_live_airspace(21.15, 79.09, 850.0, timeout_sec=12.0)
            if ok and not latest_df.empty:
                st.session_state["live_flights"] = latest_df
                st.session_state["live_features"] = feat_df
                st.session_state["live_alerts"] = live_alerts
                st.session_state["live_flight_history"] = hist
                st.session_state["live_status_msg"] = msg
                st.session_state["live_search_center"] = (21.15, 79.09, 850.0, "All India Airspace")
            else:
                st.session_state["live_flights"] = df_flights
                st.session_state["live_features"] = df_features
                st.session_state["live_alerts"] = demo_alerts
                st.session_state["live_status_msg"] = "Loaded offline Indian Airspace baseline radar."
                st.session_state["live_search_center"] = (21.15, 79.09, 850.0, "All India Airspace")
        except Exception:
            st.session_state["live_flights"] = df_flights
            st.session_state["live_features"] = df_features
            st.session_state["live_alerts"] = demo_alerts
            st.session_state["live_status_msg"] = "Loaded offline Indian Airspace baseline radar."
            st.session_state["live_search_center"] = (21.15, 79.09, 850.0, "All India Airspace")

        st.session_state["initialized"] = True


def main():
    initialize_session_state()

    df_flights = st.session_state["df_flights"]
    df_features = st.session_state["df_features"]
    df_incidents = st.session_state["df_incidents"]
    alerts = st.session_state["alerts"]
    reports = st.session_state["reports"]
    classifier = st.session_state["classifier"]

    # Sidebar Navigation
    st.sidebar.markdown("## ✈️ AeroIntel")
    st.sidebar.caption("Real-Time OpenSky Radar & Incident Intelligence")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Surveillance Modules",
        [
            "1. Overview (Operational Status)",
            "2. Real-Time Flight Monitor",
            "3. Kinematic Anomaly Center",
            "4. Safety Report Library",
            "5. Investigation & Reports",
            "6. Reference Guide & System Specifications",
        ],
        index=0,
    )

    st.sidebar.markdown("---")
    
    # Executive Context Toggle
    st.sidebar.markdown("### 💡 Operational Intelligence")
    plain_english = st.sidebar.checkbox(
        "Executive Context & Conversions",
        value=st.session_state.get("plain_english_mode", True),
        help="Provides operational assessments, context explanations, and metric conversions (mph, km/h, miles).",
    )
    st.session_state["plain_english_mode"] = plain_english

    st.sidebar.markdown("---")
    
    # Active Radar Status in Sidebar
    is_live = st.session_state.get("data_mode") == "live"
    live_flights = st.session_state.get("live_flights")
    live_alerts = st.session_state.get("live_alerts", [])

    if is_live and live_flights is not None and not live_flights.empty:
        st.sidebar.markdown("### 🟢 Primary Stream: OpenSky Live")
        st.sidebar.caption(f"Tracking **{len(live_flights)}** real-time aircraft | **{len(live_alerts)}** anomalies flagged.")
    else:
        st.sidebar.markdown("### 🧪 Airspace Baseline: Synthetic")
        st.sidebar.caption("Loaded with sample validation flights & reports. Ready offline without internet.")

    # Quick Glossary Expander in Sidebar
    with st.sidebar.expander("📖 Aviation Terminology Reference"):
        st.markdown("*Operational Aerospace Terms:*")
        for term, definition in list(AVIATION_GLOSSARY.items())[:6]:
            st.markdown(f"**{term}:** {definition}")

    if st.sidebar.button("🔄 Reset Application Data"):
        st.session_state.pop("initialized", None)
        st.session_state.pop("live_flights", None)
        st.session_state.pop("live_alerts", None)
        st.session_state.pop("live_flight_history", None)
        st.session_state["data_mode"] = "live"
        st.rerun()

    # Determine active telemetry dataset based on current mode
    if is_live and live_flights is not None and not live_flights.empty:
        active_flights = live_flights
        active_features = st.session_state.get("live_features", live_flights)
        active_alerts = live_alerts
    else:
        active_flights = df_flights
        active_features = df_features
        active_alerts = alerts

    # Route to selected page
    if "1. Overview" in page:
        render_overview(active_flights, df_incidents, active_alerts, reports, plain_english)
    elif "2. Real-Time Flight Monitor" in page:
        render_flights(active_flights, active_features, plain_english, alerts=active_alerts)
    elif "3. Kinematic Anomaly Center" in page:
        render_anomalies(active_alerts, active_flights, reports, plain_english)
    elif "4. Safety Report Library" in page:
        render_incidents(df_incidents, classifier, plain_english)
    elif "5. Investigation" in page:
        render_reports(reports, df_incidents, active_alerts, plain_english)
    elif "6. Reference Guide" in page:
        render_evaluation(classifier, active_flights, df_incidents, plain_english)


if __name__ == "__main__":
    main()
