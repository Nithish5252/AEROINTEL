"""Page 1: System Overview — Operational health and real-time surveillance orientation."""

from datetime import datetime, timezone
import streamlit as st
import pandas as pd

from aerointel.flight.live_service import scan_live_airspace, AIRSPACE_PRESETS


def render_overview(
    df_flights: pd.DataFrame,
    df_incidents: pd.DataFrame,
    alerts: list,
    reports: list,
    plain_english: bool = True,
    *args,
    **kwargs,
):
    """Render the primary operational Overview dashboard."""
    st.markdown("## ✈️ AeroIntel Flight Intelligence")
    st.markdown(
        "**Real-Time OpenSky Airspace Surveillance, Kinematic Anomaly Detection & Incident Narrative Analysis**"
    )

    # OpenSky Network Primary Surveillance Banner
    is_live = st.session_state.get("data_mode") == "live"
    live_flights = st.session_state.get("live_flights", pd.DataFrame())
    live_alerts = st.session_state.get("live_alerts", [])

    with st.container(border=True):
        b1, b2 = st.columns([5, 3])
        with b1:
            if is_live and not live_flights.empty:
                center_info = st.session_state.get("live_search_center", (21.15, 79.09, 850.0, "All India Airspace"))
                st.markdown(f"#### 🟢 Primary Radar Feed: `{len(live_flights)}` Live Aircraft (Indian Airspace)")
                st.caption(f"Actively tracking live ADS-B state vectors within **{center_info[2]:.0f} km** of **{center_info[3]}** via OpenSky Network.")
            else:
                st.markdown("#### 📡 Primary Surveillance: OpenSky Network (Indian Airspace Live)")
                st.caption("Live transponder telemetry stream ready for Indian FIR surveillance and continuous anomaly scanning.")
        with b2:
            if st.button("📡 Scan Live Airspace Now", type="primary", use_container_width=True):
                with st.spinner("Streaming state vectors from OpenSky Network across Indian Airspace..."):
                    latest_df, feat_df, new_alerts, ok, msg, history = scan_live_airspace(21.15, 79.09, 850.0)
                    if ok:
                        st.session_state["live_flights"] = latest_df
                        st.session_state["live_features"] = feat_df
                        st.session_state["live_alerts"] = new_alerts
                        st.session_state["live_flight_history"] = history
                        st.session_state["live_status_msg"] = msg
                        st.session_state["live_search_center"] = (21.15, 79.09, 850.0, "All India Airspace")
                        st.session_state["data_mode"] = "live"
                        st.rerun()

    if plain_english:
        st.markdown("""
        <div class="plain-english-box">
            <div class="plain-english-title">💡 Operational Surveillance Overview:</div>
            AeroIntel unifies real-time live transponder telemetry from the <b>OpenSky Network</b> with automated kinematic 
            anomaly detection and source-grounded NLP safety report analysis into a unified situational intelligence platform.
        </div>
        """, unsafe_allow_html=True)

    # 4 Operational KPI Metrics
    active_df = live_flights if (is_live and not live_flights.empty) else df_flights
    active_alerts = live_alerts if (is_live and not live_flights.empty) else alerts

    col1, col2, col3, col4 = st.columns(4)

    total_obs = len(active_df) if not active_df.empty else 0
    unique_aircraft = active_df["aircraft_id"].nunique() if not active_df.empty else 0
    source_label = "OpenSky Live ADS-B" if is_live else "Synthetic Airspace"
    col1.metric("Airborne Aircraft", f"{unique_aircraft} Aircraft", f"{total_obs:,} observations ({source_label})")

    col2.metric("Kinematic Anomalies", len(active_alerts), "Vertical rates, speeds & gaps")
    col3.metric("Investigation Dossiers", len(reports), "Section 7 Preliminary Reports")

    total_incidents = len(df_incidents) if not df_incidents.empty else 0
    col4.metric("Incident Narratives", f"{total_incidents} Reports", "Categorized & extracted")

    st.markdown("---")

    # Three-Column Tour Card
    st.markdown("### 🗺️ Intelligence Modules")
    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(border=True):
            st.markdown("#### 1. Live Flight Radar")
            st.write(
                "Monitor real-time aircraft positions, altitudes, and speeds via **OpenSky Network**. "
                "Select any aircraft to inspect its kinematic trajectory and altitude profile."
            )
            st.caption("📍 *Features: OpenSky ADS-B ingest, geographic radius filters, time-series telemetry.*")

    with c2:
        with st.container(border=True):
            st.markdown("#### 2. Kinematic Anomaly Center")
            st.write(
                "Review automated anomaly alerts triggered by high vertical climb/descent rates, "
                "low-altitude speed exceedances, or transponder telemetry interruptions."
            )
            st.caption("🔍 *Features: Deterministic rules, Isolation Forest, one-click preliminary dossiers.*")

    with c3:
        with st.container(border=True):
            st.markdown("#### 3. Incident Narrative Intelligence")
            st.write(
                "Search and analyze official voluntary aviation safety reports (ASRS/NTSB) "
                "using source-grounded extractive summarization and text classification."
            )
            st.caption("📖 *Features: 0% hallucination summaries, named entity extraction, TF-IDF classifier.*")

    st.markdown("---")

    # Operational Telemetry Reference
    if plain_english:
        with st.expander("📘 Flight Telemetry & Parameter Reference", expanded=False):
            st.markdown(r"""
            | Parameter | Operational Definition | Standard Range & Context |
            | :--- | :--- | :--- |
            | **Altitude (ft)** | Height above mean sea level. | Commercial cruise: 30,000 to 41,000 ft (~6 to 7.8 miles). |
            | **FL (Flight Level)** | Pressure altitude in hundreds of feet above 18,000 ft. | FL240 = 24,000 ft; FL350 = 35,000 ft. |
            | **Ground Speed (kt)** | Speed relative to the ground in nautical miles per hour. | 450 kt ≈ 518 mph (833 km/h). |
            | **Vertical Rate (fpm)** | Rate of altitude climb or descent in feet per minute. | Normal descent: 1,500 to 2,000 fpm. $>2,500$ fpm triggers anomaly alert. |
            | **Low Alt Speed Limit** | Airspace speed regulation below 10,000 ft (FAA § 91.117 / ICAO). | Standard limit: $\le 250\text{ kt}$. $\ge 275\text{ kt}$ triggers exceedance alert. |
            | **Telemetry Gap (s)** | Duration between consecutive transponder state vectors. | Normal: 5–15s. $>180$s indicates receiver masking or coverage interruption. |
            """)
