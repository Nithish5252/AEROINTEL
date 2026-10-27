"""Page 2: Flight Monitor & Real-Time Radar — Flightradar24-Style UI with aircraft icons."""

from datetime import datetime, timezone
import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

from aerointel.flight.geo import filter_by_radius
from aerointel.flight.live_service import AIRSPACE_PRESETS, scan_live_airspace, decode_airline_info
from aerointel.flight.reports import generate_preliminary_report
from aerointel.ui.humanizer import knots_to_mph_str, altitude_to_human_str, vrate_to_human_str


# Synthetic Aircraft Nicknames for Demo Mode
AIRCRAFT_STORY_NAMES = {
    "AIC-FLT-101": "Air India 101 • Rapid Descent Demo (Steep descent near Delhi NCR)",
    "IGO-FLT-204": "IndiGo 204 • Sudden Deceleration Demo (Rapid speed loss near Mumbai TMA)",
    "SEJ-FLT-309": "SpiceJet 309 • Radar Coverage Gap Demo (5-minute signal gap over Nagpur)",
    "VTI-FLT-402": "Vistara 402 • Smooth Normal Cruise (Steady flight near Bengaluru BLR)",
    "SYN-FLT-101": "Flight 101 • Rapid Altitude Drop Demo (Steep descent over Connecticut)",
    "SYN-FLT-204": "Flight 204 • Sudden Deceleration Demo (Rapid speed loss near Boston)",
    "SYN-FLT-309": "Flight 309 • Radar Coverage Gap Demo (5-minute signal gap over New Jersey)",
    "SYN-FLT-402": "Flight 402 • Smooth Normal Flight (Normal steady cruise near New York JFK)",
    "SYN-FLT-505": "Flight 505 • Complex Maneuver Demo (Combined turn & descent outlier)",
}


