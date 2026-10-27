"""Named Entity Recognition (NER) for aviation narratives with robust regex fallback."""

import re
from typing import Dict, List, Set


# Core Aviation Dictionary Patterns
AIRCRAFT_PATTERNS = [
    r"\b(?:Boeing|B)\s*(?:7[0-9]{2}(?:-[0-9]{3}|MAX\s*[0-9]+)?)\b",
    r"\b(?:Airbus|A)\s*(?:3[0-9]{2}(?:neo)?)\b",
    r"\b(?:Embraer|E)\s*(?:1[79][05])\b",
    r"\b(?:Bombardier|CRJ)\s*(?:-[0-9]{3}|[0-9]{3})\b",
    r"\b(?:Gulfstream|G)\s*(?:[0-9]{3}|[IVX]+)\b",
    r"\bCessna(?:\s+Citation)?\b",
]

AIRPORT_AND_LOCATIONS = [
    r"\b(?:Boston Logan|BOS|Logan Intl)\b",
    r"\b(?:JFK|John F\. Kennedy|New York JFK)\b",
    r"\b(?:EWR|Newark|Newark Liberty)\b",
    r"\b(?:LGA|LaGuardia)\b",
    r"\b(?:PHL|Philadelphia Intl)\b",
    r"\b(?:BDL|Bradley Intl)\b",
    r"\b(?:HPN|White Plains)\b",
    r"\b(?:PVD|Providence)\b",
]

ALTITUDE_PATTERNS = [
    r"\bFL\s*[0-9]{2,3}\b",
    r"\b[0-9]{1,2},[0-9]{3}\s*(?:feet|ft)(?:\s*(?:MSL|AGL))?\b",
    r"\b[0-9]{3,4}\s*(?:feet|ft)(?:\s*(?:MSL|AGL))?\b",
]

RUNWAY_WAYPOINT_PATTERNS = [
    r"\bRunway\s+[0-9]{1,2}[LRC]?\b",
    r"\bTaxiway\s+[A-Z](?:[0-9]+)?\b",
    r"\bwaypoint\s+[A-Z]{3,5}\b",
    r"\bfix\s+[A-Z]{3,5}\b",
]

SYSTEMS_COMPONENTS = [
    r"\bautopilot\b",
    r"\bautothrottle\b",
    r"\bpitot[- ]probe\b",
    r"\bpitot[- ]static\b",
    r"\bPFD\b",
    r"\bECAM\b",
    r"\bFMS\b",
    r"\bEGT\b",
    r"\bN1 vibration\b",
    r"\bWAAS\b",
    r"\bILS\b",
    r"\bVOR\b",
]

WEATHER_TERMS = [
    r"\b(?:clear air turbulence|CAT)\b",
    r"\b(?:moderate|severe)\s+turbulence\b",
    r"\bIMC\b",
    r"\btailwind\b",
    r"\breduced visibility\b",
    r"\bconvective activity\b",
]


def extract_entities_regex(narrative: str) -> Dict[str, List[str]]:
    """Extract domain entities from aviation narrative using curated regular expressions.
    
    Guarantees reliable entity extraction without requiring external spaCy model downloads.
    """
    if not narrative:
        return {}

    def match_patterns(patterns: List[str], text: str) -> List[str]:
        found: Set[str] = set()
        for pat in patterns:
            for match in re.finditer(pat, text, re.IGNORECASE):
                found.add(match.group(0).strip())
        return sorted(list(found))

    return {
        "AIRCRAFT": match_patterns(AIRCRAFT_PATTERNS, narrative),
        "LOCATION_AIRPORT": match_patterns(AIRPORT_AND_LOCATIONS, narrative),
        "ALTITUDE": match_patterns(ALTITUDE_PATTERNS, narrative),
        "RUNWAY_WAYPOINT": match_patterns(RUNWAY_WAYPOINT_PATTERNS, narrative),
        "SYSTEM_COMPONENT": match_patterns(SYSTEMS_COMPONENTS, narrative),
        "WEATHER": match_patterns(WEATHER_TERMS, narrative),
    }


def extract_entities(narrative: str) -> Dict[str, List[str]]:
    """Primary entity extraction entry point with graceful fallback."""
    # We use regex as the robust, non-blocking primary extractor
    return extract_entities_regex(narrative)
