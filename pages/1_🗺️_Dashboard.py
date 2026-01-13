"""
Dashboard Page - Main interactive visualization dashboard.

Features:
- KPI metrics cards
- 3D PyDeck HexagonLayer map
- Time series chart
- Top countries bar chart
- Searchable data table
"""

import streamlit as st
import pandas as pd
import pydeck as pdk

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import (
    load_gtd_data,
    get_filtered_data,
    get_unique_values,
    get_year_range,
    get_summary_stats
)
from utils.charts import create_time_series_chart, create_top_countries_chart
from utils.maps import create_hexagon_layer, get_pydeck_tooltip, MAPBOX_TOKEN

# Page configuration
st.set_page_config(
    page_title="Dashboard - GTD",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Interactive Dashboard")
st.markdown("Explore global terrorism incidents with interactive maps and charts.")


@st.cache_data
def load_data():
    """Load and cache the GTD data."""
    return load_gtd_data()


# Load data
try:
    df = load_data()
except FileNotFoundError as e:
    st.error("""
    **Data file not found!**

    Please run the preprocessing script first:
    ```bash
    python scripts/preprocess_data.py
    ```
    """)
    st.stop()

# Get data ranges for filters
year_range = get_year_range(df)
regions = get_unique_values(df, 'region_txt')
attack_types = get_unique_values(df, 'attacktype1_txt')
target_types = get_unique_values(df, 'targtype1_txt')

# Sidebar filters
st.sidebar.header("Filters")

# Year range slider
selected_years = st.sidebar.slider(
    "Year Range",
    min_value=year_range[0],
    max_value=year_range[1],
    value=year_range,
    step=1
)

# Region filter
selected_regions = st.sidebar.multiselect(
    "Regions",
    options=regions,
    default=[]
)

# Attack type filter
selected_attacks = st.sidebar.multiselect(
    "Attack Types",
    options=attack_types,
    default=[]
)

# Target type filter
selected_targets = st.sidebar.multiselect(
    "Target Types",
    options=target_types,
    default=[]
)

# Casualty threshold
min_casualties = st.sidebar.slider(
    "Minimum Casualties",
    min_value=0,
    max_value=100,
    value=0,
    step=1
)

# Success filter
success_only = st.sidebar.checkbox("Successful Attacks Only", value=False)

# Apply filters
filtered_df = get_filtered_data(
    df,
    year_range=selected_years,
    regions=selected_regions if selected_regions else None,
    attack_types=selected_attacks if selected_attacks else None,
    target_types=selected_targets if selected_targets else None,
    min_casualties=min_casualties,
    success_only=success_only
)

# Display filter summary
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Showing:** {len(filtered_df):,} incidents")
st.sidebar.markdown(f"**Total:** {len(df):,} incidents")

# Row 1: KPI Metrics
st.markdown("### Key Metrics")
stats = get_summary_stats(filtered_df)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Incidents", f"{stats['total_incidents']:,}")

with col2:
    st.metric("Total Killed", f"{stats['total_killed']:,}")

with col3:
    st.metric("Total Wounded", f"{stats['total_wounded']:,}")

with col4:
    st.metric("Countries Affected", f"{stats['countries_affected']:,}")

with col5:
    st.metric("Perpetrator Groups", f"{stats['active_groups']:,}")

st.markdown("---")

# Row 2: Interactive Map
st.markdown("### 3D Incident Density Map")

# Map controls
map_col1, map_col2, map_col3 = st.columns([1, 1, 2])

with map_col1:
    map_pitch = st.slider("Map Pitch", 0, 60, 45)

with map_col2:
    hex_radius = st.slider("Hexagon Radius (km)", 20, 200, 50)

# Create PyDeck map
if len(filtered_df) > 0:
    # Create hexagon layer
    hex_layer = pdk.Layer(
        "HexagonLayer",
        data=filtered_df,
        get_position=["longitude", "latitude"],
        radius=hex_radius * 1000,  # Convert km to meters
        elevation_scale=500,
        elevation_range=[0, 3000],
        extruded=True,
        pickable=True,
        auto_highlight=True,
        coverage=0.9,
        color_range=[
            [255, 255, 178],
            [254, 217, 118],
            [254, 178, 76],
            [253, 141, 60],
            [252, 78, 42],
            [227, 26, 28],
            [177, 0, 38]
        ]
    )

    # View state
    view_state = pdk.ViewState(
        latitude=20,
        longitude=0,
        zoom=1.5,
        pitch=map_pitch,
        bearing=0
    )

    # Create deck
    deck = pdk.Deck(
        layers=[hex_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={
            "html": "<b>Incidents:</b> {elevationValue}",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white"
            }
        }
    )

    if MAPBOX_TOKEN:
        deck.mapbox_key = MAPBOX_TOKEN

    st.pydeck_chart(deck)
else:
    st.warning("No data matches the current filters.")

st.markdown("---")

# Row 3: Charts
st.markdown("### Trend Analysis")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    if len(filtered_df) > 0:
        time_fig = create_time_series_chart(filtered_df)
        st.plotly_chart(time_fig, use_container_width=True)

with chart_col2:
    if len(filtered_df) > 0:
        countries_fig = create_top_countries_chart(filtered_df)
        st.plotly_chart(countries_fig, use_container_width=True)

st.markdown("---")

# Row 4: Data Table
st.markdown("### Incident Data")

# Table controls
table_col1, table_col2, table_col3 = st.columns([1, 1, 2])

with table_col1:
    rows_to_show = st.selectbox("Rows to display", [100, 500, 1000], index=0)

with table_col2:
    sort_by = st.selectbox(
        "Sort by",
        ['event_date', 'total_casualties', 'nkill', 'country_txt'],
        index=0
    )

# Prepare display dataframe
display_cols = [
    'event_date', 'country_txt', 'city', 'region_txt',
    'attacktype1_txt', 'targtype1_txt', 'gname',
    'nkill', 'nwound', 'total_casualties'
]

display_df = filtered_df[
    [c for c in display_cols if c in filtered_df.columns]
].copy()

# Rename columns for display
display_df.columns = [
    'Date', 'Country', 'City', 'Region',
    'Attack Type', 'Target Type', 'Group',
    'Killed', 'Wounded', 'Total Casualties'
][:len(display_df.columns)]

# Sort
if sort_by == 'event_date':
    display_df = display_df.sort_values('Date', ascending=False)
elif sort_by == 'total_casualties':
    display_df = display_df.sort_values('Total Casualties', ascending=False)
elif sort_by == 'nkill':
    display_df = display_df.sort_values('Killed', ascending=False)
else:
    display_df = display_df.sort_values('Country')

# Display table
st.dataframe(
    display_df.head(rows_to_show),
    use_container_width=True,
    height=400
)

# Download button
csv = display_df.to_csv(index=False)
st.download_button(
    label="Download Data (CSV)",
    data=csv,
    file_name="gtd_filtered_data.csv",
    mime="text/csv"
)
