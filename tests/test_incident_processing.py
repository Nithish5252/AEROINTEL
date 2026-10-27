"""Tests for incident NLP pipeline: normalization, search, summarization, and NER."""

import pandas as pd
import pytest

from aerointel.incidents.ingest import normalize_text, preprocess_incidents
from aerointel.incidents.search import search_incidents
from aerointel.incidents.summarize import summarize_narrative, split_into_sentences
from aerointel.incidents.entities import extract_entities
from aerointel.incidents.classify import IncidentClassifier


def test_normalize_text():
    raw = "   Flight encountered    severe turbulence at   FL340.   "
    cleaned = normalize_text(raw)
    assert cleaned == "Flight encountered severe turbulence at FL340."


def test_preprocess_incidents_deduplication():
    df = pd.DataFrame([
        {"report_id": "R1", "narrative": "Aircraft experienced engine vibration."},
        {"report_id": "R2", "narrative": "Aircraft experienced engine vibration."},  # exact duplicate
        {"report_id": "R3", "narrative": ""},  # empty narrative
        {"report_id": "R4", "narrative": "Runway incursion reported at Boston Logan."},
    ])
    clean_df, warnings = preprocess_incidents(df)
    assert len(clean_df) == 2
    assert set(clean_df["report_id"]) == {"R1", "R4"}


def test_search_incidents():
    df = pd.DataFrame([
        {"report_id": "R1", "category": "Turbulence", "location": "BOS", "narrative": "Clear air turbulence at FL240."},
        {"report_id": "R2", "category": "Engine Anomaly", "location": "JFK", "narrative": "Oil pressure drop on engine 1."},
        {"report_id": "R3", "category": "Turbulence", "location": "EWR", "narrative": "Moderate turbulence encountered."},
    ])

    # Search keyword
    res_kw = search_incidents(df, query="turbulence")
    assert len(res_kw) == 2

    # Category filter
    res_cat = search_incidents(df, category="Engine Anomaly")
    assert len(res_cat) == 1
    assert res_cat.iloc[0]["report_id"] == "R2"

    # Multi-criteria
    res_multi = search_incidents(df, query="turbulence", category="Turbulence", location_query="BOS")
    assert len(res_multi) == 1
    assert res_multi.iloc[0]["report_id"] == "R1"


def test_extractive_summarizer_source_grounded():
    narrative = (
        "While descending through FL240 approximately 45 miles southwest of Boston Logan, "
        "flight crew encountered unexpected moderate to severe clear air turbulence. "
        "Autopilot momentarily disconnected following a rapid altitude excursion of 800 feet. "
        "Crew initiated manual recovery, leveled off at FL230, and coordinated with Boston Center. "
        "Seatbelt signs were illuminated prior to encounter; no injuries were reported."
    )
    summary = summarize_narrative(narrative, max_sentences=2)
    sentences = split_into_sentences(narrative)

    # Every sentence in the summary must exist word-for-word in the original text (0% hallucination)
    summary_sentences = split_into_sentences(summary)
    assert len(summary_sentences) <= 2
    for s in summary_sentences:
        assert s in narrative


def test_entity_extraction_regex():
    text = "Boeing 737-800 departed JFK climbing to FL340, encountered moderate turbulence near waypoint EXERT. PFD indicated airspeed disagree."
    entities = extract_entities(text)

    assert "Boeing 737-800" in entities["AIRCRAFT"]
    assert "JFK" in entities["LOCATION_AIRPORT"]
    assert "FL340" in entities["ALTITUDE"]
    assert "waypoint EXERT" in entities["RUNWAY_WAYPOINT"]
    assert "PFD" in entities["SYSTEM_COMPONENT"]
    assert "moderate turbulence" in entities["WEATHER"]


def test_baseline_classifier_training_and_prediction():
    df = pd.DataFrame([
        {"narrative": "Clear air turbulence at FL340 causing altitude excursion.", "category": "Turbulence"},
        {"narrative": "Severe turbulence encountered over mountains.", "category": "Turbulence"},
        {"narrative": "Engine vibration and high EGT warning on engine 2.", "category": "Engine"},
        {"narrative": "Oil pressure drop on engine 1 during climb out.", "category": "Engine"},
        {"narrative": "Runway incursion crossing hold short line without clearance.", "category": "Ground"},
        {"narrative": "Aircraft crossed active runway causing go-around.", "category": "Ground"},
    ])
    clf = IncidentClassifier()
    metrics = clf.train(df)

    assert metrics["is_trained"] is True
    assert metrics["sample_count"] == 6
    assert metrics["category_count"] == 3

    # Prediction test
    pred_cat, conf = clf.predict("High engine vibration and oil warning on climb.")
    assert pred_cat == "Engine"
    assert conf is not None and conf > 0.0
