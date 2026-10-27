"""Page 5: Reports & Investigation — Human-friendly investigation dossiers and evidence correlation."""

import streamlit as st
import pandas as pd

from aerointel.shared.models import PreliminaryReport, LifecycleStatus
from aerointel.shared.lifecycle import transition_report_status, add_report_revision
from aerointel.shared.evidence import evaluate_incident_flight_association
from aerointel.ui.humanizer import altitude_to_human_str, knots_to_mph_str


STATUS_FRIENDLY_LABELS = {
    LifecycleStatus.DETECTED: "🟠 Just Detected (Initial Automated Flag)",
    LifecycleStatus.PRELIMINARY: "🔵 Preliminary Dossier (Under Initial Assessment)",
    LifecycleStatus.UNDER_REVIEW: "🟣 Under Review (Investigator Actively Inspecting)",
    LifecycleStatus.ENRICHED: "🟢 Enriched (Context & Weather Added)",
    LifecycleStatus.CONFIRMED_BY_SOURCE: "✅ Confirmed by Official Source Record",
    LifecycleStatus.CLOSED: "⚪ Closed (Investigation Complete / Archived)",
}


def render_reports(reports_store: list, df_incidents: pd.DataFrame, alerts: list, plain_english: bool = True, *args, **kwargs):
    """Render the user-friendly Preliminary Reports and Investigation interface."""
    st.markdown("## 📑 Investigation Dossiers & Evidence Review")
    st.markdown(
        "When an unusual flight movement is detected, AeroIntel compiles a formal investigation dossier. "
        "Unlike quick guesswork, a good aviation investigation documents **what the instruments recorded**, "
        "**what remains unknown**, and **tracks the case step-by-step** until verified."
    )

    if not reports_store:
        st.info("ℹ️ No investigation dossiers open right now. Go to **Page 3 (Unusual Flight Movements)** and click 'Open Formal Investigation Dossier' on any alert!")
        return

    # Select Report to Inspect
    report_options = [
        f"{r.report_id} — Airplane {r.aircraft_id or 'Unknown'} ({r.event_type})"
        for r in reports_store
    ]
    selected_idx = st.selectbox("Select an Investigation Dossier to Review:", range(len(reports_store)), format_func=lambda i: report_options[i])
    report: PreliminaryReport = reports_store[selected_idx]

    st.markdown("---")

    # Header Row
    h1, h2 = st.columns([5, 3])
    with h1:
        st.markdown(f"### 📂 Case File: `{report.report_id}`")
        st.caption(f"Airplane: **{report.aircraft_id}** | Event Type: **{report.event_type}** | Started: **{report.event_start_utc.strftime('%H:%M:%S UTC')}**")
    with h2:
        status_label = STATUS_FRIENDLY_LABELS.get(report.lifecycle_status, report.lifecycle_status.value)
        st.info(f"**Current Stage:**\n\n{status_label}")

    # 1. Plain-English Summary & Assessment
    st.markdown("#### 📝 Initial Summary")
    st.info(f"“{report.initial_assessment}”")

    # 2. What We Know for Sure (Measurements) vs What is Still Unknown
    st.markdown("#### ⚖️ Evidence Balance Sheet")
    col_know, col_unk = st.columns(2)

    with col_know:
        with st.container(border=True):
            st.markdown("##### ✅ What the Instruments Recorded")
            m = report.observed_measurements or {}
            for k, v in m.items():
                if "altitude" in k:
                    st.write(f"• **Altitude:** {altitude_to_human_str(v)}")
                elif "speed" in k:
                    st.write(f"• **Speed:** {knots_to_mph_str(v)}")
                elif "vertical_rate" in k:
                    st.write(f"• **Climb / Descent Rate:** {v:,.0f} ft/min (~{round(abs(v)*0.01136)} mph vertically)")
                elif "gap" in k:
                    st.write(f"• **Signal Gap:** {v} seconds without radar contact")
                else:
                    st.write(f"• **{k.replace('_', ' ').title()}:** {v}")

    with col_unk:
        with st.container(border=True):
            st.markdown("##### ❓ What We Do NOT Know (Unknowns)")
            for unk in report.unknowns:
                st.write(f"• {unk}")

    st.markdown("---")

    # 3. Correlation with Safety Reports
    st.markdown("#### 🔗 Does this match any Safety Report in our Library?")
    st.caption("We compare this flight's airplane name, time, and location against our safety report archive.")

    matching_alert = next((a for a in alerts if a.alert_id == report.alert_id), None)
    if matching_alert and not df_incidents.empty:
        links = [
            evaluate_incident_flight_association(matching_alert, inc_row.to_dict())
            for _, inc_row in df_incidents.iterrows()
        ]
        supported = [l for l in links if l.is_supported or l.confidence_level == "Needs Review"]

        if supported:
            for l in supported:
                with st.container(border=True):
                    st.markdown(f"**Potential Match Found:** Safety Report `{l.incident_id}` (Confidence: **{l.confidence_level}**)")
                    st.write(f"**Why this might match:** {l.link_rationale}")
                    if l.supporting_evidence:
                        st.markdown("**Matching Clues:**")
                        for s_ev in l.supporting_evidence:
                            st.write(f"• ✅ {s_ev}")
                    if l.limitations:
                        st.markdown("**Remaining Questions / Differences:**")
                        for lim in l.limitations:
                            st.write(f"• ⚠️ {lim}")
        else:
            st.write("ℹ️ *No matching safety report found in our library for this event. This movement may have been a completely routine maneuver.*")

    st.markdown("---")

    # 4. Status Updater
    st.markdown("#### 🔄 Update Investigation Progress")
    with st.expander("Change Investigation Stage or Add Reviewer Notes", expanded=False):
        t1, t2, t3 = st.columns(3)
        with t1:
            all_statuses = [s for s in LifecycleStatus]
            new_status = st.selectbox(
                "New Investigation Stage:",
                all_statuses,
                index=all_statuses.index(report.lifecycle_status),
                format_func=lambda s: STATUS_FRIENDLY_LABELS.get(s, s.value),
            )
        with t2:
            author = st.text_input("Reviewer Name:", value="Safety Analyst")
        with t3:
            evidence_ref = st.text_input("Official Reference (Required for 'Confirmed by Source'):", "")

        notes = st.text_area("Notes for case file:", "Reviewing radar altitude profile and comparing against local ATC sector logs.")

        if st.button("Save Progress"):
            if evidence_ref.strip() and evidence_ref not in report.evidence_references:
                report.evidence_references.append(evidence_ref.strip())
            ok, msg = transition_report_status(report, new_status, author=author, notes=notes)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    # 5. Case History
    with st.expander("📜 View Case Audit History", expanded=False):
        rev_data = [
            {
                "Time (UTC)": r.timestamp_utc.strftime("%Y-%m-%d %H:%M:%S"),
                "User / System": r.author_or_system,
                "Action Taken": r.action,
                "Notes": r.notes,
            }
            for r in report.revision_history
        ]
        st.dataframe(pd.DataFrame(rev_data), use_container_width=True)
