"""Synthetic demo dataset generator for flight telemetry and incident narratives."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd


def generate_demo_flights() -> pd.DataFrame:
    """Generate high-fidelity, clearly marked synthetic aircraft telemetry.
    
    Includes realistic trajectories, normal cruising flights, and deliberately
    injected anomalies for detector verification.
    """
    records: List[Dict[str, Any]] = []
    base_time = datetime(2026, 10, 26, 14, 0, 0, tzinfo=timezone.utc)

    # 1. Aircraft SYN-FLT-402: Normal En-Route Cruise (Control / Baseline)
    lat, lon = 40.6413, -73.7781  # JFK area heading northeast
    alt = 33000.0
    spd = 450.0
    hdg = 45.0
    for i in range(25):
        t = base_time + timedelta(seconds=i * 15)
        lat += 0.015
        lon += 0.018
        alt += (i % 3 - 1) * 20  # slight +/- 20 ft normal jitter
        spd += (i % 2 - 0.5) * 2  # slight +/- 1 kt jitter
        records.append({
            "aircraft_id": "SYN-FLT-402",
            "timestamp": t.isoformat(),
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "altitude_ft": round(alt, 1),
            "ground_speed_kt": round(spd, 1),
            "heading_deg": round(hdg, 1),
            "vertical_rate_fpm": 0.0,
            "source": "AeroIntel Synthetic Demo Generator",
            "is_synthetic": True,
        })

    # 2. Aircraft SYN-FLT-101: Injected Rapid Altitude Change (Descent > 3500 fpm)
    lat, lon = 41.2000, -72.9000
    alt = 31000.0
    spd = 430.0
    hdg = 90.0
    for i in range(20):
        t = base_time + timedelta(seconds=i * 15)
        lat += 0.012
        lon += 0.020
        vrate = 0.0
        if 8 <= i <= 12:
            # Rapid descent anomaly: 900 ft drop per 15s = 3600 fpm
            alt -= 950.0
            vrate = -3800.0
        elif i > 12:
            vrate = -500.0
            alt -= 125.0
        records.append({
            "aircraft_id": "SYN-FLT-101",
            "timestamp": t.isoformat(),
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "altitude_ft": round(alt, 1),
            "ground_speed_kt": round(spd, 1),
            "heading_deg": round(hdg, 1),
            "vertical_rate_fpm": round(vrate, 1),
            "source": "AeroIntel Synthetic Demo Generator",
            "is_synthetic": True,
        })

    # 3. Aircraft SYN-FLT-204: Injected Abrupt Speed Drop (Deceleration > 50 kt)
    lat, lon = 42.3601, -71.0589  # Boston area
    alt = 18000.0
    spd = 360.0
    hdg = 210.0
    for i in range(20):
        t = base_time + timedelta(seconds=i * 15)
        lat -= 0.014
        lon -= 0.010
        if 7 <= i <= 10:
            spd -= 20.0  # Drops 60 knots over 30s
        records.append({
            "aircraft_id": "SYN-FLT-204",
            "timestamp": t.isoformat(),
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "altitude_ft": round(alt, 1),
            "ground_speed_kt": round(spd, 1),
            "heading_deg": round(hdg, 1),
            "vertical_rate_fpm": -200.0,
            "source": "AeroIntel Synthetic Demo Generator",
            "is_synthetic": True,
        })

    # 4. Aircraft SYN-FLT-309: Injected Stale Telemetry Gap (320s loss of signal)
    lat, lon = 40.0000, -74.5000
    alt = 24000.0
    spd = 400.0
    hdg = 180.0
    for i in range(12):
        if i < 6:
            t = base_time + timedelta(seconds=i * 15)
        else:
            # 320 second time gap at observation 6
            t = base_time + timedelta(seconds=(5 * 15) + 320 + (i - 6) * 15)
        lat -= 0.015
        lon += 0.002
        records.append({
            "aircraft_id": "SYN-FLT-309",
            "timestamp": t.isoformat(),
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "altitude_ft": round(alt, 1),
            "ground_speed_kt": round(spd, 1),
            "heading_deg": round(hdg, 1),
            "vertical_rate_fpm": 0.0,
            "source": "AeroIntel Synthetic Demo Generator",
            "is_synthetic": True,
        })

    # 5. Aircraft SYN-FLT-505: Injected Complex Multimodal Outlier (for Isolation Forest)
    lat, lon = 41.5000, -73.5000
    alt = 28000.0
    spd = 410.0
    hdg = 300.0
    for i in range(20):
        t = base_time + timedelta(seconds=i * 15)
        lat += 0.010
        lon -= 0.016
        if 9 <= i <= 13:
            alt -= 1100.0  # steep descent: 4400 fpm
            spd -= 18.0   # simultaneous rapid deceleration
            hdg = (hdg + 35.0) % 360.0
        records.append({
            "aircraft_id": "SYN-FLT-505",
            "timestamp": t.isoformat(),
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "altitude_ft": round(alt, 1),
            "ground_speed_kt": round(spd, 1),
            "heading_deg": round(hdg, 1),
            "vertical_rate_fpm": -4400.0 if (9 <= i <= 13) else 0.0,
            "source": "AeroIntel Synthetic Demo Generator",
            "is_synthetic": True,
        })

    # 6. Aircraft AIC-FLT-101 (Air India Demo): Delhi FIR (Rapid descent demo)
    lat, lon = 28.556, 77.100
    alt = 32000.0
    spd = 440.0
    hdg = 145.0
    for i in range(20):
        t = base_time + timedelta(seconds=i * 15)
        lat += 0.012
        lon += 0.015
        vrate = 0.0
        if 8 <= i <= 12:
            alt -= 950.0
            vrate = -3800.0
        elif i > 12:
            alt -= 150.0
            vrate = -600.0
        records.append({
            "aircraft_id": "AIC-FLT-101",
            "timestamp": t.isoformat(),
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "altitude_ft": round(alt, 1),
            "ground_speed_kt": round(spd, 1),
            "heading_deg": round(hdg, 1),
            "vertical_rate_fpm": round(vrate, 1),
            "source": "AeroIntel Synthetic Demo Generator (Indian Airspace)",
            "is_synthetic": True,
        })

    # 7. Aircraft IGO-FLT-204 (IndiGo Demo): Mumbai TMA (Abrupt speed drop demo)
    lat, lon = 19.089, 72.865
    alt = 22000.0
    spd = 390.0
    hdg = 60.0
    for i in range(20):
        t = base_time + timedelta(seconds=i * 15)
        lat += 0.010
        lon += 0.014
        if 7 <= i <= 10:
            spd -= 25.0
        records.append({
            "aircraft_id": "IGO-FLT-204",
            "timestamp": t.isoformat(),
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "altitude_ft": round(alt, 1),
            "ground_speed_kt": round(spd, 1),
            "heading_deg": round(hdg, 1),
            "vertical_rate_fpm": -250.0,
            "source": "AeroIntel Synthetic Demo Generator (Indian Airspace)",
            "is_synthetic": True,
        })

    # 8. Aircraft SEJ-FLT-309 (SpiceJet Demo): Central India / Nagpur (Telemetry gap demo)
    lat, lon = 21.150, 79.090
    alt = 35000.0
    spd = 460.0
    hdg = 180.0
    for i in range(12):
        if i < 6:
            t = base_time + timedelta(seconds=i * 15)
        else:
            t = base_time + timedelta(seconds=(5 * 15) + 320 + (i - 6) * 15)
        lat -= 0.014
        lon += 0.005
        records.append({
            "aircraft_id": "SEJ-FLT-309",
            "timestamp": t.isoformat(),
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "altitude_ft": round(alt, 1),
            "ground_speed_kt": round(spd, 1),
            "heading_deg": round(hdg, 1),
            "vertical_rate_fpm": 0.0,
            "source": "AeroIntel Synthetic Demo Generator (Indian Airspace)",
            "is_synthetic": True,
        })

    # 9. Aircraft VTI-FLT-402 (Vistara Demo): Bengaluru TMA (Smooth cruise baseline)
    lat, lon = 13.198, 77.706
    alt = 36000.0
    spd = 455.0
    hdg = 350.0
    for i in range(25):
        t = base_time + timedelta(seconds=i * 15)
        lat += 0.015
        lon -= 0.005
        alt += (i % 3 - 1) * 20
        spd += (i % 2 - 0.5) * 2
        records.append({
            "aircraft_id": "VTI-FLT-402",
            "timestamp": t.isoformat(),
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "altitude_ft": round(alt, 1),
            "ground_speed_kt": round(spd, 1),
            "heading_deg": round(hdg, 1),
            "vertical_rate_fpm": 0.0,
            "source": "AeroIntel Synthetic Demo Generator (Indian Airspace)",
            "is_synthetic": True,
        })

    return pd.DataFrame(records)


def generate_demo_incidents() -> pd.DataFrame:
    """Generate clearly marked fictional aviation safety incident narratives.
    
    Includes diverse categories, structured narratives, realistic aviation vocabulary,
    and metadata for search, NER, summarization, and baseline classification.
    """
    incidents = [
        {
            "report_id": "INC-2026-001",
            "event_date": "2026-10-24 16:30:00",
            "location": "Boston Logan Intl (BOS)",
            "aircraft_type": "Boeing 737-800",
            "category": "Turbulence / Weather Encounter",
            "narrative": (
                "While descending through FL240 approximately 45 miles southwest of Boston Logan, "
                "flight crew encountered unexpected moderate to severe clear air turbulence. "
                "Autopilot momentarily disconnected following a rapid altitude excursion of 800 feet. "
                "Crew initiated manual recovery, leveled off at FL230, and coordinated with Boston Center. "
                "Seatbelt signs were illuminated prior to encounter; no injuries were reported. "
                "Post-flight inspection revealed no structural damage to the airframe."
            ),
            "source_name": "AeroIntel Synthetic Safety Archive",
            "source_url": "",
            "is_synthetic": True,
        },
        {
            "report_id": "INC-2026-002",
            "event_date": "2026-10-25 09:15:00",
            "location": "JFK Intl (JFK)",
            "aircraft_type": "Airbus A321neo",
            "category": "Engine & Propulsion Anomaly",
            "narrative": (
                "During initial climb out out of Runway 22R passing 3,500 feet MSL, flight crew "
                "observed fluctuating EGT (Exhaust Gas Temperature) and abnormal N1 vibration on engine number 1. "
                "Crew executed the uncommanded engine vibration quick reference checklist, reduced power on engine 1, "
                "and declared an urgency condition with New York Departure. Radar vectors were provided for an "
                "uneventful single-engine overweight landing back on Runway 22L. Airport rescue and firefighting (ARFF) "
                "met the aircraft as a standard precaution."
            ),
            "source_name": "AeroIntel Synthetic Safety Archive",
            "source_url": "",
            "is_synthetic": True,
        },
        {
            "report_id": "INC-2026-003",
            "event_date": "2026-10-25 14:40:00",
            "location": "Newark Liberty Intl (EWR)",
            "aircraft_type": "Boeing 777-200ER",
            "category": "Cabin Depressurization Event",
            "narrative": (
                "En route at FL340, cabin altitude warning horn sounded with cabin rate of climb indicating "
                "1,500 feet per minute. Flight crew immediately donned oxygen masks and initiated an expedited "
                "emergency descent to 10,000 feet in accordance with SOP. Telemetry recorded a rapid descent rate "
                "exceeding 4,000 fpm during the initial descent phase. ATC cleared the flight direct to a lower sector. "
                "Passenger oxygen masks deployed automatically. The flight diverted safely to Newark without further incident."
            ),
            "source_name": "AeroIntel Synthetic Safety Archive",
            "source_url": "",
            "is_synthetic": True,
        },
        {
            "report_id": "INC-2026-004",
            "event_date": "2026-10-25 18:20:00",
            "location": "LaGuardia Airport (LGA)",
            "aircraft_type": "Embraer E175",
            "category": "Runway Incursion / Ground Conflict",
            "narrative": (
                "While taxiing via Taxiway Bravo toward Runway 04, aircraft crossed the hold short line of "
                "Runway 31 without explicit air traffic control clearance. Ground controller observed the conflict "
                "and immediately instructed an approaching Cessna Citation on final approach to execute an immediate go-around. "
                "Minimum separation was maintained at 1.4 miles. Ground crew reported momentary confusion due to "
                "ongoing construction signage and reduced visibility in low dusk lighting."
            ),
            "source_name": "AeroIntel Synthetic Safety Archive",
            "source_url": "",
            "is_synthetic": True,
        },
        {
            "report_id": "INC-2026-005",
            "event_date": "2026-10-26 08:05:00",
            "location": "Philadelphia Intl (PHL)",
            "aircraft_type": "Bombardier CRJ-900",
            "category": "Avionics & Sensor Failure",
            "narrative": (
                "Shortly after reaching cruise altitude at FL280, primary flight display (PFD) showed an erroneous "
                "airspeed disagree and pitot-static mismatch warning. Autothrottle disconnected automatically. "
                "Flight crew recognized unreliable airspeed indications, referred to memory items for pitch and power settings, "
                "and notified ATC of degraded navigation capabilities. After cross-checking standby instruments, "
                "crew confirmed pitot probe heat failure. Flight proceeded to destination at reduced cruise speed without incident."
            ),
            "source_name": "AeroIntel Synthetic Safety Archive",
            "source_url": "",
            "is_synthetic": True,
        },
        {
            "report_id": "INC-2026-006",
            "event_date": "2026-10-26 11:50:00",
            "location": "Bradley Intl (BDL)",
            "aircraft_type": "Boeing 737 MAX 8",
            "category": "Altitude Deviation / Level Bust",
            "narrative": (
                "During descent into Bradley International, ATC instructed flight crew to cross waypoint EXERT "
                "at or above 11,000 feet. Due to a late descent clearance in tailwind conditions and FMS vertical "
                "navigation path capture lag, the aircraft crossed the fix at 9,800 feet, resulting in a 1,200-foot level bust. "
                "Controller issued corrective altitude adjustment to maintain separation with departing traffic. "
                "Both crew members acknowledged the vertical deviation and submitted an internal safety report."
            ),
            "source_name": "AeroIntel Synthetic Safety Archive",
            "source_url": "",
            "is_synthetic": True,
        },
        {
            "report_id": "INC-2026-007",
            "event_date": "2026-10-26 13:10:00",
            "location": "White Plains (HPN)",
            "aircraft_type": "Gulfstream G650",
            "category": "Avionics & Sensor Failure",
            "narrative": (
                "During instrument approach to Runway 16 in IMC conditions, flight crew reported dual flight director "
                "discrepancy and momentary loss of GPS WAAS signal. Crew aborted the approach at 800 feet AGL and performed "
                "a standard missed approach. After resetting the avionics bus and confirming VOR backup reception, "
                "the aircraft landed safely via ILS approach."
            ),
            "source_name": "AeroIntel Synthetic Safety Archive",
            "source_url": "",
            "is_synthetic": True,
        },
        {
            "report_id": "INC-2026-008",
            "event_date": "2026-10-26 14:15:00",
            "location": "Providence (PVD)",
            "aircraft_type": "Airbus A320",
            "category": "Engine & Propulsion Anomaly",
            "narrative": (
                "On initial climb through 8,000 feet, pilots detected an oil pressure drop on engine 2 accompanied "
                "by an ECAM warning. Thrust was reduced to flight idle while completing abnormal checklists. Crew decided "
                "to return to the departure airport as a precautionary measure. Flight landed uneventfully."
            ),
            "source_name": "AeroIntel Synthetic Safety Archive",
            "source_url": "",
            "is_synthetic": True,
        },
    ]
    return pd.DataFrame(incidents)


def ensure_demo_datasets(data_dir: Path) -> None:
    """Ensure that demo_flights.csv and demo_incidents.csv exist on disk."""
    data_dir.mkdir(parents=True, exist_ok=True)
    flights_path = data_dir / "demo_flights.csv"
    incidents_path = data_dir / "demo_incidents.csv"

    if not flights_path.exists():
        df_flights = generate_demo_flights()
        df_flights.to_csv(flights_path, index=False)

    if not incidents_path.exists():
        df_incidents = generate_demo_incidents()
        df_incidents.to_csv(incidents_path, index=False)
