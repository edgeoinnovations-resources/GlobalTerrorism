#!/usr/bin/env python3
"""
GTD Data Preprocessing Script

Loads the Global Terrorism Database Excel file, cleans the data,
and exports to GeoParquet format for efficient loading in visualizations.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_gtd_data(filepath: str) -> pd.DataFrame:
    """Load GTD Excel file with progress indication."""
    print(f"Loading GTD data from: {filepath}")
    print("This may take a few minutes for large files...")

    # Read Excel file
    df = pd.read_excel(
        filepath,
        engine='openpyxl',
        dtype={
            'eventid': 'int64',
            'iyear': 'int16',
            'imonth': 'int8',
            'iday': 'int8',
            'success': 'int8'
        }
    )

    print(f"Loaded {len(df):,} rows and {len(df.columns)} columns")
    return df


def clean_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with missing or invalid coordinates."""
    initial_count = len(df)

    # Remove rows with missing lat/long
    df = df.dropna(subset=['latitude', 'longitude'])

    # Remove "Null Island" (0,0 coordinates)
    df = df[~((df['latitude'] == 0) & (df['longitude'] == 0))]

    # Remove invalid coordinates
    df = df[(df['latitude'] >= -90) & (df['latitude'] <= 90)]
    df = df[(df['longitude'] >= -180) & (df['longitude'] <= 180)]

    removed = initial_count - len(df)
    print(f"Removed {removed:,} rows with invalid/missing coordinates")
    print(f"Remaining rows: {len(df):,}")

    return df


def create_datetime_column(df: pd.DataFrame) -> pd.DataFrame:
    """Create proper datetime column from iyear, imonth, iday."""
    # Replace 0 values with 1 for unknown month/day
    df['imonth'] = df['imonth'].replace(0, 1)
    df['iday'] = df['iday'].replace(0, 1)

    # Handle invalid day values (e.g., day > 28 for February)
    def safe_date(row):
        try:
            return datetime(int(row['iyear']), int(row['imonth']), int(row['iday']))
        except ValueError:
            # If day is invalid, use first of month
            try:
                return datetime(int(row['iyear']), int(row['imonth']), 1)
            except ValueError:
                # If month is also invalid, use first of year
                return datetime(int(row['iyear']), 1, 1)

    print("Creating datetime column...")
    df['event_date'] = df.apply(safe_date, axis=1)

    return df


