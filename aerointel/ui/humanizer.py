"""Humanizer & Plain-English translation engine for non-aviation users."""

from typing import Dict, Any, Tuple, Optional


# Everyday Aviation Glossary for Non-Specialists
AVIATION_GLOSSARY = {
    "Altitude (ft)": "How high the airplane is flying above sea level. Commercial jetliners usually cruise between 30,000 and 40,000 feet (about 6 to 7.5 miles high).",
    "FL (Flight Level)": "A shorthand pilots use for altitude above 18,000 feet. Add two zeros: FL240 means 24,000 feet; FL340 means 34,000 feet.",
    "Ground Speed (kt)": "Speed measured in nautical miles per hour (knots). 400 knots is roughly 460 mph (740 km/h) over the ground.",
    "Vertical Rate (fpm)": "Feet per minute: how fast the plane is climbing or descending. Normal cruising descent is 1,000 to 2,000 fpm. A drop over 3,000 fpm (~35 mph downward) feels like a very fast elevator.",
    "Heading (deg)": "Compass direction the airplane is pointed, from 0° (North) to 90° (East), 180° (South), and 270° (West).",
    "ADS-B Telemetry": "Automatic Dependent Surveillance-Broadcast: radio beacons planes broadcast every second showing position, altitude, and speed.",
    "Level Bust": "When an airplane flies slightly above or below the exact altitude Air Traffic Control assigned.",
    "ASRS": "Aviation Safety Reporting System: a confidential NASA/FAA database where pilots and controllers report unusual events voluntarily so everyone learns from them.",
    "NTSB": "National Transportation Safety Board: the federal agency that investigates major aviation incidents.",
    "PFD": "Primary Flight Display: the main computer screen directly in front of the pilot showing speed, altitude, and artificial horizon.",
    "ECAM / EICAS": "Cockpit warning screen that alerts pilots if engine temperatures or pressures go outside normal ranges.",
    "EGT": "Exhaust Gas Temperature: measure of how hot the jet engine exhaust is running.",
    "ARFF": "Airport Rescue and Fire Fighting: safety trucks that meet airplanes upon landing as a routine precaution.",
}


def knots_to_mph_str(kt: Optional[float]) -> str:
    """Convert knots to friendly mph and km/h explanation."""
    if kt is None:
        return "Unknown speed"
    mph = round(kt * 1.15078)
    kmh = round(kt * 1.852)
    return f"{kt:,.0f} knots (~{mph:,} mph / {kmh:,} km/h)"


def altitude_to_human_str(alt_ft: Optional[float]) -> str:
    """Explain altitude in relation to recognizable benchmarks."""
    if alt_ft is None:
        return "Unknown altitude"
    miles = round(alt_ft / 5280.0, 1)
    if alt_ft >= 28000:
        desc = f"Cruising altitude ({miles} miles up — higher than Mt. Everest)"
    elif alt_ft >= 10000:
        desc = f"Mid-altitude descent / climb ({miles} miles up)"
    elif alt_ft >= 3000:
        desc = "Low approach altitude near an airport"
    else:
        desc = "Very close to ground / airport pattern"
    return f"{alt_ft:,.0f} ft ({desc})"


def vrate_to_human_str(fpm: Optional[float]) -> str:
    """Convert feet per minute to human elevator comparison."""
    if fpm is None:
        return "Level flight"
    mph_vert = round(abs(fpm) * 0.0113636, 1)
    if abs(fpm) < 300:
        return "Level flight (holding steady altitude)"
    direction = "descending" if fpm < 0 else "climbing"
    intensity = "unusually steep" if abs(fpm) >= 3000 else ("moderate" if abs(fpm) >= 1500 else "gentle")
    return f"{abs(fpm):,.0f} ft/min {direction} ({intensity}, ~{mph_vert} mph vertically)"


