"""Data loading utilities with caching for Streamlit."""

import os
from pathlib import Path
from typing import Optional, Tuple, List

import pandas as pd
import streamlit as st


def get_data_path() -> Path:
    """Get the path to the processed data file."""
    # Check multiple possible locations
    possible_paths = [
        Path(__file__).parent.parent / "data" / "processed" / "gtd_processed.parquet",
        Path("data/processed/gtd_processed.parquet"),
        Path("/Users/paulstrootman/Desktop/Global Terrorism/data/processed/gtd_processed.parquet")
    ]

    for path in possible_paths:
        if path.exists():
            return path

    raise FileNotFoundError(
        "GTD processed data not found. Please run: python scripts/preprocess_data.py"
    )


@st.cache_data(ttl=3600)
def load_gtd_data() -> pd.DataFrame:
    """
    Load the preprocessed GTD data with caching.

    Returns:
        pd.DataFrame: The preprocessed GTD dataframe
    """
    data_path = get_data_path()

    df = pd.read_parquet(data_path)

    # Ensure datetime column is proper datetime type
    if 'event_date' in df.columns:
        df['event_date'] = pd.to_datetime(df['event_date'])

    # Convert categorical columns back to category type for efficiency
    categorical_cols = ['country_txt', 'region_txt', 'attacktype1_txt',
                        'targtype1_txt', 'weaptype1_txt']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype('category')

    return df


def get_filtered_data(
    df: pd.DataFrame,
    year_range: Optional[Tuple[int, int]] = None,
    regions: Optional[List[str]] = None,
    attack_types: Optional[List[str]] = None,
    target_types: Optional[List[str]] = None,
    min_casualties: int = 0,
    success_only: bool = False
) -> pd.DataFrame:
    """
    Filter the GTD data based on various criteria.

    Args:
        df: The source dataframe
        year_range: Tuple of (start_year, end_year)
        regions: List of region names to include
        attack_types: List of attack types to include
        target_types: List of target types to include
        min_casualties: Minimum total casualties threshold
        success_only: Whether to include only successful attacks

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    filtered = df.copy()

    # Year range filter
    if year_range is not None:
        filtered = filtered[
            (filtered['iyear'] >= year_range[0]) &
            (filtered['iyear'] <= year_range[1])
        ]

    # Region filter
    if regions is not None and len(regions) > 0:
        filtered = filtered[filtered['region_txt'].isin(regions)]

    # Attack type filter
    if attack_types is not None and len(attack_types) > 0:
        filtered = filtered[filtered['attacktype1_txt'].isin(attack_types)]

    # Target type filter
    if target_types is not None and len(target_types) > 0:
        filtered = filtered[filtered['targtype1_txt'].isin(target_types)]

    # Casualty threshold
    if min_casualties > 0 and 'total_casualties' in filtered.columns:
        filtered = filtered[filtered['total_casualties'] >= min_casualties]

    # Success filter
    if success_only and 'success' in filtered.columns:
        filtered = filtered[filtered['success'] == 1]

    return filtered


def get_unique_values(df: pd.DataFrame, column: str) -> List[str]:
    """Get sorted unique values for a column."""
    if column not in df.columns:
        return []
    return sorted(df[column].dropna().unique().tolist())


def get_year_range(df: pd.DataFrame) -> Tuple[int, int]:
    """Get the min and max years in the dataset."""
    if 'iyear' not in df.columns:
        return (1970, 2020)
    return (int(df['iyear'].min()), int(df['iyear'].max()))


def get_summary_stats(df: pd.DataFrame) -> dict:
    """
    Calculate summary statistics for the dashboard.

    Returns:
        dict with keys: total_incidents, total_killed, total_wounded,
                       countries_affected, active_groups
    """
    stats = {
        'total_incidents': len(df),
        'total_killed': int(df['nkill'].sum()) if 'nkill' in df.columns else 0,
        'total_wounded': int(df['nwound'].sum()) if 'nwound' in df.columns else 0,
        'countries_affected': df['country_txt'].nunique() if 'country_txt' in df.columns else 0,
        'active_groups': df['gname'].nunique() if 'gname' in df.columns else 0
    }
    return stats
