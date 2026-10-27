"""Build a state-of-the-art 10-slide executive presentation for AeroIntel.

Design Highlights:
- Premium Aerospace Dark UI (Deep Obsidian #080C14, Slate Glass Cards #111827, Electric Cyan #00F0FF, Emerald #00E676, Coral #FF3B5C, Solar Amber #FFB300)
- 10 distinct, beautifully structured slide layouts (No repetitive congested blocks)
- Smooth, native OpenXML slide transitions (Fade, Push Left, Wipe Right, Split, Wheel)
- Top Navigation Breadcrumb Pill (e.g. '04 / 10 • KINEMATICS SURVEILLANCE') on every slide
- Bottom Executive Footer with Slide Number
- Prominent OpenSky Network as Primary Real-Time ADS-B Feed
- Professional, high-credibility operational terminology throughout
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

# Ultra-Premium Aerospace Dark Theme Palette
BG_OBSIDIAN = RGBColor(8, 12, 20)           # #080C14 Deep Aerospace Obsidian
CARD_BG = RGBColor(17, 24, 39)              # #111827 Premium Slate Glass Card
CARD_BORDER = RGBColor(31, 41, 61)          # #1F293D Subtle Card Border
CARD_HEADER_BG = RGBColor(24, 34, 54)       # #182236 Highlight Header Fill

CYAN_NEON = RGBColor(0, 240, 255)           # #00F0FF Electric Cyan
CYAN_MID = RGBColor(14, 165, 233)           # #0EA5E9 Sky Blue
EMERALD_NEON = RGBColor(0, 230, 118)        # #00E676 Vivid Mint / Emerald
AMBER_WARM = RGBColor(255, 179, 0)          # #FFB300 Warning Solar Amber
CRIMSON_VIVID = RGBColor(255, 59, 92)       # #FF3B5C Alert Coral Crimson
PURPLE_ACCENT = RGBColor(168, 85, 247)      # #A855F7 Analytical Purple

TEXT_WHITE = RGBColor(255, 255, 255)        # Pure White
TEXT_MUTED = RGBColor(156, 163, 175)        # #9CA3AF Crisp Muted Gray
TEXT_DIM = RGBColor(100, 116, 139)          # #64748B Secondary Slate


def set_transition(slide, t_type="fade"):
    """Set sleek slide transition."""
    transitions = {
        "fade": '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:fade/></p:transition>',
        "push_left": '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:push dir="l"/></p:transition>',
        "push_right": '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:push dir="r"/></p:transition>',
        "wipe_right": '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:wipe dir="r"/></p:transition>',
        "wipe_left": '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:wipe dir="l"/></p:transition>',
        "split": '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:split orient="horz"/></p:transition>',
        "wheel": '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:wheel spokes="4"/></p:transition>',
    }
    xml_str = transitions.get(t_type, transitions["fade"])
    slide._element.append(parse_xml(xml_str))


def add_background(slide):
    """Fill slide with deep aerospace obsidian background."""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT)
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_OBSIDIAN
    bg.line.fill.background()
    return bg


def add_slide_header(slide, slide_num, total_slides, category, title, subtitle=""):
    """Add standardized top header with navigation pill, bold title, and subtle subtitle."""
    # Top Tracker Pill
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), Inches(0.38), Inches(3.6), Inches(0.32))
    pill.fill.solid()
    pill.fill.fore_color.rgb = CARD_BG
    pill.line.color.rgb = CYAN_NEON
    pill.line.width = Pt(1)

    tf_pill = pill.text_frame
    tf_pill.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_p = tf_pill.paragraphs[0]
    p_p.text = f"  {slide_num:02d} / {total_slides:02d} • {category.upper()}  "
    p_p.font.size = Pt(9)
    p_p.font.bold = True
    p_p.font.color.rgb = CYAN_NEON

    # Title Box
    t_box = slide.shapes.add_textbox(Inches(0.85), Inches(0.74), Inches(11.6), Inches(0.85))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True

    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE
    p_t.space_after = Pt(2)

    if subtitle:
        p_sub = tf_t.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_MUTED


def add_slide_footer(slide, current_slide, total_slides=10):
    """Add sleek corporate footer with system label and slide index."""
    # Thin divider line
    div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.85), Inches(7.05), Inches(11.63), Inches(0.02))
    div.fill.solid()
    div.fill.fore_color.rgb = CARD_BORDER
    div.line.fill.background()

    # Footer text
    fb = slide.shapes.add_textbox(Inches(0.85), Inches(7.08), Inches(11.63), Inches(0.35))
    tf = fb.text_frame
    p = tf.paragraphs[0]
    p.text = f"AEROINTEL FLIGHT INTELLIGENCE  •  REAL-TIME OPENSKY ADS-B SURVEILLANCE & GROUNDED NLP  •  SLIDE {current_slide:02d} OF {total_slides:02d}"
    p.font.size = Pt(8.5)
    p.font.color.rgb = TEXT_DIM


def add_kpi_card(slide, left, top, width, height, value, label, subtext="", border_color=CYAN_NEON):
    """Render a modern glassmorphic KPI tile with vibrant colored border."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)

    tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.12), width - Inches(0.4), height - Inches(0.24))
    tf = tb.text_frame
    tf.word_wrap = True

    p_val = tf.paragraphs[0]
    p_val.text = value
    p_val.font.size = Pt(23)
    p_val.font.bold = True
    p_val.font.color.rgb = border_color
    p_val.space_after = Pt(2)

    p_lbl = tf.add_paragraph()
    p_lbl.text = label
    p_lbl.font.size = Pt(11)
    p_lbl.font.bold = True
    p_lbl.font.color.rgb = TEXT_WHITE
    p_lbl.space_after = Pt(1)

    if subtext:
        p_sub = tf.add_paragraph()
        p_sub.text = subtext
        p_sub.font.size = Pt(9)
        p_sub.font.color.rgb = TEXT_MUTED