def render_flights(
    df_flights: pd.DataFrame,
    df_features: pd.DataFrame,
    plain_english: bool = True,
    *args,
    **kwargs,
):
    """Render the Flightradar24-style real-time aircraft surveillance radar."""
    st.markdown("## 🗺️ Real-Time Radar Display (Flightradar24 Style)")
    st.markdown(
        "Live surveillance display powered by the **OpenSky Network ADS-B stream**, "
        "featuring directional aircraft icons, real-time kinematics, and automated anomaly detection over **Indian Airspace**."
    )

    # 1. Source Mode Selector (OpenSky Indian Airspace as Primary)
    current_mode = st.session_state.get("data_mode", "live")
    mode_options = [
        "📡 OpenSky Network (Primary Real-Time Indian Airspace Feed)",
        "🧪 Offline Synthetic Airspace (Validation Scenarios)",
    ]
    mode_idx = 0 if current_mode == "live" else 1

    selected_mode_label = st.radio(
        "Surveillance Telemetry Feed:",
        mode_options,
        index=mode_idx,
        horizontal=True,
    )
    is_live_mode = "OpenSky Network" in selected_mode_label
    st.session_state["data_mode"] = "live" if is_live_mode else "demo"

    # 2. Flightradar24 Radar Control Panel
    if is_live_mode:
        with st.container(border=True):
            st.markdown("##### 📡 Flightradar24 Tactical Airspace Scanner")
            st.caption("Select an Indian Airspace FIR/region or enter custom coordinates and search radius to scan live airborne flights.")

            r1, r2 = st.columns([3, 2])
            with r1:
                preset_choice = st.selectbox(
                    "Select Airspace Region / FIR:",
                    list(AIRSPACE_PRESETS.keys()),
                    index=0,
                )
                preset_lat, preset_lon, preset_rad = AIRSPACE_PRESETS[preset_choice]

            with r2:
                radius_km = st.slider(
                    "Surveillance Radius from Center",
                    min_value=50,
                    max_value=1200,
                    value=int(preset_rad),
                    step=25,
                    format="%d km",
                )

            # Custom Coordinates Expander / Overrides
            c_lat, c_lon = preset_lat, preset_lon
            if "Custom" in preset_choice:
                c1, c2 = st.columns(2)
                with c1:
                    c_lat = st.number_input("Center Latitude", value=21.15, min_value=-90.0, max_value=90.0, step=0.1)
                with c2:
                    c_lon = st.number_input("Center Longitude", value=79.09, min_value=-180.0, max_value=180.0, step=0.1)

            miles_radius = round(radius_km * 0.621371)
            st.caption(f"📍 Center Point: **({c_lat:.3f}°, {c_lon:.3f}°)** | Coverage Radius: **{radius_km} km ({miles_radius} miles)**")

            # Scan Action Button
            scan_col1, scan_col2 = st.columns([3, 5])
            with scan_col1:
                do_scan = st.button("📡 Scan Live Airspace Now", type="primary", use_container_width=True)
            with scan_col2:
                st.caption("Streams real-time ADS-B transponder state vectors from OpenSky Network terrestrial receivers.")

            # Perform scan if requested, or if no live data has been fetched yet
            if do_scan or ("live_flights" not in st.session_state or st.session_state["live_flights"].empty):
                with st.spinner(f"Acquiring live ADS-B state vectors across {preset_choice}..."):
                    history_df = st.session_state.get("live_flight_history")
                    latest_df, feat_df, alerts, ok, msg, updated_history = scan_live_airspace(
                        center_lat=c_lat,
                        center_lon=c_lon,
                        radius_km=float(radius_km),
                        history_df=history_df,
                        timeout_sec=14.0,
                    )
                    if ok and not latest_df.empty:
                        st.session_state["live_flights"] = latest_df
                        st.session_state["live_features"] = feat_df
                        st.session_state["live_alerts"] = alerts
                        st.session_state["live_flight_history"] = updated_history
                        st.session_state["live_status_msg"] = msg
                        st.session_state["live_search_center"] = (c_lat, c_lon, radius_km, preset_choice)
                        st.success(msg)
                    else:
                        st.warning(msg)

        # In Live Mode, active data is live data
        display_df = st.session_state.get("live_flights")
        if display_df is None or display_df.empty:
            display_df = df_flights
        active_features = st.session_state.get("live_features", df_features)
        active_alerts = st.session_state.get("live_alerts", kwargs.get("alerts", []))
    else:
        # In Demo Mode, use pre-loaded flights
        with st.container(border=True):
            st.markdown("##### 📍 Search Offline Synthetic Airspace")
            d_preset = st.selectbox(
                "Select Baseline Airspace Sector:",
                [
                    "🇮🇳 Indian Airspace Baseline (Delhi, Mumbai, Nagpur, Bengaluru)",
                    "🗽 US Northeast Baseline (New York, Boston, JFK)",
                    "🎯 Custom Demo Coordinates",
                ],
                index=0,
            )
            if "Indian Airspace" in d_preset:
                def_lat, def_lon, def_rad = 21.15, 79.09, 850
            elif "US Northeast" in d_preset:
                def_lat, def_lon, def_rad = 41.20, -73.00, 300
            else:
                def_lat, def_lon, def_rad = 21.15, 79.09, 500

            f1, f2, f3 = st.columns([3, 3, 2])
            with f1:
                center_lat = st.number_input("Center Latitude", value=def_lat, min_value=-90.0, max_value=90.0, step=0.1)
            with f2:
                center_lon = st.number_input("Center Longitude", value=def_lon, min_value=-180.0, max_value=180.0, step=0.1)
            with f3:
                radius_km = st.slider("Search Distance", min_value=50, max_value=1200, value=def_rad, step=25, format="%d km")

            display_df = filter_by_radius(df_flights, center_lat, center_lon, float(radius_km))
            if display_df.empty:
                st.info(f"📍 No demo aircraft found within {radius_km} km of ({center_lat:.2f}°, {center_lon:.2f}°). Showing all available flights across the airspace.")
                display_df = df_flights

            active_features = df_features
            active_alerts = kwargs.get("alerts", st.session_state.get("alerts", []))
            miles_radius = round(radius_km * 0.621371)
            st.caption(f"Currently showing baseline flights within **{radius_km} km ({miles_radius} miles)** of ({center_lat:.2f}°, {center_lon:.2f}°).")

    if display_df is None or display_df.empty:
        display_df = df_flights
        active_features = df_features
        active_alerts = kwargs.get("alerts", st.session_state.get("alerts", []))

    # Flightradar24-Style Real-Time Status Ticker
    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        total_ac = display_df["aircraft_id"].nunique()
        st.metric("Airborne Aircraft", f"{total_ac} Aircraft", f"{len(display_df)} live state vectors")
    with m2:
        climbing = (display_df["vertical_rate_fpm"] >= 500).sum() if "vertical_rate_fpm" in display_df.columns else 0
        descending = (display_df["vertical_rate_fpm"] <= -500).sum() if "vertical_rate_fpm" in display_df.columns else 0
        st.metric("Climbing / Descending", f"🔺 {climbing}  /  🔻 {descending}", "Active vertical transitions")
    with m3:
        max_alt = display_df["altitude_ft"].max() if "altitude_ft" in display_df.columns else 0
        st.metric("Highest Flight", f"{max_alt:,.0f} ft", f"FL{round(max_alt/100):03d} • {round(max_alt/5280, 1)} mi")
    with m4:
        st.metric("Kinematic Anomalies", f"{len(active_alerts)} Flagged", "Detected in search radius")

    # 3. Interactive Filter & Search Bar (Flightradar24 Style)
    latest_positions = display_df.sort_values("timestamp").groupby("aircraft_id").last().reset_index()

    # Pre-calculate airline & anomaly metadata
    anomaly_map = {a.aircraft_id: a for a in active_alerts}

    def enrich_flight_record(row):
        aid = row["aircraft_id"]
        cs = row.get("callsign") or aid
        airline_name, iata, flag = decode_airline_info(cs)
        is_anomaly = aid in anomaly_map
        alt = row.get("altitude_ft", 0) or 0
        spd = row.get("ground_speed_kt", 0) or 0
        vr = row.get("vertical_rate_fpm", 0) or 0
        hdg = row.get("heading_deg", 0) or 0

        fl = f"FL{round(alt/100):03d}" if alt >= 18000 else f"{alt:,.0f} ft"
        spd_kmh = round(spd * 1.852)

        return pd.Series({
            "airline_name": airline_name,
            "airline_iata": iata,
            "airline_flag": flag,
            "is_anomaly": is_anomaly,
            "status_color": "#EF4444" if is_anomaly else "#10B981",
            "anomaly_type": anomaly_map[aid].event_type.value if is_anomaly else "Normal",
            "flight_level": fl,
            "speed_kmh": spd_kmh,
            "icon": "✈",
            # Color: Flightradar24 Golden Yellow [245, 158, 11] or Red [239, 68, 68] for anomalies
            "color_r": 239 if is_anomaly else 245,
            "color_g": 68 if is_anomaly else 158,
            "color_b": 68 if is_anomaly else 11,
            "color_a": 255 if is_anomaly else 235,
        })

    enriched = latest_positions.apply(enrich_flight_record, axis=1)
    for col in enriched.columns:
        latest_positions[col] = enriched[col]

    # Quick Search Bar
    with st.container(border=True):
        f_col1, f_col2, f_col3 = st.columns([3, 2, 2])
        with f_col1:
            search_query = st.text_input(
                "🔍 Quick Search Aircraft / Airline / Callsign:",
                placeholder="e.g., IGO, Air India, 6E, AIC, DEL, BOM",
            )
        with f_col2:
            alt_band = st.selectbox(
                "Filter by Altitude Band:",
                ["All Altitudes", "Low (<10,000 ft)", "Mid (10k - 25k ft)", "High Cruise (>25k ft)"],
            )
        with f_col3:
            only_anomalies = st.checkbox("⚠️ Show Only Anomalies", value=False)

    # Apply filters
    filtered_map_df = latest_positions.copy()
    if search_query:
        q = search_query.strip().lower()
        filtered_map_df = filtered_map_df[
            filtered_map_df["aircraft_id"].str.lower().str.contains(q)
            | filtered_map_df["airline_name"].str.lower().str.contains(q)
            | filtered_map_df.get("callsign", pd.Series([""]*len(filtered_map_df))).astype(str).str.lower().str.contains(q)
        ]
    if alt_band == "Low (<10,000 ft)":
        filtered_map_df = filtered_map_df[filtered_map_df["altitude_ft"] < 10000]
    elif alt_band == "Mid (10k - 25k ft)":
        filtered_map_df = filtered_map_df[(filtered_map_df["altitude_ft"] >= 10000) & (filtered_map_df["altitude_ft"] < 25000)]
    elif alt_band == "High Cruise (>25k ft)":
        filtered_map_df = filtered_map_df[filtered_map_df["altitude_ft"] >= 25000]

    if only_anomalies:
        filtered_map_df = filtered_map_df[filtered_map_df["is_anomaly"]]

    # 4. Flightradar24 Tactical Radar Display
    st.markdown("### 🎛️ Tactical Radar Map (Flightradar24 View)")
    st.caption("Golden airplane icons (`✈`) represent live airborne flights rotated to their exact compass heading. Red icons indicate flagged kinematic anomalies.")

    # Radar View Style Switcher
    view_style = st.radio(
        "Radar View Style:",
        ["🗺️ Flightradar24 Tactical Radar Map (Instant Reliable View)", "🟡 3D Vector Deck (PyDeck WebGL)"],
        index=0,
        horizontal=True,
    )

    if filtered_map_df.empty:
        st.warning("No aircraft match the current search filters. Showing all active airspace flights.")
        filtered_map_df = display_df

    # Determine map center
    center_lat = float(filtered_map_df["latitude"].mean()) if not filtered_map_df.empty else 21.15
    center_lon = float(filtered_map_df["longitude"].mean()) if not filtered_map_df.empty else 79.09
    
    # Calculate dynamic zoom
    lat_range = filtered_map_df["latitude"].max() - filtered_map_df["latitude"].min()
    zoom_level = 5.0 if lat_range > 10 else (6.5 if lat_range > 4 else 8.0)

    if "Flightradar24 Tactical Radar Map" in view_style:
        # High-Resolution Plotly Carto Dark Display with Flightradar24 Styling
        filtered_map_df["hover_info"] = filtered_map_df.apply(
            lambda r: f"<b>{r.get('airline_flag', '✈️')} {r.get('airline_name', 'Commercial')}</b><br>"
                      f"Flight / Callsign: <b>{r['aircraft_id']}</b><br>"
                      f"Altitude: <b>{r.get('altitude_ft', 0):,.0f} ft ({r.get('flight_level', 'N/A')})</b><br>"
                      f"Speed: <b>{r.get('ground_speed_kt', 0):.0f} kt ({r.get('speed_kmh', 0)} km/h)</b><br>"
                      f"Vertical Rate: <b>{r.get('vertical_rate_fpm', 0):,.0f} fpm</b><br>"
                      f"Heading: <b>{r.get('heading_deg', 0):.0f}°</b><br>"
                      f"Status: <b>{r.get('anomaly_type', 'Normal')}</b>",
            axis=1,
        )

        fig_map = px.scatter_geo(
            filtered_map_df,
            lat="latitude",
            lon="longitude",
            text="icon",
            hover_name="aircraft_id",
            hover_data={"hover_info": True, "latitude": False, "longitude": False, "icon": False},
            color="altitude_ft",
            color_continuous_scale="Plasma",
            title=f"Airspace Radar ({len(filtered_map_df)} Active Flights Displayed)",
        )
        fig_map.update_traces(
            textposition="middle center",
            textfont=dict(size=20, color="#FBBF24"),
            marker=dict(size=14, color=filtered_map_df.get("status_color", "#10B981"), opacity=0.85),
        )

        # Center properly over Indian subcontinent if within bounds
        mean_lat = float(filtered_map_df["latitude"].mean())
        mean_lon = float(filtered_map_df["longitude"].mean())
        is_india = (5.0 <= mean_lat <= 38.0) and (65.0 <= mean_lon <= 100.0)

        if is_india:
            fig_map.update_geos(
                scope="asia",
                center=dict(lat=21.5, lon=79.5),
                projection_scale=3.8,
                showland=True,
                landcolor="#0B0F19",
                countrycolor="#38BDF8",
                showocean=True,
                oceancolor="#020617",
                showlakes=True,
                lakecolor="#020617",
                showcountries=True,
                showsubunits=True,
                subunitcolor="#1E293B",
            )
        else:
            fig_map.update_geos(
                fitbounds="locations",
                showland=True,
                landcolor="#0B0F19",
                countrycolor="#38BDF8",
                showocean=True,
                oceancolor="#020617",
                showcountries=True,
            )

        fig_map.update_layout(
            height=540,
            margin={"r": 0, "t": 35, "l": 0, "b": 0},
            paper_bgcolor="#0A0E17",
            plot_bgcolor="#0A0E17",
            font=dict(color="#F8FAFC"),
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.caption("📡 *Flightradar24 Tactical Display: Golden aircraft icons (✈) = Nominal Cruise | Red = Flagged Anomaly Exceedance.*")
    else:
        # PyDeck Flightradar24 Tactical Display with Rotated Aircraft Icons
        try:
            deck_df = filtered_map_df.copy()
            deck_df["heading_deg"] = deck_df["heading_deg"].fillna(0).astype(float)
            deck_df["display_color"] = deck_df.apply(lambda r: [r["color_r"], r["color_g"], r["color_b"], r["color_a"]], axis=1)

            icon_layer = pdk.Layer(
                "TextLayer",
                data=deck_df,
                get_position=["longitude", "latitude"],
                get_text="icon",
                get_size=24,
                get_angle="heading_deg",
                get_color="display_color",
                pickable=True,
            )

            halo_layer = pdk.Layer(
                "ScatterplotLayer",
                data=deck_df,
                get_position=["longitude", "latitude"],
                get_radius=12000,
                get_fill_color="display_color",
                opacity=0.25,
                pickable=False,
            )

            view_state = pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=zoom_level,
                pitch=0,
                bearing=0,
            )

            deck = pdk.Deck(
                layers=[halo_layer, icon_layer],
                initial_view_state=view_state,
                map_style=None,
                tooltip={
                    "html": """
                    <div style="background-color: #0F172A; padding: 10px 14px; border-radius: 8px; border: 1.5px solid #F59E0B; font-family: sans-serif; color: white;">
                        <div style="font-size: 14px; font-weight: bold; color: #FBBF24;">✈ {airline_flag} {airline_name} • {aircraft_id}</div>
                        <div style="font-size: 11px; color: #94A3B8; margin-bottom: 6px;">Origin: {origin_country}</div>
                        <div style="font-size: 12px; margin: 3px 0;"><b>Altitude:</b> {altitude_ft} ft ({flight_level})</div>
                        <div style="font-size: 12px; margin: 3px 0;"><b>Ground Speed:</b> {ground_speed_kt} kt ({speed_kmh} km/h)</div>
                        <div style="font-size: 12px; margin: 3px 0;"><b>Climb / Descent:</b> {vertical_rate_fpm} fpm</div>
                        <div style="font-size: 12px; margin: 3px 0;"><b>Heading:</b> {heading_deg}°</div>
                        <div style="font-size: 11px; font-weight: bold; margin-top: 6px; color: {status_color};">
                            Status: {anomaly_type}
                        </div>
                    </div>
                    """,
                    "style": {"backgroundColor": "transparent"},
                },
            )
            st.pydeck_chart(deck, use_container_width=True)
            st.caption("📡 *Flightradar24 Tactical Display: Golden icons = Standard Cruise | Red icons = Flagged Anomaly Alerts.*")
        except Exception as e:
            st.warning(f"Could not load 3D PyDeck WebGL layer: {e}. Switch to the Tactical Radar Map above.")

    st.markdown("---")

    # 5. Flightradar24 Flight Dossier Inspector
    st.markdown("### 🔍 Flightradar24 Aircraft Telemetry Drawer")
    aircraft_options = sorted(filtered_map_df["aircraft_id"].unique()) if not filtered_map_df.empty else sorted(display_df["aircraft_id"].unique())

    def format_dossier_choice(aid: str) -> str:
        row = display_df[display_df["aircraft_id"] == aid].iloc[-1]
        cs = row.get("callsign") or aid
        airline_name, _, flag = decode_airline_info(cs)
        alt = row.get("altitude_ft", 0) or 0
        is_anom = aid in {a.aircraft_id for a in active_alerts}
        status_flag = "⚠️ " if is_anom else "✈️ "
        return f"{status_flag}{aid} • {flag} {airline_name} • {alt:,.0f} ft"

    selected_ac = st.selectbox(
        "Select Flight to Inspect (Flightradar24 Dossier):",
        aircraft_options,
        format_func=format_dossier_choice,
    )

    # Pull observation history
    history_store = st.session_state.get("live_flight_history") if is_live_mode else display_df
    if history_store is not None and not history_store.empty and "aircraft_id" in history_store.columns:
        ac_obs = history_store[history_store["aircraft_id"] == selected_ac].sort_values("timestamp").reset_index(drop=True)
    else:
        ac_obs = display_df[display_df["aircraft_id"] == selected_ac].sort_values("timestamp").reset_index(drop=True)

    if not ac_obs.empty:
        latest = ac_obs.iloc[-1]
        callsign_str = latest.get("callsign") or selected_ac
        airline_name, iata, flag = decode_airline_info(callsign_str)
        is_selected_anomaly = selected_ac in anomaly_map

        # Flightradar24 Header Card
        with st.container(border=True):
            h_col1, h_col2 = st.columns([4, 2])
            with h_col1:
                st.markdown(f"## {flag} `{selected_ac}` — {airline_name} ({iata})")
                st.caption(
                    f"**Callsign:** `{callsign_str}` | **ICAO24:** `{latest.get('icao24', 'N/A').upper()}` | "
                    f"**Country of Registration:** {latest.get('origin_country', 'India')} | **Source:** OpenSky Network (ADS-B)"
                )
            with h_col2:
                if is_selected_anomaly:
                    st.error(f"⚠️ ANOMALY DETECTED\n\n{anomaly_map[selected_ac].event_type.value}")
                else:
                    st.success("🟢 NOMINAL FLIGHT\n\nStandard Cruise Profile")

            # 4 Large Flightradar24 Telemetry Gauges
            g1, g2, g3, g4 = st.columns(4)
            with g1:
                alt_ft = latest.get("altitude_ft", 0) or 0
                fl_str = f"FL{round(alt_ft/100):03d}" if alt_ft >= 18000 else f"{alt_ft:,.0f} ft"
                st.metric("CALIBRATED ALTITUDE", f"{alt_ft:,.0f} ft", fl_str)
                st.caption(f"~{round(alt_ft/5280, 1)} miles high")

            with g2:
                spd_kt = latest.get("ground_speed_kt", 0) or 0
                st.metric("GROUND SPEED", f"{spd_kt:.0f} kt", f"{round(spd_kt * 1.852)} km/h")
                st.caption(f"~{round(spd_kt * 1.151)} mph")

            with g3:
                vr = latest.get("vertical_rate_fpm", 0.0) or 0.0
                direction_arrow = "🔺" if vr >= 300 else ("🔻" if vr <= -300 else "➡️")
                st.metric("VERTICAL RATE", f"{vr:,.0f} fpm", f"{direction_arrow} {vrate_to_human_str(vr)}")
                st.caption(f"~{round(abs(vr)*0.01136, 1)} mph vertical speed")

            with g4:
                hdg = latest.get("heading_deg", 0.0) or 0.0
                cardinals = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
                card_idx = round(hdg / 22.5) % 16
                st.metric("TRACK / HEADING", f"{hdg:.0f}°", cardinals[card_idx])
                st.caption(f"Coordinates: {latest['latitude']:.2f}°, {latest['longitude']:.2f}°")

            # Action: Open Formal Dossier if Anomaly
            if is_selected_anomaly:
                reports_store = st.session_state.get("reports", [])
                alert_obj = anomaly_map[selected_ac]
                existing_rep = next((r for r in reports_store if r.alert_id == alert_obj.alert_id), None)
                st.markdown("---")
                btn_c1, btn_c2 = st.columns([3, 4])
                with btn_c1:
                    if existing_rep:
                        st.info(f"📄 Investigation Dossier `{existing_rep.report_id}` is open in Page 5.")
                    else:
                        if st.button("📝 Open Formal Investigation Dossier", key=f"btn_dossier_{selected_ac}"):
                            new_rep = generate_preliminary_report(alert_obj)
                            reports_store.append(new_rep)
                            st.success(f"Investigation dossier created for {selected_ac}!")
                            st.rerun()
                with btn_c2:
                    st.caption("Captures observed measurements, rate deltas, and explicit unknowns into a formal preliminary report.")

        # Trajectory Time-series Charts
        if len(ac_obs) > 1:
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                fig_alt = px.line(
                    ac_obs,
                    x="timestamp",
                    y="altitude_ft",
                    title=f"Altitude Profile — {selected_ac} ({airline_name})",
                    markers=True,
                    labels={"altitude_ft": "Altitude (feet)", "timestamp": "Time (UTC)"},
                )
                fig_alt.update_layout(height=300, paper_bgcolor="#0A0E17", plot_bgcolor="#0A0E17", font=dict(color="#F8FAFC"))
                st.plotly_chart(fig_alt, use_container_width=True)

            with p_col2:
                fig_spd = px.line(
                    ac_obs,
                    x="timestamp",
                    y="ground_speed_kt",
                    title=f"Ground Speed Profile — {selected_ac}",
                    markers=True,
                    labels={"ground_speed_kt": "Speed (knots)", "timestamp": "Time (UTC)"},
                )
                fig_spd.update_layout(height=300, paper_bgcolor="#0A0E17", plot_bgcolor="#0A0E17", font=dict(color="#F8FAFC"))
                st.plotly_chart(fig_spd, use_container_width=True)
        else:
            st.info(
                f"💡 Showing active real-time radar snapshot for **{selected_ac}** (`{airline_name}`). "
                f"Click **'📡 Scan Live Airspace Now'** periodically to accumulate multi-point flight trajectories."
            )
