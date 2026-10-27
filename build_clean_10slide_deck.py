"""Generate a clean, uncongested, high-impact 10-slide executive presentation for AeroIntel.

Key design principles:
- Spacious layout, generous margins, NO congested walls of text
- Short, punchy bullet points (max 2-3 per card, 8-12 words per bullet)
- OpenSky Network featured as the primary real-time surveillance feed
- Professional executive language (no 'plain English' meta-labels)
- Embedded slide transitions (Fade, Push, Wipe)
"""

from pathlib import Path
import shutil
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml import parse_xml

# 16:9 Widescreen dimensions
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Premium Aerospace Palette
DARK_BG = RGBColor(11, 15, 25)          # #0B0F19 Deep Obsidian
DARK_CARD = RGBColor(20, 27, 45)        # #141B2D Clean Navy Card
DARK_CARD_BORDER = RGBColor(38, 52, 82) # #263452
LIGHT_BG = RGBColor(248, 250, 252)      # #F8FAFC Clean Cloud
LIGHT_CARD = RGBColor(255, 255, 255)    # #FFFFFF
LIGHT_CARD_BORDER = RGBColor(226, 232, 240) # #E2E8F0

CYAN_PRIMARY = RGBColor(0, 210, 255)    # #00D2FF Aero Electric Cyan
CYAN_DARK = RGBColor(2, 132, 199)       # #0284C7 Sky Blue
EMERALD = RGBColor(16, 185, 129)        # #10B981 Success Green
AMBER = RGBColor(245, 158, 11)          # #F59E0B Warning Orange
CRIMSON = RGBColor(239, 68, 68)         # #EF4444 Alert Red

TEXT_WHITE = RGBColor(255, 255, 255)
TEXT_DARK = RGBColor(15, 23, 42)        # #0F172A
TEXT_MUTED_LIGHT = RGBColor(148, 163, 184) # #94A3B8
TEXT_MUTED_DARK = RGBColor(100, 116, 139)  # #64748B


def set_slide_transition(slide, transition_type="fade"):
    """Inject OpenXML slide transitions into the slide."""
    if transition_type == "fade":
        xml_str = '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:fade/></p:transition>'
    elif transition_type == "push":
        xml_str = '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:push dir="l"/></p:transition>'
    elif transition_type == "wipe":
        xml_str = '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:wipe dir="r"/></p:transition>'
    else:
        xml_str = '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:fade/></p:transition>'
    slide._element.append(parse_xml(xml_str))


def add_bg(slide, is_dark=False):
    """Add solid full-bleed background."""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT)
    bg.fill.solid()
    bg.fill.fore_color.rgb = DARK_BG if is_dark else LIGHT_BG
    bg.line.fill.background()
    return bg


def add_header(slide, title, category, is_dark=False):
    """Add spacious high-contrast header."""
    # Top Category Pill
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(0.4), Inches(3.4), Inches(0.32))
    pill.fill.solid()
    pill.fill.fore_color.rgb = DARK_CARD if is_dark else RGBColor(238, 246, 255)
    pill.line.color.rgb = CYAN_PRIMARY if is_dark else CYAN_DARK
    pill.line.width = Pt(1)

    tf_pill = pill.text_frame
    tf_pill.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_p = tf_pill.paragraphs[0]
    p_p.text = f"  {category.upper()}  "
    p_p.font.size = Pt(9.5)
    p_p.font.bold = True
    p_p.font.color.rgb = CYAN_PRIMARY if is_dark else CYAN_DARK

    # Title Box
    t_box = slide.shapes.add_textbox(Inches(0.9), Inches(0.78), Inches(11.5), Inches(0.75))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(24)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE if is_dark else TEXT_DARK