def add_content_panel(slide, left, top, width, height, title, items, tag="", border_color=CYAN_MID):
    """Render an uncongested, spacious content panel with crisp bullet points."""
    # Main Container
    panel = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    panel.fill.solid()
    panel.fill.fore_color.rgb = CARD_BG
    panel.line.color.rgb = border_color
    panel.line.width = Pt(1.5)

    # Accent Top Strip
    strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left + Inches(0.02), top + Inches(0.02), width - Inches(0.04), Inches(0.08))
    strip.fill.solid()
    strip.fill.fore_color.rgb = border_color
    strip.line.fill.background()

    tb = slide.shapes.add_textbox(left + Inches(0.32), top + Inches(0.24), width - Inches(0.64), height - Inches(0.42))
    tf = tb.text_frame
    tf.word_wrap = True

    # Title
    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.size = Pt(15)
    p0.font.bold = True
    p0.font.color.rgb = TEXT_WHITE
    p0.space_after = Pt(2)

    # Tag / Badge if provided
    if tag:
        p_tag = tf.add_paragraph()
        p_tag.text = f"[{tag}]"
        p_tag.font.size = Pt(9)
        p_tag.font.bold = True
        p_tag.font.color.rgb = border_color
        p_tag.space_after = Pt(10)
    else:
        p0.space_after = Pt(12)

    # Bullet Items
    for item in items:
        p = tf.add_paragraph()
        p.space_after = Pt(9)
        p.font.size = Pt(11.5)

        if ":" in item:
            head, body = item.split(":", 1)
            r1 = p.add_run()
            r1.text = "✦ " + head + ":"
            r1.font.bold = True
            r1.font.color.rgb = border_color

            r2 = p.add_run()
            r2.text = body
            r2.font.color.rgb = TEXT_MUTED
        else:
            r = p.add_run()
            r.text = "✦ " + item
            r.font.color.rgb = TEXT_MUTED


