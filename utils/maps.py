"""PyDeck map layer configurations for the GTD dashboard."""

import os
from typing import Dict, List, Optional

import pandas as pd
import pydeck as pdk
from dotenv import load_dotenv

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.color_schemes import get_attack_color_rgb, ATTACK_TYPE_COLORS_RGB

# Load environment variables
load_dotenv()

# Get Mapbox token from environment or Streamlit secrets
MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN', '')

# Try to get from Streamlit secrets if not in environment
try:
    import streamlit as st
    if hasattr(st, 'secrets') and 'MAPBOX_TOKEN' in st.secrets:
        MAPBOX_TOKEN = st.secrets['MAPBOX_TOKEN']
except:
    pass


def get_pydeck_tooltip() -> Dict:
    """Get the tooltip configuration for PyDeck maps."""
    return {
        "html": """
        <div style="font-family: Arial, sans-serif; padding: 10px;">
            <b style="font-size: 14px;">{city}, {country_txt}</b><br/>
            <hr style="margin: 5px 0; border-color: #444;"/>
            <b>Date:</b> {event_date}<br/>
            <b>Attack Type:</b> {attacktype1_txt}<br/>
            <b>Target:</b> {targtype1_txt}<br/>
            <b>Group:</b> {gname}<br/>
            <hr style="margin: 5px 0; border-color: #444;"/>
            <b>Killed:</b> {nkill} | <b>Wounded:</b> {nwound}
        </div>
        """,
        "style": {
            "backgroundColor": "rgba(20, 20, 30, 0.9)",
            "color": "white",
            "border": "1px solid #444"
        }
    }


def create_hexagon_layer(
    df: pd.DataFrame,
    radius: int = 50000,
    elevation_scale: int = 1000,
    extruded: bool = True
) -> pdk.Layer:
    """
    Create a 3D hexagon aggregation layer.

    Args:
        df: DataFrame with latitude and longitude columns
        radius: Hexagon radius in meters
        elevation_scale: Multiplier for hexagon height
        extruded: Whether to show 3D extrusion

    Returns:
        PyDeck HexagonLayer
    """
    return pdk.Layer(
        "HexagonLayer",
        data=df,
        get_position=["longitude", "latitude"],
        radius=radius,
        elevation_scale=elevation_scale,
        elevation_range=[0, 3000],
        extruded=extruded,
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


def create_scatterplot_layer(
    df: pd.DataFrame,
    radius_scale: int = 100,
    radius_min: int = 50,
    radius_max: int = 5000
) -> pdk.Layer:
    """
    Create a scatterplot layer with points colored by attack type.

    Args:
        df: DataFrame with required columns
        radius_scale: Scale factor for point radius
        radius_min: Minimum radius in meters
        radius_max: Maximum radius in meters

    Returns:
        PyDeck ScatterplotLayer
    """
    # Add color column based on attack type
    df = df.copy()

    def get_color(attack_type):
        return ATTACK_TYPE_COLORS_RGB.get(attack_type, [153, 153, 153])

    df['color'] = df['attacktype1_txt'].apply(get_color)

    # Calculate radius based on casualties
    df['radius'] = (df['total_casualties'].fillna(0) * radius_scale + radius_min).clip(
        lower=radius_min, upper=radius_max
    )

    return pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_color="color",
        get_radius="radius",
        pickable=True,
        auto_highlight=True,
        opacity=0.6
    )


def create_heatmap_layer(df: pd.DataFrame, radius: int = 50000) -> pdk.Layer:
    """
    Create a heatmap layer for incident density.

    Args:
        df: DataFrame with latitude and longitude
        radius: Heatmap radius in meters

    Returns:
        PyDeck HeatmapLayer
    """
    return pdk.Layer(
        "HeatmapLayer",
        data=df,
        get_position=["longitude", "latitude"],
        aggregation="SUM",
        get_weight="total_casualties" if "total_casualties" in df.columns else 1,
        radius_pixels=50,
        opacity=0.8,
        color_range=[
            [255, 255, 178, 100],
            [254, 217, 118, 150],
            [254, 178, 76, 180],
            [253, 141, 60, 200],
            [252, 78, 42, 220],
            [227, 26, 28, 240],
            [177, 0, 38, 255]
        ]
    )


def create_pydeck_map(
    df: pd.DataFrame,
    layer_type: str = "hexagon",
    pitch: int = 45,
    zoom: int = 2,
    center: Optional[List[float]] = None
) -> pdk.Deck:
    """
    Create a complete PyDeck map with the specified layer type.

    Args:
        df: DataFrame with required columns
        layer_type: One of 'hexagon', 'scatter', 'heatmap'
        pitch: Map pitch angle
        zoom: Initial zoom level
        center: [longitude, latitude] for map center

    Returns:
        PyDeck Deck object
    """
    if center is None:
        center = [20, 20]

    # Create the appropriate layer
    if layer_type == "hexagon":
        layer = create_hexagon_layer(df)
    elif layer_type == "scatter":
        layer = create_scatterplot_layer(df)
    elif layer_type == "heatmap":
        layer = create_heatmap_layer(df)
    else:
        raise ValueError(f"Unknown layer type: {layer_type}")

    # Create view state
    view_state = pdk.ViewState(
        latitude=center[1],
        longitude=center[0],
        zoom=zoom,
        pitch=pitch,
        bearing=0
    )

    # Create deck
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip=get_pydeck_tooltip() if layer_type != "heatmap" else None
    )

    # Set Mapbox token
    if MAPBOX_TOKEN:
        deck.mapbox_key = MAPBOX_TOKEN

    return deck


def export_pydeck_to_html(deck: pdk.Deck, filepath: str) -> None:
    """
    Export a PyDeck map to standalone HTML.

    Args:
        deck: PyDeck Deck object
        filepath: Output file path
    """
    html = deck.to_html(as_string=True)
    with open(filepath, 'w') as f:
        f.write(html)
    print(f"Exported PyDeck map to: {filepath}")