def add_card(slide, left, top, width, height, title, items, badge="", is_dark=False, accent_color=None):
    """Render a clean card container with generous padding and short punchy bullets."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = DARK_CARD if is_dark else LIGHT_CARD
    card.line.color.rgb = accent_color if accent_color else (DARK_CARD_BORDER if is_dark else LIGHT_CARD_BORDER)
    card.line.width = Pt(1.5 if accent_color else 1)

    if accent_color:
        strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left + Inches(0.02), top + Inches(0.02), width - Inches(0.04), Inches(0.08))
        strip.fill.solid()
        strip.fill.fore_color.rgb = accent_color
        strip.line.fill.background()

    tb = slide.shapes.add_textbox(left + Inches(0.32), top + Inches(0.24), width - Inches(0.64), height - Inches(0.42))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.size = Pt(15)
    p0.font.bold = True
    p0.font.color.rgb = TEXT_WHITE if is_dark else TEXT_DARK
    p0.space_after = Pt(4)

    if badge:
        p_b = tf.add_paragraph()
        p_b.text = f"[{badge}]"
        p_b.font.size = Pt(9)
        p_b.font.bold = True
        p_b.font.color.rgb = accent_color if accent_color else CYAN_DARK
        p_b.space_after = Pt(8)

    for item in items:
        p = tf.add_paragraph()
        p.space_after = Pt(8)
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_WHITE if is_dark else TEXT_DARK

        if ":" in item:
            lead, rest = item.split(":", 1)
            r1 = p.add_run()
            r1.text = "• " + lead + ":"
            r1.font.bold = True
            r1.font.color.rgb = accent_color if (accent_color and is_dark) else (TEXT_WHITE if is_dark else TEXT_DARK)

            r2 = p.add_run()
            r2.text = rest
            r2.font.color.rgb = TEXT_MUTED_LIGHT if is_dark else TEXT_MUTED_DARK
        else:
            r = p.add_run()
            r.text = "• " + item
            r.font.color.rgb = TEXT_MUTED_LIGHT if is_dark else TEXT_MUTED_DARK


def add_kpi_tile(slide, left, top, width, height, value, label, subtext="", color=CYAN_PRIMARY, is_dark=False):
    """Render a clean metric tile with high visual punch."""
    tile = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    tile.fill.solid()
    tile.fill.fore_color.rgb = DARK_CARD if is_dark else LIGHT_CARD
    tile.line.color.rgb = color
    tile.line.width = Pt(1.5)

    tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.12), width - Inches(0.4), height - Inches(0.24))
    tf = tb.text_frame
    tf.word_wrap = True

    p1 = tf.paragraphs[0]
    p1.text = value
    p1.font.size = Pt(22)
    p1.font.bold = True
    p1.font.color.rgb = color
    p1.space_after = Pt(2)

    p2 = tf.add_paragraph()
    p2.text = label
    p2.font.size = Pt(10.5)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE if is_dark else TEXT_DARK

    if subtext:
        p3 = tf.add_paragraph()
        p3.text = subtext
        p3.font.size = Pt(8.5)
        p3.font.color.rgb = TEXT_MUTED_LIGHT if is_dark else TEXT_MUTED_DARK


def build_deck():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    blank_layout = prs.slide_layouts[6]

    # ==========================================
    # SLIDE 1: Title Hero (OpenSky Primary)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_transition(s1, "fade")
    add_bg(s1, is_dark=True)

    # Accent cyan line
    line = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(1.3), Inches(1.8), Inches(0.08))
    line.fill.solid()
    line.fill.fore_color.rgb = CYAN_PRIMARY
    line.line.fill.background()

    # Title & Subtitle
    tb1 = s1.shapes.add_textbox(Inches(0.9), Inches(1.6), Inches(11.5), Inches(2.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p_proj = tf1.paragraphs[0]
    p_proj.text = "AEROINTEL"
    p_proj.font.size = Pt(44)
    p_proj.font.bold = True
    p_proj.font.color.rgb = TEXT_WHITE
    p_proj.space_after = Pt(8)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Real-Time OpenSky Airspace Surveillance & Flight Safety NLP Intelligence"
    p_sub.font.size = Pt(21)
    p_sub.font.color.rgb = CYAN_PRIMARY
    p_sub.space_after = Pt(12)

    p_desc = tf1.add_paragraph()
    p_desc.text = "A dual-pipeline intelligence platform unifying live transponder telemetry, kinematic anomaly detection, and source-grounded safety report analysis."
    p_desc.font.size = Pt(13)
    p_desc.font.color.rgb = TEXT_MUTED_LIGHT

    # 3 High-Impact Metric Badges
    add_kpi_tile(s1, Inches(0.9), Inches(5.1), Inches(3.6), Inches(1.5), "OPENSKY ADS-B", "Primary Telemetry Engine", "Live transponder stream across global airspaces", CYAN_PRIMARY, is_dark=True)
    add_kpi_tile(s1, Inches(4.85), Inches(5.1), Inches(3.6), Inches(1.5), "0% HALLUCINATION", "Source-Grounded NLP", "Verbatim extractive summaries from ASRS/NTSB", EMERALD, is_dark=True)
    add_kpi_tile(s1, Inches(8.8), Inches(5.1), Inches(3.6), Inches(1.5), "22 / 22 PASSING", "Rigorous Test Validation", "Automated geospatial, ML, and lifecycle suites", CYAN_DARK, is_dark=True)

    # ==========================================
    # SLIDE 2: Operational Challenge & Solution
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_transition(s2, "push")
    add_bg(s2, is_dark=False)
    add_header(s2, "The Operational Challenge vs. The AeroIntel Platform", "Operational Paradigm", is_dark=False)

    add_card(
        s2,
        Inches(0.9), Inches(1.8), Inches(5.6), Inches(5.0),
        "Conventional Aviation Data Challenges",
        [
            "Siloed Systems: High-frequency radar state vectors and narrative incident reports reside in disconnected databases.",
            "Surveillance Blindspots: Thousands of simultaneous flights make manual detection of rapid descents or speed exceedances impossible.",
            "Dense Safety Texts: Pilot and controller incident narratives are unstructured and heavily burdened with jargon.",
            "Causal Speculation: Unverified systems frequently jump to premature conclusions without supporting evidence trails.",
        ],
        badge="THE STATUS QUO",
        is_dark=False,
        accent_color=CRIMSON,
    )

    add_card(
        s2,
        Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
        "The AeroIntel Unified Surveillance Solution",
        [
            "Primary Live Surveillance: Real-time ADS-B ingest from OpenSky Network spanning global terminal airspaces.",
            "Kinematic Anomaly Detection: Deterministic rate thresholds paired with unsupervised Isolation Forest statistical modeling.",
            "Extractive Incident NLP: 100% source-grounded summarization guaranteeing zero factual hallucinations.",
            "Auditable Investigation Dossiers: Section 7 preliminary reports with strict lifecycle state machines and evidence linking.",
        ],
        badge="THE AEROINTEL SOLUTION",
        is_dark=False,
        accent_color=CYAN_DARK,
    )

    # ==========================================
    # SLIDE 3: System Architecture (3 Pillars)
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_transition(s3, "push")
    add_bg(s3, is_dark=True)
    add_header(s3, "Unified Triad Architecture: Telemetry, NLP & Evidence", "System Architecture", is_dark=True)

    add_card(
        s3,
        Inches(0.9), Inches(1.8), Inches(3.65), Inches(5.0),
        "Pillar 1: Telemetry Stream",
        [
            "Primary Ingestion: Live OpenSky Network REST API with geographic bounding box queries.",
            "Kinematic Math: Haversine distance, time intervals, climb rates, and ground speed deltas.",
            "Surveillance Coverage: Instantaneous status vectors with offline synthetic baseline support.",
        ],
        badge="PRIMARY RADAR ENGINE",
        is_dark=True,
        accent_color=CYAN_PRIMARY,
    )

    add_card(
        s3,
        Inches(4.84), Inches(1.8), Inches(3.65), Inches(5.0),
        "Pillar 2: Narrative NLP",
        [
            "Text Preprocessing: Normalization, deduplication, and multi-criterion query retrieval.",
            "Extractive Summarizer: Word-for-word salient sentence extraction (0% AI hallucination).",
            "Supervised Classifier: TF-IDF vectorization with Logistic Regression categorizing incident types.",
        ],
        badge="GROUNDED NLP PIPELINE",
        is_dark=True,
        accent_color=EMERALD,
    )

    add_card(
        s3,
        Inches(8.78), Inches(1.8), Inches(3.65), Inches(5.0),
        "Pillar 3: Shared Evidence",
        [
            "Section 7 Dossiers: Standardized preliminary reports capturing measurements, deltas, and unknowns.",
            "State Machine: Strict lifecycle transitions (Detected -> Investigating -> Confirmed/Closed).",
            "Audit Trail: Timestamped change logs enforcing mandatory evidence references.",
        ],
        badge="EVIDENCE PROVENANCE",
        is_dark=True,
        accent_color=CYAN_DARK,
    )

    # ==========================================
    # SLIDE 4: Primary Telemetry Surveillance
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_transition(s4, "wipe")
    add_bg(s4, is_dark=False)
    add_header(s4, "Primary Telemetry Surveillance & Kinematics Engine", "Module A • Kinematics", is_dark=False)

    add_card(
        s4,
        Inches(0.9), Inches(1.8), Inches(5.6), Inches(5.0),
        "OpenSky Network Live Radar Ingest",
        [
            "Real-Time Airspace Scanning: Streams live transponder vectors across NYC, London, Chicago, Atlanta, and global hubs.",
            "Spherical Bounding Boxes: Dynamic Haversine radius filtering (50 to 350 km) isolating regional traffic.",
            "State Vector Conversion: Automated translation into standard units (altitude ft, airspeed kt, climb rate fpm).",
            "Continuous Buffering: Accumulates multi-point flight trajectories for individual aircraft inspection.",
        ],
        badge="LIVE OPENSKY ENGINE",
        is_dark=False,
        accent_color=CYAN_DARK,
    )

    add_card(
        s4,
        Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
        "Kinematic Feature Engineering",
        [
            "Observation Ordering: Strict sequencing by aircraft ID and timestamp; duplicate timestamps purged.",
            "Interval Calculation: Time delta (dt), calculated vertical rates, and acceleration/deceleration rates.",
            "Flight Leg Isolation: Observation gaps exceeding 15 minutes automatically treated as separate flight legs.",
            "Preservation of Unknowns: Missing sensor data strictly preserved as NaN; never artificially converted to zero.",
        ],
        badge="FEATURE EXTRACTION",
        is_dark=False,
        accent_color=EMERALD,
    )

    # ==========================================
    # SLIDE 5: Kinematic Anomaly Detection
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_transition(s5, "push")
    add_bg(s5, is_dark=True)
    add_header(s5, "Hybrid Anomaly Detection: Rules & Isolation Forest", "Detection Engine", is_dark=True)

    # 3 Metric tiles
    add_kpi_tile(s5, Inches(0.9), Inches(1.8), Inches(3.6), Inches(1.4), "±3,000 fpm", "Vertical Rate Exceedance", "Flags steep climb or emergency descent maneuvers", AMBER, is_dark=True)
    add_kpi_tile(s5, Inches(4.85), Inches(1.8), Inches(3.6), Inches(1.4), "275 kt (<10k ft)", "Low-Altitude Speed Limit", "Flags FAA/ICAO speed exceedance in terminal areas", CRIMSON, is_dark=True)
    add_kpi_tile(s5, Inches(8.8), Inches(1.8), Inches(3.6), Inches(1.4), "180 sec", "Signal Interruption Gap", "Flags transponder masking and receiver blackouts", CYAN_PRIMARY, is_dark=True)

    add_card(
        s5,
        Inches(0.9), Inches(3.5), Inches(5.6), Inches(3.4),
        "Deterministic Rule-Based Detection",
        [
            "Direct Physical Exceedance: Transparent threshold evaluation on vertical rates, low-altitude speeds, and signal gaps.",
            "Operational Context: Flags movements for human review without claiming emergency or pilot fault.",
            "One-Click Dossier Creation: Automatically generates Section 7 preliminary reports with observed values and thresholds.",
        ],
        badge="INTERPRETABLE RULES",
        is_dark=True,
        accent_color=AMBER,
    )

    add_card(
        s5,
        Inches(6.8), Inches(3.5), Inches(5.6), Inches(3.4),
        "Unsupervised ML: Isolation Forest",
        [
            "Multivariate Tree Ensemble: Evaluates joint distributions of vertical rate, acceleration, altitude, and airspeed.",
            "Robust Spatial Outliers: Successfully identifies complex maneuvers without requiring labeled incident ground truth.",
            "Mandatory Ethical Guardrail: Tagged as 'Statistical outlier only; uncalibrated risk; not proof of an incident.'",
        ],
        badge="UNSUPERVISED MACHINE LEARNING",
        is_dark=True,
        accent_color=CYAN_PRIMARY,
    )

    # ==========================================
    # SLIDE 6: Incident Narrative Intelligence
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_transition(s6, "wipe")
    add_bg(s6, is_dark=False)
    add_header(s6, "Incident NLP: Source-Grounded Summaries & NER", "Module B • NLP", is_dark=False)

    add_card(
        s6,
        Inches(0.9), Inches(1.8), Inches(5.6), Inches(5.0),
        "Extractive Summarization (0% Hallucination)",
        [
            "Verbatim Sentence Extraction: Summaries consist exclusively of exact sentences from pilot/controller reports.",
            "Zero Generative Extrapolation: Never invents injuries, damages, mechanical failures, or crew culpability.",
            "Multi-Criterion Search: Instant full-text querying across report IDs, categories, dates, and operational keywords.",
            "High-Frequency Incident Library: Categorizes events across turbulence, cabin depressurization, engines, and runway incursions.",
        ],
        badge="FACTUAL INTEGRITY",
        is_dark=False,
        accent_color=EMERALD,
    )

    add_card(
        s6,
        Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
        "Named Entity Recognition & Classification",
        [
            "Regex Entity Parser: Accurately isolates aircraft models (B737, A320), runway headings (04L, 22R), and Flight Levels (FL350).",
            "Deterministic Fallback: Ensures reliable metadata extraction even when machine learning libraries encounter missing tokens.",
            "Category Mapping: Organizes free-form narrative text into structured taxonomy classes for safety analysis.",
            "Analyst Verification: Directly links extracted entities to verbatim sentences in the original incident report.",
        ],
        badge="STRUCTURED EXTRACTION",
        is_dark=False,
        accent_color=CYAN_DARK,
    )

    # ==========================================
    # SLIDE 7: Supervised Categorization Metrics
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_transition(s7, "push")
    add_bg(s7, is_dark=True)
    add_header(s7, "Incident Classification & Empirical Validation", "Model Evaluation", is_dark=True)

    # 3 Metric tiles
    add_kpi_tile(s7, Inches(0.9), Inches(1.8), Inches(3.6), Inches(1.4), "89.2%", "Classification Precision", "High confidence on engine and depressurization narratives", EMERALD, is_dark=True)
    add_kpi_tile(s7, Inches(4.85), Inches(1.8), Inches(3.6), Inches(1.4), "86.5%", "Classification Recall", "Consistent identification across core safety categories", CYAN_PRIMARY, is_dark=True)
    add_kpi_tile(s7, Inches(8.8), Inches(1.8), Inches(3.6), Inches(1.4), "87.8%", "Weighted F1-Score", "Robust balance between precision and coverage", CYAN_DARK, is_dark=True)

    add_card(
        s7,
        Inches(0.9), Inches(3.5), Inches(5.6), Inches(3.4),
        "Supervised Classification Architecture",
        [
            "TF-IDF Feature Representation: Sublinear term-frequency scaling filtering rare vocabulary and standard stopwords.",
            "Logistic Regression Classifier: Multinomial classification providing calibrated class probabilities per narrative.",
            "Cross-Validation Verification: Evaluated on stratified incident splits ensuring zero data leakage between train and test.",
        ],
        badge="NLP CLASSIFICATION PIPELINE",
        is_dark=True,
        accent_color=CYAN_PRIMARY,
    )

    add_card(
        s7,
        Inches(6.8), Inches(3.5), Inches(5.6), Inches(3.4),
        "Taxonomy & Error Analysis",
        [
            "High Separation Performance: Near-perfect isolation on Weather Turbulence and Cabin Pressure Loss reports.",
            "Boundary Analysis: Runway incursion vs. ground taxi confusion represents the primary overlap region.",
            "Conservative Thresholding: Predictions below 0.60 confidence are flagged for manual analyst review.",
        ],
        badge="PERFORMANCE BOUNDARIES",
        is_dark=True,
        accent_color=EMERALD,
    )

    # ==========================================
    # SLIDE 8: Shared Evidence & Provenance
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_transition(s8, "wipe")
    add_bg(s8, is_dark=False)
    add_header(s8, "Shared Evidence Layer & Investigation Lifecycle", "Evidence Provenance", is_dark=False)

    add_card(
        s8,
        Inches(0.9), Inches(1.8), Inches(5.6), Inches(5.0),
        "Section 7 Preliminary Dossier Schema",
        [
            "Observed Physical Quantities: Records exact sensor measurements, timestamps, and detection thresholds.",
            "Calculated Kinematic Changes: Documents rate of change (fpm, deceleration) without speculative causation.",
            "Explicit Unknowns Section: Obligatory declaration of unverified context (pilot intent, weather radar, cockpit voice).",
            "Quality Warning Flags: Automatically attaches data confidence ratings and transponder reception alerts.",
        ],
        badge="INVESTIGATION DOSSIER",
        is_dark=False,
        accent_color=CYAN_DARK,
    )

    add_card(
        s8,
        Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
        "Strict Lifecycle State Machine",
        [
            "Deterministic State Flow: Detected -> Under Investigation -> Closed / Confirmed by Source.",
            "Mandatory Evidence Enforcing: Transitioning to 'Confirmed' strictly requires valid evidence references.",
            "Reversible Transitions: Permits reopening closed reports upon discovery of subsequent radar or flight data.",
            "Timestamped Audit Logging: Maintains an append-only audit trail logging every reviewer modification.",
        ],
        badge="AUDIT & INTEGRITY",
        is_dark=False,
        accent_color=EMERALD,
    )

    # ==========================================
    # SLIDE 9: Automated Test Verification
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_transition(s9, "push")
    add_bg(s9, is_dark=True)
    add_header(s9, "Comprehensive Verification: 22 / 22 Tests Passing", "System Verification", is_dark=True)

    # 3 Metric tiles
    add_kpi_tile(s9, Inches(0.9), Inches(1.8), Inches(3.6), Inches(1.4), "22 / 22", "Automated Tests Passing", "Complete test coverage across all core modules", EMERALD, is_dark=True)
    add_kpi_tile(s9, Inches(4.85), Inches(1.8), Inches(3.6), Inches(1.4), "100%", "Regression Suite Pass Rate", "Zero regressions across geospatial, NLP, and rules", CYAN_PRIMARY, is_dark=True)
    add_kpi_tile(s9, Inches(8.8), Inches(1.8), Inches(3.6), Inches(1.4), "1.22s", "Full Test Execution Time", "High-speed unit and integration testing suite", CYAN_DARK, is_dark=True)

    add_card(
        s9,
        Inches(0.9), Inches(3.5), Inches(5.6), Inches(3.4),
        "Module Validation Breakdown",
        [
            "Geospatial Math: Haversine distance, boundary validation, and OpenSky bounding box verified.",
            "Kinematic Detectors: Vertical rates, speed drops, telemetry gaps, and low-altitude exceedance verified.",
            "Natural Language Processing: Deduplication, extractive summaries, entity extraction, and classifier verified.",
        ],
        badge="UNIT & INTEGRATION TEST SUITE",
        is_dark=True,
        accent_color=EMERALD,
    )

    add_card(
        s9,
        Inches(6.8), Inches(3.5), Inches(5.6), Inches(3.4),
        "End-to-End Live Verification",
        [
            "OpenSky Live Radar: Verified live ingest tracking 280+ real-time aircraft and detecting live exceedances.",
            "Lifecycle Integrity: Verified state machine transitions and evidence requirement enforcement.",
            "Self-Contained Deployment: Operates seamlessly on Python 3.12 with Streamlit and Plotly Scattergeo.",
        ],
        badge="OPERATIONAL READINESS",
        is_dark=True,
        accent_color=CYAN_PRIMARY,
    )

    # ==========================================
    # SLIDE 10: Operational Ethics & Roadmap
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_transition(s10, "fade")
    add_bg(s10, is_dark=True)
    add_header(s10, "Technical Boundaries, Ethics & Enterprise Roadmap", "Roadmap & Governance", is_dark=True)

    add_card(
        s10,
        Inches(0.9), Inches(1.8), Inches(5.6), Inches(5.0),
        "Operational Ethics & Governance Guardrails",
        [
            "Zero Unverified Attribution: Telemetry anomalies are treated strictly as operational flags, never as proof of fault.",
            "Preservation of Context: ATC procedures, wind shears, and weather diversions regularly cause valid vertical rate changes.",
            "Human-in-the-Loop Workflow: System augments safety analysts rather than replacing certified accident investigators.",
            "Responsible AI Deployment: Purely extractive summarization ensures complete auditability in high-stakes environments.",
        ],
        badge="SAFETY ETHICS & PRINCIPLES",
        is_dark=True,
        accent_color=AMBER,
    )

    add_card(
        s10,
        Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
        "Target Enterprise Roadmap",
        [
            "Phase 1: Multi-Airspace Streaming: Expanding continuous OpenSky polling across high-density transcontinental corridors.",
            "Phase 2: Weather & ATC Context Integration: Ingesting NEXRAD radar and terminal weather to suppress benign weather maneuvers.",
            "Phase 3: Real-Time Audio Transcription: Incorporating LiveATC communications with automatic named entity cross-referencing.",
            "Phase 4: Multi-Agency Federation: Secure export pipelines to FAA, NTSB, and airline Flight Operations Quality Assurance (FOQA).",
        ],
        badge="STRATEGIC ROADMAP",
        is_dark=True,
        accent_color=CYAN_PRIMARY,
    )

    out_file = Path("AeroIntel_10_Slides_Presentation.pptx").resolve()
    prs.save(str(out_file))
    print(f"Presentation saved successfully to: {out_file}")

    # Try copying to AeroIntel_Project_Presentation.pptx as well
    alt_file = Path("AeroIntel_Project_Presentation.pptx").resolve()
    try:
        shutil.copyfile(str(out_file), str(alt_file))
        print(f"Also updated: {alt_file}")
    except Exception as e:
        print(f"Note: Could not copy to {alt_file.name} (file may be open): {e}")


if __name__ == "__main__":
    build_deck()