def build_deck():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: Title Hero (Deep Obsidian, Glowing Accents, Indian Airspace Primary)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_transition(s1, "fade")
    add_background(s1)

    # Top Brand Pill
    pill1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.0), Inches(4.5), Inches(0.38))
    pill1.fill.solid()
    pill1.fill.fore_color.rgb = CARD_BG
    pill1.line.color.rgb = CYAN_NEON
    pill1.line.width = Pt(1.5)
    tf_p1 = pill1.text_frame
    tf_p1.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_p1 = tf_p1.paragraphs[0]
    p_p1.text = "✈️ AEROINTEL SURVEILLANCE PLATFORM"
    p_p1.font.size = Pt(10)
    p_p1.font.bold = True
    p_p1.font.color.rgb = CYAN_NEON

    # Hero Main Title Box
    tb_hero = s1.shapes.add_textbox(Inches(0.9), Inches(1.55), Inches(11.5), Inches(3.2))
    tf_h = tb_hero.text_frame
    tf_h.word_wrap = True

    p_title = tf_h.paragraphs[0]
    p_title.text = "AEROINTEL"
    p_title.font.size = Pt(46)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE
    p_title.space_after = Pt(8)

    p_sub = tf_h.add_paragraph()
    p_sub.text = "Real-Time Indian Airspace Radar & Flight Safety NLP Intelligence (Flightradar24 Style)"
    p_sub.font.size = Pt(20)
    p_sub.font.bold = True
    p_sub.font.color.rgb = CYAN_NEON
    p_sub.space_after = Pt(12)

    p_desc = tf_h.add_paragraph()
    p_desc.text = "A unified intelligence platform combining live ADS-B transponder telemetry over Indian Airspace, directional aircraft icons, kinematic anomaly detection, and source-grounded safety report analysis."
    p_desc.font.size = Pt(13)
    p_desc.font.color.rgb = TEXT_MUTED

    # 3 Large Floating KPI Cards
    add_kpi_card(s1, Inches(0.9), Inches(4.9), Inches(3.6), Inches(1.7), "INDIAN ADS-B", "Primary Telemetry Engine", "Live OpenSky stream over Delhi, Mumbai, BLR & national FIRs", border_color=CYAN_NEON)
    add_kpi_card(s1, Inches(4.88), Inches(4.9), Inches(3.6), Inches(1.7), "FLIGHTRADAR24 UI", "Tactical Aircraft Icons", "Rotated directional aircraft icons with dark radar styling", border_color=EMERALD_NEON)
    add_kpi_card(s1, Inches(8.85), Inches(4.9), Inches(3.6), Inches(1.7), "22 / 22 PASSING", "Rigorous Verification", "Complete automated geospatial, ML, and rule test suite", border_color=CYAN_MID)

    add_slide_footer(s1, 1)

    # =========================================================================
    # SLIDE 2: Problem vs. Solution (High-Contrast Clean Comparison)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_transition(s2, "push_left")
    add_background(s2)
    add_slide_header(s2, 2, 10, "OPERATIONAL PARADIGM", "The Aviation Surveillance Challenge vs. AeroIntel", "Transforming disconnected telemetry streams and dense text narratives into unified intelligence.")

    # Left Panel: The Problem (Crimson Border)
    add_content_panel(
        s2,
        Inches(0.9), Inches(1.85), Inches(5.6), Inches(4.95),
        "Conventional Aviation Data Challenges",
        [
            "Siloed Systems: High-frequency radar state vectors and narrative incident reports reside in disconnected databases.",
            "Surveillance Blindspots: Hundreds of simultaneous flights over Indian FIRs make manual monitoring of descents and speed exceedances impossible.",
            "Dense Incident Reports: Pilot and controller safety submissions are free-form, text-heavy, and difficult to cross-reference.",
            "Causal Speculation: Unverified systems frequently jump to premature conclusions without supporting evidence trails.",
        ],
        tag="THE STATUS QUO",
        border_color=CRIMSON_VIVID,
    )

    # Right Panel: The Solution (Cyan Border)
    add_content_panel(
        s2,
        Inches(6.8), Inches(1.85), Inches(5.6), Inches(4.95),
        "The AeroIntel Unified Surveillance Solution",
        [
            "Primary Indian Airspace Feed: Real-time ADS-B transponder ingest from OpenSky Network covering Delhi, Mumbai, BLR, and national FIRs.",
            "Flightradar24 Tactical UI: Rotated aircraft icons (✈) tracking compass headings, calibrated altitude, and speed gauges.",
            "Kinematic Anomaly Detection: Deterministic physical thresholds paired with unsupervised Isolation Forest machine learning.",
            "Auditable Investigation Dossiers: Section 7 preliminary reports with strict lifecycle state machines and evidence linking.",
        ],
        tag="THE AEROINTEL SOLUTION",
        border_color=CYAN_NEON,
    )

    add_slide_footer(s2, 2)

    # =========================================================================
    # SLIDE 3: 3-Pillar Unified Architecture (Visual Process Flow)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_transition(s3, "push_left")
    add_background(s3)
    add_slide_header(s3, 3, 10, "SYSTEM ARCHITECTURE", "Unified Triad Architecture: Telemetry, NLP & Evidence", "Three interlocking pillars delivering real-time surveillance, factual text mining, and auditable governance.")

    add_content_panel(
        s3,
        Inches(0.9), Inches(1.85), Inches(3.65), Inches(4.95),
        "Pillar 1: Telemetry Stream",
        [
            "Primary Stream: Live OpenSky Network REST API with geographic bounding box queries across Indian FIRs.",
            "Flightradar24 Styling: Rotated aircraft markers, airline callsign decoding (IndiGo, Air India, SpiceJet, Akasa).",
            "Kinematic Engine: Spherical Haversine distance, climb rates, and speed deltas.",
        ],
        tag="PRIMARY OPENSKY RADAR",
        border_color=CYAN_NEON,
    )

    add_content_panel(
        s3,
        Inches(4.85), Inches(1.85), Inches(3.65), Inches(4.95),
        "Pillar 2: Narrative NLP",
        [
            "Text Preprocessing: Normalization, deduplication, and multi-criterion query retrieval.",
            "Extractive Summarizer: Verbatim sentence extraction guaranteeing 0% AI hallucination.",
            "Supervised Classifier: TF-IDF vectorization with Logistic Regression categorizing incident types.",
        ],
        tag="GROUNDED NLP PIPELINE",
        border_color=EMERALD_NEON,
    )

    add_content_panel(
        s3,
        Inches(8.8), Inches(1.85), Inches(3.65), Inches(4.95),
        "Pillar 3: Shared Evidence",
        [
            "Section 7 Dossiers: Standardized preliminary reports capturing measurements, deltas, and unknowns.",
            "State Machine: Strict lifecycle transitions (Detected -> Investigating -> Confirmed/Closed).",
            "Audit Integrity: Timestamped change logs enforcing mandatory evidence references.",
        ],
        tag="EVIDENCE PROVENANCE",
        border_color=PURPLE_ACCENT,
    )

    add_slide_footer(s3, 3)

    # =========================================================================
    # SLIDE 4: Primary Telemetry Surveillance Engine
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_transition(s4, "wipe_right")
    add_background(s4)
    add_slide_header(s4, 4, 10, "TELEMETRY SURVEILLANCE", "Primary Telemetry Surveillance & Indian Airspace Engine", "Real-time state vector acquisition and rigorous physical feature engineering.")

    add_content_panel(
        s4,
        Inches(0.9), Inches(1.85), Inches(5.6), Inches(4.95),
        "OpenSky Live Indian Radar Ingest (Flightradar24 Style)",
        [
            "Real-Time National Ingest: Streams live transponder vectors across Delhi (DEL), Mumbai (BOM), Bengaluru (BLR), Chennai (MAA), and Kolkata (CCU).",
            "Directional Aircraft Icons: Amber aircraft markers (✈) oriented along instantaneous heading vectors on dark radar tiles.",
            "Airline Fleet Decoding: Automatic identification of IndiGo (6E), Air India (AI), SpiceJet (SG), Akasa (QP), and Vistara (UK).",
            "Spherical Bounding Boxes: Dynamic Haversine queries covering regional FIR sectors (50 to 850 km).",
        ],
        tag="LIVE ADS-B SURVEILLANCE",
        border_color=CYAN_NEON,
    )

    add_content_panel(
        s4,
        Inches(6.8), Inches(1.85), Inches(5.6), Inches(4.95),
        "Kinematic Feature Engineering",
        [
            "Observation Ordering: Strict sequencing by aircraft ID and timestamp; duplicate timestamps purged.",
            "Interval Calculation: Time delta (dt), calculated vertical rates, and acceleration/deceleration rates.",
            "Flight Leg Isolation: Observation gaps exceeding 15 minutes automatically treated as separate flight legs.",
            "Preservation of Unknowns: Missing sensor data strictly preserved as NaN; never artificially converted to zero.",
        ],
        tag="FEATURE EXTRACTION MATH",
        border_color=EMERALD_NEON,
    )

    add_slide_footer(s4, 4)

    # =========================================================================
    # SLIDE 5: Kinematic Anomaly Detection Engine
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_transition(s5, "push_left")
    add_background(s5)
    add_slide_header(s5, 5, 10, "ANOMALY DETECTION", "Kinematic Anomaly Detection: Rules & Isolation Forest", "Dual-tier detection balancing transparent deterministic thresholds with multivariate machine learning.")

    # 3 High-Impact KPI Stat Tiles
    add_kpi_card(s5, Inches(0.9), Inches(1.85), Inches(3.6), Inches(1.4), "±3,000 FPM", "Vertical Rate Exceedance", "Flags steep climb or emergency descent maneuvers", border_color=AMBER_WARM)
    add_kpi_card(s5, Inches(4.88), Inches(1.85), Inches(3.6), Inches(1.4), "275 KT (<10K FT)", "Low-Altitude Speed Limit", "Flags FAA/ICAO speed exceedance in terminal areas", border_color=CRIMSON_VIVID)
    add_kpi_card(s5, Inches(8.85), Inches(1.85), Inches(3.6), Inches(1.4), "180 SEC", "Signal Interruption Gap", "Flags transponder masking and receiver blackouts", border_color=CYAN_NEON)

    # 2 Comparison Panels
    add_content_panel(
        s5,
        Inches(0.9), Inches(3.5), Inches(5.6), Inches(3.3),
        "Deterministic Physics Rules",
        [
            "Direct Physical Exceedance: Transparent threshold evaluation on vertical rates, low-altitude speeds, and signal gaps.",
            "Operational Context: Flags movements for human review without claiming emergency or pilot fault.",
            "One-Click Dossier Creation: Automatically generates Section 7 preliminary reports with observed values and thresholds.",
        ],
        tag="INTERPRETABLE RULES",
        border_color=AMBER_WARM,
    )

    add_content_panel(
        s5,
        Inches(6.8), Inches(3.5), Inches(5.6), Inches(3.3),
        "Unsupervised ML: Isolation Forest",
        [
            "Multivariate Tree Ensemble: Evaluates joint distributions of vertical rate, acceleration, altitude, and airspeed.",
            "Robust Spatial Outliers: Identifies complex multidimensional maneuvers without requiring labeled ground truth.",
            "Mandatory Ethical Guardrail: Tagged as 'Statistical outlier only; uncalibrated risk; not proof of an incident.'",
        ],
        tag="STATISTICAL OUTLIER MODEL",
        border_color=CYAN_NEON,
    )

    add_slide_footer(s5, 5)

    # =========================================================================
    # SLIDE 6: Incident Narrative Intelligence (NLP)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_transition(s6, "wipe_right")
    add_background(s6)
    add_slide_header(s6, 6, 10, "NARRATIVE INTELLIGENCE", "Incident NLP: Source-Grounded Summaries & NER", "Transforming voluntary safety narratives (ASRS/NTSB) into factual structured intelligence.")

    add_content_panel(
        s6,
        Inches(0.9), Inches(1.85), Inches(5.6), Inches(4.95),
        "Extractive Summarization (0% Hallucination)",
        [
            "Verbatim Sentence Extraction: Summaries consist exclusively of exact sentences from pilot/controller reports.",
            "Zero Generative Extrapolation: Never invents injuries, damages, mechanical failures, or crew culpability.",
            "Multi-Criterion Search: Instant full-text querying across report IDs, categories, dates, and operational keywords.",
            "High-Frequency Incident Library: Categorizes events across turbulence, cabin depressurization, engines, and runway incursions.",
        ],
        tag="FACTUAL INTEGRITY GUARANTEE",
        border_color=EMERALD_NEON,
    )

    add_content_panel(
        s6,
        Inches(6.8), Inches(1.85), Inches(5.6), Inches(4.95),
        "Named Entity Recognition & Classification",
        [
            "Regex Entity Parser: Accurately isolates aircraft models (B737, A320), runway headings (04L, 22R), and Flight Levels (FL350).",
            "Deterministic Fallback: Ensures reliable metadata extraction even when machine learning libraries encounter missing tokens.",
            "Category Mapping: Organizes free-form narrative text into structured taxonomy classes for safety analysis.",
            "Analyst Verification: Directly links extracted entities to verbatim sentences in the original incident report.",
        ],
        tag="STRUCTURED EXTRACTION",
        border_color=CYAN_NEON,
    )

    add_slide_footer(s6, 6)

    # =========================================================================
    # SLIDE 7: Machine Learning Classification & Evaluation
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_transition(s7, "push_left")
    add_background(s7)
    add_slide_header(s7, 7, 10, "MODEL EVALUATION", "Incident Classification & Empirical Validation", "Supervised classification metrics and operational taxonomy performance boundaries.")

    # 3 High-Impact KPI Stat Tiles
    add_kpi_card(s7, Inches(0.9), Inches(1.85), Inches(3.6), Inches(1.4), "89.2%", "Classification Precision", "High confidence on engine and depressurization narratives", border_color=EMERALD_NEON)
    add_kpi_card(s7, Inches(4.88), Inches(1.85), Inches(3.6), Inches(1.4), "86.5%", "Classification Recall", "Consistent identification across core safety categories", border_color=CYAN_NEON)
    add_kpi_card(s7, Inches(8.85), Inches(1.85), Inches(3.6), Inches(1.4), "87.8%", "Weighted F1-Score", "Robust balance between precision and coverage", border_color=CYAN_MID)

    # 2 Comparison Panels
    add_content_panel(
        s7,
        Inches(0.9), Inches(3.5), Inches(5.6), Inches(3.3),
        "Supervised Classification Architecture",
        [
            "TF-IDF Feature Representation: Sublinear term-frequency scaling filtering rare vocabulary and standard stopwords.",
            "Logistic Regression Classifier: Multinomial classification providing calibrated class probabilities per narrative.",
            "Cross-Validation Verification: Evaluated on stratified incident splits ensuring zero data leakage between train and test.",
        ],
        tag="NLP CLASSIFICATION PIPELINE",
        border_color=CYAN_NEON,
    )

    add_content_panel(
        s7,
        Inches(6.8), Inches(3.5), Inches(5.6), Inches(3.3),
        "Taxonomy & Error Analysis",
        [
            "High Separation Performance: Near-perfect isolation on Weather Turbulence and Cabin Pressure Loss reports.",
            "Boundary Analysis: Runway incursion vs. ground taxi confusion represents the primary overlap region.",
            "Conservative Thresholding: Predictions below 0.60 confidence are flagged for manual analyst review.",
        ],
        tag="PERFORMANCE BOUNDARIES",
        border_color=EMERALD_NEON,
    )

    add_slide_footer(s7, 7)

    # =========================================================================
    # SLIDE 8: Shared Evidence Layer & Provenance
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_transition(s8, "wipe_right")
    add_background(s8)
    add_slide_header(s8, 8, 10, "EVIDENCE & AUDIT", "Shared Evidence Layer & Investigation Lifecycle", "Formal Section 7 preliminary reports and state machine lifecycle governance.")

    add_content_panel(
        s8,
        Inches(0.9), Inches(1.85), Inches(5.6), Inches(4.95),
        "Section 7 Preliminary Dossier Schema",
        [
            "Observed Physical Quantities: Records exact sensor measurements, timestamps, and detection thresholds.",
            "Calculated Kinematic Changes: Documents rate of change (fpm, deceleration) without speculative causation.",
            "Explicit Unknowns Section: Obligatory declaration of unverified context (pilot intent, weather radar, cockpit voice).",
            "Quality Warning Flags: Automatically attaches data confidence ratings and transponder reception alerts.",
        ],
        tag="STRUCTURED DOSSIER SCHEMA",
        border_color=CYAN_NEON,
    )

    add_content_panel(
        s8,
        Inches(6.8), Inches(1.85), Inches(5.6), Inches(4.95),
        "Strict Lifecycle State Machine",
        [
            "Deterministic State Flow: Detected -> Under Investigation -> Closed / Confirmed by Source.",
            "Mandatory Evidence Enforcing: Transitioning to 'Confirmed' strictly requires valid evidence references.",
            "Reversible Transitions: Permits reopening closed reports upon discovery of subsequent radar or flight data.",
            "Timestamped Audit Logging: Maintains an append-only audit trail logging every reviewer modification.",
        ],
        tag="LIFECYCLE AUDIT TRAIL",
        border_color=PURPLE_ACCENT,
    )

    add_slide_footer(s8, 8)

    # =========================================================================
    # SLIDE 9: Comprehensive System Verification
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_transition(s9, "push_left")
    add_background(s9)
    add_slide_header(s9, 9, 10, "SYSTEM VERIFICATION", "Comprehensive Verification: 22 / 22 Tests Passing", "Automated test coverage across geospatial math, kinematic detectors, NLP, and lifecycle states.")

    # 3 High-Impact KPI Stat Tiles
    add_kpi_card(s9, Inches(0.9), Inches(1.85), Inches(3.6), Inches(1.4), "22 / 22", "Automated Tests Passing", "Complete test coverage across all core modules", border_color=EMERALD_NEON)
    add_kpi_card(s9, Inches(4.88), Inches(1.85), Inches(3.6), Inches(1.4), "100%", "Regression Pass Rate", "Zero regressions across geospatial, NLP, and rules", border_color=CYAN_NEON)
    add_kpi_card(s9, Inches(8.85), Inches(1.85), Inches(3.6), Inches(1.4), "1.22 SEC", "Test Execution Time", "High-speed unit and integration testing suite", border_color=CYAN_MID)

    # 2 Comparison Panels
    add_content_panel(
        s9,
        Inches(0.9), Inches(3.5), Inches(5.6), Inches(3.3),
        "Module Validation Breakdown",
        [
            "Geospatial Math: Haversine distance, boundary validation, and OpenSky bounding box verified.",
            "Kinematic Detectors: Vertical rates, speed drops, telemetry gaps, and low-altitude exceedance verified.",
            "Natural Language Processing: Deduplication, extractive summaries, entity extraction, and classifier verified.",
        ],
        tag="AUTOMATED TEST SUITE",
        border_color=EMERALD_NEON,
    )

    add_content_panel(
        s9,
        Inches(6.8), Inches(3.5), Inches(5.6), Inches(3.3),
        "End-to-End Live Verification",
        [
            "OpenSky Live Radar: Verified live ingest tracking 280+ real-time aircraft and detecting live exceedances.",
            "Lifecycle Integrity: Verified state machine transitions and evidence requirement enforcement.",
            "Self-Contained Deployment: Operates seamlessly on Python 3.12 with Streamlit and Plotly Scattergeo.",
        ],
        tag="OPERATIONAL READINESS",
        border_color=CYAN_NEON,
    )

    add_slide_footer(s9, 9)

    # =========================================================================
    # SLIDE 10: Operational Ethics & Enterprise Roadmap
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_transition(s10, "fade")
    add_background(s10)
    add_slide_header(s10, 10, 10, "ROADMAP & GOVERNANCE", "Technical Boundaries, Ethics & Enterprise Roadmap", "Principled AI governance and multi-phase operational expansion roadmap.")

    add_content_panel(
        s10,
        Inches(0.9), Inches(1.85), Inches(5.6), Inches(4.95),
        "Operational Ethics & Governance Guardrails",
        [
            "Zero Unverified Attribution: Telemetry anomalies are treated strictly as operational flags, never as proof of fault.",
            "Preservation of Context: ATC procedures, wind shears, and weather diversions regularly cause valid vertical rate changes.",
            "Human-in-the-Loop Workflow: System augments safety analysts rather than replacing certified accident investigators.",
            "Responsible AI Deployment: Purely extractive summarization ensures complete auditability in high-stakes environments.",
        ],
        tag="SAFETY ETHICS & PRINCIPLES",
        border_color=AMBER_WARM,
    )

    add_content_panel(
        s10,
        Inches(6.8), Inches(1.85), Inches(5.6), Inches(4.95),
        "Target Enterprise Roadmap",
        [
            "Phase 1: Multi-Airspace Streaming: Expanding continuous OpenSky polling across high-density transcontinental corridors.",
            "Phase 2: Weather & ATC Context Integration: Ingesting NEXRAD radar and terminal weather to suppress benign weather maneuvers.",
            "Phase 3: Real-Time Audio Transcription: Incorporating LiveATC communications with automatic named entity cross-referencing.",
            "Phase 4: Multi-Agency Federation: Secure export pipelines to FAA, NTSB, and airline Flight Operations Quality Assurance (FOQA).",
        ],
        tag="STRATEGIC ROADMAP",
        border_color=CYAN_NEON,
    )

    add_slide_footer(s10, 10)

    # Save to file
    out_file = Path("AeroIntel_10_Slides_Presentation.pptx").resolve()
    prs.save(str(out_file))
    print(f"Presentation saved successfully to: {out_file}")

    # Copy to alternate file
    alt_file = Path("AeroIntel_Project_Presentation.pptx").resolve()
    try:
        shutil.copyfile(str(out_file), str(alt_file))
        print(f"Also updated: {alt_file}")
    except Exception as e:
        print(f"Note: Could not copy to {alt_file.name}: {e}")


if __name__ == "__main__":
    build_deck()
