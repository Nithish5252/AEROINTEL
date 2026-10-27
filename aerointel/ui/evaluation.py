"""Page 6: System Reference Guide, Detection Logic, and Project Architecture."""

import streamlit as st
import pandas as pd

from aerointel.config import config
from aerointel.incidents.classify import IncidentClassifier
from aerointel.ui.humanizer import AVIATION_GLOSSARY


def render_evaluation(
    classifier: IncidentClassifier,
    df_flights: pd.DataFrame,
    df_incidents: pd.DataFrame,
    plain_english: bool = True,
    *args,
    **kwargs,
):
    """Render the comprehensive System Reference Guide, Glossary, and Architecture Specifications."""
    st.markdown("## 📖 System Reference Guide & Architecture")
    st.markdown(
        "AeroIntel adheres to strict engineering principles: **deterministic physical rules, "
        "unsupervised statistical baselines, 100% source-grounded extractive NLP, and auditable evidence provenance.**"
    )

    # 1. Aviation Terminology & Acronyms Reference
    st.markdown("### 📚 1. Aviation Terminology & Acronym Reference")
    st.caption("Standard aerospace definitions and real-world operational benchmarks:")

    cols = st.columns(2)
    glossary_items = list(AVIATION_GLOSSARY.items())
    half = (len(glossary_items) + 1) // 2

    with cols[0]:
        for term, desc in glossary_items[:half]:
            with st.container(border=True):
                st.markdown(f"**✈️ {term}**")
                st.write(desc)

    with cols[1]:
        for term, desc in glossary_items[half:]:
            with st.container(border=True):
                st.markdown(f"**✈️ {term}**")
                st.write(desc)

    st.markdown("---")

    # 2. How the Detection Engine Works
    st.markdown("### 🧠 2. Kinematic Detection Engine Specifications")
    with st.container(border=True):
        st.markdown(r"""
        The telemetry surveillance engine applies dual-tier anomaly detection:
        * **1. Vertical Rate Exceedance ($|vrate| \ge 2,500\text{–}3,000\text{ fpm}$):** Identifies rapid descent or climb phases exceeding typical passenger airline profiles ($\sim 1,500\text{--}2,000\text{ fpm}$).
        * **2. Low-Altitude High-Speed Exceedance ($\ge 275\text{ kt below } 10,000\text{ ft}$):** Evaluates FAA § 91.117 / ICAO terminal area speed separation standards ($\le 250\text{ kt}$).
        * **3. Deceleration Exceedance ($\Delta spd \le -45\text{ kt}$):** Flags sudden aerodynamic braking maneuvers or abrupt airspeed reduction.
        * **4. Transponder Interval Gap ($\ge 180\text{ s}$):** Flags receiver masking or low-altitude coverage boundary transits.
        * **5. Unsupervised Isolation Forest:** Multivariate tree ensemble isolating joint distribution outliers across vertical rate, speed delta, altitude, and ground speed.
        """)

    st.markdown("---")

    # 3. Source-Grounded Extractive NLP
    st.markdown("### 🛡️ 3. Source-Grounded Extractive NLP (0% Hallucination Guarantee)")
    with st.container(border=True):
        st.markdown("""
        In aviation safety analysis, **absolute factual veracity is paramount**. Generative language models frequently extrapolate unverified causal claims, imaginary equipment damages, or inaccurate injury counts.
        
        **AeroIntel Technical Guarantees:**
        * **Strictly Extractive Summarization:** Summaries are composed exclusively of verbatim sentences extracted directly from the primary submitted report text.
        * **Zero Causal Extrapolation:** The engine never hallucinates mechanical failures, crew blame, or unrecorded outcomes.
        * **Named Entity Recognition:** Regex patterns extract structured aircraft models (`B737`, `A320`), runways (`04L`, `22R`), and Flight Levels (`FL350`) directly from raw text.
        """)

    st.markdown("---")

    # 4. Operational Ethics & Technical Boundaries
    st.markdown("### ⚖️ 4. Technical Boundaries & Operational Ethics")
    with st.container(border=True):
        st.markdown("""
        * **Detections are Alerts, Not Verified Emergencies:** A steep descent is overwhelmingly an ATC-directed procedure or weather avoidance. AeroIntel never presents a telemetry anomaly as proof of an emergency without verified ATC or official incident documentation.
        * **Structured Uncertainty:** Every Section 7 Preliminary Dossier generated explicitly documents unknown variables (such as pilot intent, cockpit voice recordings, or weather radar data) to prevent premature investigator bias.
        """)