def select_essential_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Select only columns needed for visualization."""
    essential_columns = [
        'eventid',
        'iyear',
        'imonth',
        'iday',
        'event_date',
        'country_txt',
        'region_txt',
        'city',
        'latitude',
        'longitude',
        'attacktype1_txt',
        'targtype1_txt',
        'gname',
        'nkill',
        'nwound',
        'success',
        'weaptype1_txt',
        'summary'
    ]

    # Only select columns that exist in the dataframe
    available_columns = [col for col in essential_columns if col in df.columns]
    missing_columns = [col for col in essential_columns if col not in df.columns]

    if missing_columns:
        print(f"Warning: Missing columns: {missing_columns}")

    df = df[available_columns].copy()
    print(f"Selected {len(available_columns)} essential columns")

    return df


def fill_missing_casualties(df: pd.DataFrame) -> pd.DataFrame:
    """Fill NaN values in casualty columns with 0."""
    if 'nkill' in df.columns:
        df['nkill'] = df['nkill'].fillna(0).astype('float32')
    if 'nwound' in df.columns:
        df['nwound'] = df['nwound'].fillna(0).astype('float32')

    # Create total casualties column
    if 'nkill' in df.columns and 'nwound' in df.columns:
        df['total_casualties'] = df['nkill'] + df['nwound']

    return df


def generate_quality_report(df: pd.DataFrame, output_path: str) -> None:
    """Generate a data quality report."""
    report = []
    report.append("=" * 60)
    report.append("GTD DATA QUALITY REPORT")
    report.append("=" * 60)
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\nTotal Records: {len(df):,}")

    # Temporal distribution
    report.append("\n" + "-" * 40)
    report.append("TEMPORAL DISTRIBUTION")
    report.append("-" * 40)
    if 'iyear' in df.columns:
        report.append(f"Year Range: {df['iyear'].min()} - {df['iyear'].max()}")
        yearly_counts = df['iyear'].value_counts().sort_index()
        report.append(f"Years with data: {len(yearly_counts)}")
        report.append(f"Average incidents per year: {len(df) / len(yearly_counts):.0f}")

    # Geographic coverage
    report.append("\n" + "-" * 40)
    report.append("GEOGRAPHIC COVERAGE")
    report.append("-" * 40)
    if 'country_txt' in df.columns:
        report.append(f"Countries: {df['country_txt'].nunique()}")
    if 'region_txt' in df.columns:
        report.append(f"Regions: {df['region_txt'].nunique()}")
        report.append("\nIncidents by Region:")
        for region, count in df['region_txt'].value_counts().head(12).items():
            report.append(f"  {region}: {count:,}")

    # Attack types
    report.append("\n" + "-" * 40)
    report.append("ATTACK TYPES")
    report.append("-" * 40)
    if 'attacktype1_txt' in df.columns:
        report.append(f"Attack Types: {df['attacktype1_txt'].nunique()}")
        for attack, count in df['attacktype1_txt'].value_counts().items():
            report.append(f"  {attack}: {count:,}")

    # Casualty statistics
    report.append("\n" + "-" * 40)
    report.append("CASUALTY STATISTICS")
    report.append("-" * 40)
    if 'nkill' in df.columns:
        report.append(f"Total Killed: {df['nkill'].sum():,.0f}")
        report.append(f"Average per incident: {df['nkill'].mean():.2f}")
        report.append(f"Max in single incident: {df['nkill'].max():,.0f}")
    if 'nwound' in df.columns:
        report.append(f"Total Wounded: {df['nwound'].sum():,.0f}")
        report.append(f"Average per incident: {df['nwound'].mean():.2f}")

    # Perpetrator groups
    report.append("\n" + "-" * 40)
    report.append("TOP PERPETRATOR GROUPS")
    report.append("-" * 40)
    if 'gname' in df.columns:
        report.append(f"Total Groups: {df['gname'].nunique()}")
        report.append("\nTop 15 Groups by Incident Count:")
        for group, count in df['gname'].value_counts().head(15).items():
            report.append(f"  {group}: {count:,}")

    # Missing values
    report.append("\n" + "-" * 40)
    report.append("MISSING VALUES")
    report.append("-" * 40)
    for col in df.columns:
        missing = df[col].isna().sum()
        if missing > 0:
            pct = (missing / len(df)) * 100
            report.append(f"  {col}: {missing:,} ({pct:.1f}%)")

    report.append("\n" + "=" * 60)

    # Write report
    report_text = "\n".join(report)
    with open(output_path, 'w') as f:
        f.write(report_text)

    print(f"\nData quality report saved to: {output_path}")
    print(report_text)


def main():
    """Main preprocessing function."""
    # Define paths
    project_dir = Path(__file__).parent.parent
    data_dir = project_dir
    processed_dir = project_dir / "data" / "processed"

    # Find the GTD Excel file
    excel_files = list(data_dir.glob("*.xlsx"))
    if not excel_files:
        print("Error: No Excel file found in the data directory")
        sys.exit(1)

    input_file = excel_files[0]
    output_file = processed_dir / "gtd_processed.parquet"
    report_file = processed_dir / "data_quality_report.txt"

    # Ensure output directory exists
    processed_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("GTD DATA PREPROCESSING")
    print("=" * 60)

    # Load data
    df = load_gtd_data(str(input_file))

    # Clean coordinates
    df = clean_coordinates(df)

    # Create datetime column
    df = create_datetime_column(df)

    # Select essential columns
    df = select_essential_columns(df)

    # Fill missing casualties
    df = fill_missing_casualties(df)

    # Optimize data types
    print("\nOptimizing data types...")
    if 'city' in df.columns:
        df['city'] = df['city'].astype('string')
    if 'country_txt' in df.columns:
        df['country_txt'] = df['country_txt'].astype('category')
    if 'region_txt' in df.columns:
        df['region_txt'] = df['region_txt'].astype('category')
    if 'attacktype1_txt' in df.columns:
        df['attacktype1_txt'] = df['attacktype1_txt'].astype('category')
    if 'targtype1_txt' in df.columns:
        df['targtype1_txt'] = df['targtype1_txt'].astype('category')
    if 'weaptype1_txt' in df.columns:
        df['weaptype1_txt'] = df['weaptype1_txt'].astype('category')
    if 'gname' in df.columns:
        df['gname'] = df['gname'].astype('string')

    # Generate quality report
    generate_quality_report(df, str(report_file))

    # Export to Parquet
    print(f"\nExporting to Parquet: {output_file}")
    df.to_parquet(
        output_file,
        engine='pyarrow',
        compression='snappy',
        index=False
    )

    # Report file size
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"Parquet file size: {file_size_mb:.1f} MB")

    print("\n" + "=" * 60)
    print("PREPROCESSING COMPLETE")
    print("=" * 60)
    print(f"\nProcessed data saved to: {output_file}")
    print(f"Records: {len(df):,}")

    return df


if __name__ == "__main__":
    main()
