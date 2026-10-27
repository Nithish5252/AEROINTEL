"""Search and multi-criteria filtering for incident narratives."""

from datetime import datetime
from typing import Optional, List
import pandas as pd


def search_incidents(
    df: pd.DataFrame,
    query: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    location_query: Optional[str] = None,
) -> pd.DataFrame:
    """Filter incident records by keyword search, category, and date bounds.
    
    Safe search: handles case-insensitivity, regex safety, and missing metadata.
    """
    if df.empty:
        return df.copy()

    filtered = df.copy()

    # 1. Category Filter
    if category and category != "All Categories":
        if "category" in filtered.columns:
            filtered = filtered[filtered["category"].str.lower() == category.lower()]

    # 2. Location Filter
    if location_query and location_query.strip():
        if "location" in filtered.columns:
            loc_term = location_query.strip().lower()
            filtered = filtered[filtered["location"].fillna("").str.lower().str.contains(loc_term, regex=False)]

    # 3. Date Filters
    if "event_date" in filtered.columns:
        # Ensure event_date is datetime
        if not pd.api.types.is_datetime64_any_dtype(filtered["event_date"]):
            filtered["event_date"] = pd.to_datetime(filtered["event_date"], errors="coerce")

        if start_date is not None:
            filtered = filtered[filtered["event_date"] >= pd.to_datetime(start_date)]
        if end_date is not None:
            filtered = filtered[filtered["event_date"] <= pd.to_datetime(end_date)]

    # 4. Keyword Query Search
    if query and query.strip():
        terms = [t.strip().lower() for t in query.split() if t.strip()]
        if terms:
            def matches_all_terms(row: pd.Series) -> bool:
                combined_text = " ".join([
                    str(row.get("narrative", "")),
                    str(row.get("category", "")),
                    str(row.get("location", "")),
                    str(row.get("aircraft_type", "")),
                ]).lower()
                return all(t in combined_text for t in terms)

            filtered = filtered[filtered.apply(matches_all_terms, axis=1)]

    return filtered.reset_index(drop=True)
