"""Extractive source-grounded summarizer for aviation incident narratives."""

import re
from typing import List


# Domain keywords indicating salient operational facts
SALIENT_KEYWORDS = [
    "encountered", "observed", "excursion", "warning", "failure",
    "checklist", "diverted", "recovery", "autopilot", "altitude",
    "speed", "emergency", "urgency", "atc", "descent", "clearance",
    "level bust", "incursion", "discrepancy", "damage",
]


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences safely using punctuation boundaries."""
    if not text:
        return []
    # Split on periods/exclamations followed by space and capital letter, avoiding abbreviations like FL. or ft.
    raw_sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
    return [s.strip() for s in raw_sentences if s.strip()]


def summarize_narrative(narrative: str, max_sentences: int = 2) -> str:
    """Generate an extractive, source-grounded summary of an incident narrative.
    
    Principles:
    - Purely extractive: selects only sentences that exist in source text.
    - Zero hallucination: does not invent causes, injuries, or outcomes.
    - Highlights critical operational sentences (encounter, action, resolution).
    """
    if not narrative or not narrative.strip():
        return "No narrative text available to summarize."

    sentences = split_into_sentences(narrative)
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    scored_sentences = []
    for idx, sentence in enumerate(sentences):
        score = 0.0
        s_lower = sentence.lower()
        # Keyword density
        for kw in SALIENT_KEYWORDS:
            if kw in s_lower:
                score += 1.5

        # First and last sentences often contain context and outcome
        if idx == 0:
            score += 1.2
        elif idx == len(sentences) - 1:
            score += 0.8

        # Length penalty for extremely short or long sentences
        word_count = len(sentence.split())
        if 8 <= word_count <= 35:
            score += 0.5

        scored_sentences.append((score, idx, sentence))

    # Rank by score, select top N, and sort back by original narrative order
    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    top_n = scored_sentences[:max_sentences]
    top_n.sort(key=lambda x: x[1])

    summary_text = " ".join([s[2] for s in top_n])
    return summary_text
