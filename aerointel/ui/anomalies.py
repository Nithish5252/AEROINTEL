"""Page 3: Unusual Flight Movements — Plain-English anomaly review and intuitive report creation."""

import streamlit as st
import pandas as pd

from aerointel.flight.reports import generate_preliminary_report
from aerointel.flight.live_service import scan_live_airspace, AIRSPACE_PRESETS
from aerointel.shared.models import AnomalyAlert
from aerointel.ui.humanizer import explain_anomaly_in_plain_english, knots_to_mph_str, altitude_to_human_str


def render_anomalies(alerts: list, df_flights: pd.DataFrame, reports_store: list, plain_english: bool = True, *args, **kwargs):
    """Render the user-friendly Anomaly Center dashboard with Live OpenSky support."""
    st.markdown("## 🚨 Unusual Flight Movements (Anomaly Center)")
    st.markdown(
        "Our detection engine continuously scans flight telemetry for movements that deviate from standard steady cruising: "
        "such as rapid climbs or descents, low-altitude speed exceedances, sudden deceleration, or interrupted radio signals."
    )

    # 1. Source Switcher (OpenSky as Primary)
    live_alerts = st.session_state.get("live_alerts", [])
    demo_alerts = alerts
    current_mode = st.session_state.get("data_mode", "live")

    col_s1, col_s2 = st.columns([3, 2])
    with col_s1:
        source_choice = st.radio(
            "Surveillance Anomaly Stream:",
            [
                f"📡 Real-Time OpenSky Feed (Primary — {len(live_alerts)} alerts)",
                f"🧪 Offline Validation Scenarios ({len(demo_alerts)} alerts)",
            ],
            index=0,
            horizontal=True,
        )
    with col_s2:
        if "Real-Time OpenSky" in source_choice:
            st.caption("Active ADS-B state vector stream via OpenSky Network.")
            if st.button("📡 Re-Scan Live Airspace Now", type="secondary"):
                with st.spinner("Scanning live airspace..."):
                    center = st.session_state.get("live_search_center", (21.15, 79.09, 850.0, "All India Airspace"))
                    c_lat, c_lon, radius_km = center[0], center[1], center[2]
                    latest_df, feat_df, new_alerts, ok, msg, history = scan_live_airspace(c_lat, c_lon, radius_km)
                    if ok:
                        st.session_state["live_flights"] = latest_df
                        st.session_state["live_features"] = feat_df
                        st.session_state["live_alerts"] = new_alerts
                        st.session_state["live_flight_history"] = history
                        st.session_state["data_mode"] = "live"
                        st.rerun()

    is_reviewing_live = "Real-Time OpenSky" in source_choice
    active_alerts = live_alerts if is_reviewing_live else demo_alerts

    if not active_alerts:
        if is_reviewing_live:
            st.info(
                "No live anomalies currently detected, or no live scan has been executed yet. "
                "Click **'📡 Re-Scan Live Airspace Now'** above to fetch live aircraft and run the anomaly detector!"
            )
        else:
            st.success("✅ All monitored demo flights are currently cruising within standard, peaceful parameters.")
        return

    st.markdown("---")

    # Filter Bar
    a1, a2 = st.columns([3, 2])
    with a1:
        types = ["All Alert Types"] + sorted(list({a.event_type.value for a in active_alerts}))
        selected_type = st.selectbox("Filter by Movement Type:", types)
    with a2:
        aircraft_ids = ["All Aircraft"] + sorted(list({a.aircraft_id for a in active_alerts}))
        selected_ac = st.selectbox("Filter by Airplane:", aircraft_ids)

    # Filter alerts
    filtered_alerts = active_alerts
    if selected_type != "All Alert Types":
        filtered_alerts = [a for a in filtered_alerts if a.event_type.value == selected_type]
    if selected_ac != "All Aircraft":
        filtered_alerts = [a for a in filtered_alerts if a.aircraft_id == selected_ac]

    st.markdown(f"**Showing {len(filtered_alerts)} unusual flight event(s):**")

    # Display Alerts in Clean, Human-Friendly Cards
    for i, alert in enumerate(filtered_alerts):
        with st.container(border=True):
            # Header Row
            h1, h2, h3 = st.columns([4, 2, 2])
            with h1:
                country_label = ""
                m = alert.supporting_measurements or {}
                if m.get("origin_country") and m.get("origin_country") != "Unknown":
                    country_label = f" • {m['origin_country']}"
                st.markdown(f"### ✈️ `{alert.aircraft_id}`{country_label} — {alert.event_type.value}")
                st.caption(f"Spotted at: **{alert.window_end_utc.strftime('%H:%M:%S UTC')}** | Detection Rule: {alert.detection_method}")
            with h2:
                st.metric("Recorded Value", f"{alert.observed_value} {alert.unit}")
                st.caption(f"Normal Limit: {alert.threshold_value} {alert.unit}")
            with h3:
                existing_report = next((r for r in reports_store if r.alert_id == alert.alert_id), None)
                if existing_report:
                    st.success("📋 Report Created")
                else:
                    st.info("🟡 Needs Review")

            # Operational Assessment Box
            if plain_english:
                plain_info = explain_anomaly_in_plain_english(alert.event_type.value, alert.observed_value, alert.unit)
                st.markdown(f"""
                <div class="plain-english-box">
                    <div class="plain-english-title">💡 Operational Assessment & Guidance: {plain_info['title']}</div>
                    <p><b>Observed Kinematics:</b> {plain_info['what_happened']}</p>
                    <p><b>Operational Context:</b> {plain_info['what_it_usually_means']}</p>
                    <p><b>Investigative Action:</b> {plain_info['what_to_look_for']}</p>
                </div>
                """, unsafe_allow_html=True)

            # Humanized Measurement Cards
            with st.expander("📊 View Key Flight Numbers for this Moment", expanded=False):
                m1, m2, m3 = st.columns(3)
                with m1:
                    alt_val = m.get("altitude_ft") or m.get("last_known_altitude")
                    st.markdown(f"**Altitude:** {altitude_to_human_str(alt_val)}")
                with m2:
                    spd_val = m.get("ground_speed_kt")
                    st.markdown(f"**Forward Speed:** {knots_to_mph_str(spd_val)}")
                with m3:
                    vr_val = m.get("vertical_rate_fpm")
                    if vr_val is not None:
                        st.markdown(f"**Vertical Drop / Climb:** {vr_val:,.0f} fpm (~{round(abs(vr_val)*0.01136)} mph vertically)")
                    elif "gap_seconds" in m:
                        st.markdown(f"**Signal Blackout:** {m['gap_seconds']} seconds ({round(m['gap_seconds']/60, 1)} minutes)")

            # Create Report Action
            btn_col1, btn_col2 = st.columns([3, 4])
            with btn_col1:
                if existing_report:
                    st.write(f"📄 *Report file `{existing_report.report_id}` is ready in Page 5.*")
                else:
                    if st.button("📝 Open Formal Investigation Dossier", key=f"btn_rep_{alert.alert_id}_{i}"):
                        new_report = generate_preliminary_report(alert)
                        reports_store.append(new_report)
                        st.success(f"Investigation dossier created! You can view it under Page 5 (Investigation & Reports).")
                        st.rerun()
            with btn_col2:
                st.caption("Documents all measurements, uncertainties, and what is still unknown before drawing conclusions.")
