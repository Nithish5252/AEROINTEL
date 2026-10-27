"""Incident narrative ingestion, normalization, and deduplication."""

import re
from typing import Tuple, List
import pandas as pd


def normalize_text(text: str) -> str:
    """Normalize text while preserving aviation terms, numbers, and flight levels."""
    if not isinstance(text, str):
        return ""
    # Collapse multiple whitespaces and trim
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned


def preprocess_incidents(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Clean, normalize, and deduplicate incident narrative records.
    
    Returns:
        (clean_df, list_of_warnings)
    """
    if df.empty:
        return df.copy(), ["Incident dataframe is empty."]

    warnings = []
    initial_len = len(df)
    clean_df = df.copy()

    # Drop missing report_id or narrative
    clean_df = clean_df.dropna(subset=["report_id", "narrative"])
    clean_df = clean_df[clean_df["narrative"].str.strip() != ""]

    # Normalize narrative text
    clean_df["clean_narrative"] = clean_df["narrative"].apply(normalize_text)

    # Deduplicate exact duplicate narratives
    dup_mask = clean_df.duplicated(subset=["clean_narrative"], keep="first")
    duplicates_count = dup_mask.sum()
    if duplicates_count > 0:
        clean_df = clean_df[~dup_mask].copy()
        warnings.append(f"Removed {duplicates_count} duplicate incident records based on narrative content.")

    dropped = initial_len - len(clean_df)
    if dropped > 0 and duplicates_count == 0:
        warnings.append(f"Filtered out {dropped} invalid incident records.")

    return clean_df.reset_index(drop=True), warnings
