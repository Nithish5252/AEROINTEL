"""Page 4: Safety Report Library — Search safety narratives, plain-English summaries, and extracted entities."""

import streamlit as st
import pandas as pd

from aerointel.incidents.search import search_incidents
from aerointel.incidents.summarize import summarize_narrative
from aerointel.incidents.entities import extract_entities
from aerointel.incidents.classify import IncidentClassifier
from aerointel.ui.humanizer import explain_incident_narrative_plain_english


def render_incidents(df_incidents: pd.DataFrame, classifier: IncidentClassifier, plain_english: bool = True, *args, **kwargs):
    """Render the user-friendly Incident Intelligence interface."""
    st.markdown("## 📖 Safety Report Library")
    st.markdown(
        "Aviation is the safest mode of transport because pilots and air traffic controllers write detailed, "
        "transparent reports whenever anything unexpected occurs. Here, our AI reads these reports, extracts the facts, "
        "and summarizes what happened without guessing or exaggerating."
    )

    if df_incidents.empty:
        st.warning("No incident narratives available.")
        return

    # Friendly Search & Filter Bar
    with st.container(border=True):
        st.markdown("##### 🔍 Search Safety Reports")
        s1, s2, s3 = st.columns([3, 2, 2])
        with s1:
            query = st.text_input("Type a keyword (e.g. 'turbulence', 'descent', 'engine', 'runway'):", "")
        with s2:
            categories = ["All Categories"] + sorted(df_incidents["category"].dropna().unique().tolist())
            selected_cat = st.selectbox("Filter by Category:", categories)
        with s3:
            location_q = st.text_input("Airport Code or City (e.g. 'BOS', 'JFK', 'EWR'):", "")

        # Quick Search Suggestions
        st.markdown(
            "💡 *Popular searches: "
            "`turbulence` • `engine vibration` • `oxygen masks` • `taxiway` • `pitot probe`*"
        )

    # Execute Search
    filtered_df = search_incidents(
        df_incidents,
        query=query,
        category=selected_cat,
        location_query=location_q,
    )

    st.markdown(f"**Found {len(filtered_df)} matching safety report(s):**")

    # Render Incidents in Clean, Accessible Cards
    for idx, row in filtered_df.iterrows():
        with st.container(border=True):
            r1, r2 = st.columns([5, 2])
            with r1:
                st.markdown(f"### 📋 `{row['report_id']}` — {row.get('category', 'Safety Event')}")
                st.caption(
                    f"📅 **Date:** {str(row.get('event_date', 'Unknown'))} | "
                    f"📍 **Airport/Location:** {row.get('location', 'N/A')} | "
                    f"✈️ **Aircraft:** {row.get('aircraft_type', 'N/A')}"
                )
            with r2:
                st.markdown("""<span class="badge-pill badge-emerald">Verified Source</span>""", unsafe_allow_html=True)
                st.caption(f"Source: {row.get('source_name', 'Safety Archive')}")

            # 1. Plain English Layperson Translation
            if plain_english:
                plain_cat_desc = explain_incident_narrative_plain_english(
                    str(row.get("category", "")),
                    str(row.get("narrative", ""))
                )
                st.markdown(plain_cat_desc)

            # 2. Extractive Summary (Source Grounded)
            narrative = str(row.get("narrative", ""))
            summary = summarize_narrative(narrative, max_sentences=2)
            st.markdown("##### 📌 Key Facts *(100% Extracted from Official Text, Zero AI Hallucination)*")
            st.info(f"“{summary}”")

            # 3. Extracted Named Entities with Friendly Labels
            entities = extract_entities(narrative)
            with st.expander("🏷️ View Details Extracted by AI (Airports, Altitudes, Equipment)", expanded=False):
                e1, e2, e3 = st.columns(3)
                with e1:
                    st.markdown("**✈️ Airplane Model:**")
                    st.write(entities.get("AIRCRAFT", []) or ["Standard airliner"])
                    st.markdown("**📏 Altitudes / Heights:**")
                    st.write(entities.get("ALTITUDE", []) or ["None mentioned"])
                with e2:
                    st.markdown("**📍 Airport or Waypoint:**")
                    st.write(entities.get("LOCATION_AIRPORT", []) or ["En-route"])
                    st.markdown("**🛣️ Runway / Taxiway:**")
                    st.write(entities.get("RUNWAY_WAYPOINT", []) or ["None"])
                with e3:
                    st.markdown("**🖥️ Cockpit Instrument / System:**")
                    st.write(entities.get("SYSTEM_COMPONENT", []) or ["None"])
                    st.markdown("**🌤️ Weather Conditions:**")
                    st.write(entities.get("WEATHER", []) or ["Clear / Normal"])

            # 4. View Original Narrative
            with st.expander("📄 View Full Original Report Narrative"):
                st.markdown(f"*{narrative}*")

        st.markdown("")