def explain_anomaly_in_plain_english(alert_type_val: str, observed_val: Any, unit: str) -> Dict[str, str]:
    """Generate professional operational explanation and situational assessment."""
    alert_lower = str(alert_type_val).lower()

    if "low" in alert_lower and "speed" in alert_lower:
        val = float(observed_val) if observed_val is not None else 285.0
        mph = round(val * 1.15078)
        return {
            "title": "High-Speed Transit Below 10,000 ft",
            "what_happened": f"Aircraft recorded at {val:,.0f} knots (~{mph} mph) below 10,000 ft altitude.",
            "what_it_usually_means": "Aviation procedures generally recommend 250 knots below 10,000 ft for airport traffic management. ATC frequently clears departing or climbing flights for higher speeds once clear of surrounding traffic.",
            "what_to_look_for": "Verify if the aircraft was in an active climb corridor or received an ATC high-speed clearance.",
            "badge_color": "🟡 Speed Exceedance",
        }
    elif "altitude" in alert_lower:
        val = abs(float(observed_val)) if observed_val is not None else 3500.0
        mph_down = round(val * 0.0113636)
        return {
            "title": "Elevated Vertical Rate (Climb / Descent Exceedance)",
            "what_happened": f"Aircraft measured climbing or descending at {val:,.0f} ft/min (approx. {mph_down} mph vertically), exceeding the standard 2,500 fpm threshold.",
            "what_it_usually_means": "Most commonly an ATC instruction to reach an assigned altitude promptly, or a standard maneuver to bypass weather. Does not indicate an emergency or mechanical malfunction.",
            "what_to_look_for": "Check subsequent altitude stability to confirm safe level-off at assigned flight level.",
            "badge_color": "🟠 Notable Movement",
        }
    elif "speed" in alert_lower:
        val = abs(float(observed_val)) if observed_val is not None else 50.0
        return {
            "title": "Rapid Deceleration Detected",
            "what_happened": f"Aircraft airspeed decreased by {val:,.0f} knots (~{round(val*1.15)} mph) across consecutive observations.",
            "what_it_usually_means": "Flight crews regularly deploy flight spoilers (speed brakes) upon approach or encounter localized headwind shifts.",
            "what_to_look_for": "Confirm altitude maintenance and airspeed stabilization on approach.",
            "badge_color": "🟡 Deceleration",
        }
    elif "stale" in alert_lower or "gap" in alert_lower:
        val = float(observed_val) if observed_val is not None else 180.0
        mins = round(val / 60.0, 1)
        return {
            "title": "Transponder Signal Interval Exceeded",
            "what_happened": f"Ground ADS-B sensors recorded a {val:,.0f}-second (~{mins} min) interval between successive state vectors.",
            "what_it_usually_means": "Aircraft routinely transit through low-altitude terrain masking or peripheral coverage zones between terrestrial receiver stations.",
            "what_to_look_for": "Confirm downstream re-acquisition with intact altitude and track.",
            "badge_color": "⚪ Signal Gap",
        }
    else:
        return {
            "title": "Multivariate Statistical Outlier",
            "what_happened": "Unsupervised Isolation Forest flagged a joint telemetry distribution anomaly across altitude, airspeed, and climb rate.",
            "what_it_usually_means": "Represents an uncommon operational profile (e.g., steep climb coupled with turn maneuvers). Statistical outlier only; not evidence of an incident.",
            "what_to_look_for": "Review full geographic flight trajectory to assess operational context.",
            "badge_color": "🟣 Statistical Outlier",
        }


explain_anomaly_context = explain_anomaly_in_plain_english


def explain_incident_narrative_plain_english(category: str, summary: str) -> str:
    """Provide professional operational context for an incident classification."""
    cat_lower = category.lower()
    if "turbulence" in cat_lower:
        return "🌬️ **Operational Context:** In-flight atmospheric turbulence encountered. Airframe structural limits far exceed typical turbulence forces."
    elif "engine" in cat_lower:
        return "⚙️ **Operational Context:** Powerplant telemetry indicated parameters (vibration/oil) outside target range. Crew followed standard checklist procedures."
    elif "depressurization" in cat_lower:
        return "💨 **Operational Context:** Cabin pressure loss at altitude. Crew initiated standard immediate descent to breathable atmospheric levels (10,000 ft)."
    elif "runway" in cat_lower or "ground" in cat_lower:
        return "🛑 **Operational Context:** Surface movement irregularity during taxi. ATC maintained required runway separation buffers."
    elif "avionics" in cat_lower or "sensor" in cat_lower:
        return "🖥️ **Operational Context:** Flight instrument sensor divergence. Redundant backup avionics systems engaged per standard operating procedures."
    elif "altitude" in cat_lower:
        return "📏 **Operational Context:** Minor altitude deviation ('level bust') during transition, promptly resolved with ATC guidance."
    else:
        return "📋 **Operational Context:** Formal safety narrative documented for organizational review and hazard prevention."


explain_incident_narrative_context = explain_incident_narrative_plain_english
