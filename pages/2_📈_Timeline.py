"""
Timeline Page - Enhanced multi-view temporal analysis.

Features:
- Year slider controlling all visualizations
- KPI metrics for selected year
- 3D PyDeck HexagonLayer map
- Stacked area chart with year indicator
- Animated choropleth
- Top countries bar chart
- Attack type pie chart
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_gtd_data

# Page configuration
st.set_page_config(
    page_title="Timeline Analysis - GTD",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Timeline Analysis")
st.markdown("Explore how global terrorism has evolved over 50 years with interactive visualizations.")

# Color scheme for regions
REGION_COLORS = {
    'Middle East & North Africa': '#e41a1c',
    'South Asia': '#377eb8',
    'Sub-Saharan Africa': '#4daf4a',
    'South America': '#984ea3',
    'Western Europe': '#ff7f00',
    'Southeast Asia': '#ffff33',
    'Eastern Europe': '#a65628',
    'North America': '#f781bf',
    'Central America & Caribbean': '#999999',
    'East Asia': '#66c2a5',
    'Central Asia': '#fc8d62',
    'Australasia & Oceania': '#8da0cb'
}

# Country to ISO-3 mapping
COUNTRY_TO_ISO = {
    'Afghanistan': 'AFG', 'Albania': 'ALB', 'Algeria': 'DZA', 'Argentina': 'ARG',
    'Australia': 'AUS', 'Austria': 'AUT', 'Azerbaijan': 'AZE', 'Bahrain': 'BHR',
    'Bangladesh': 'BGD', 'Belgium': 'BEL', 'Bolivia': 'BOL', 'Bosnia-Herzegovina': 'BIH',
    'Brazil': 'BRA', 'Bulgaria': 'BGR', 'Burkina Faso': 'BFA', 'Burundi': 'BDI',
    'Cambodia': 'KHM', 'Cameroon': 'CMR', 'Canada': 'CAN', 'Central African Republic': 'CAF',
    'Chad': 'TCD', 'Chile': 'CHL', 'China': 'CHN', 'Colombia': 'COL',
    'Democratic Republic of the Congo': 'COD', 'Republic of the Congo': 'COG',
    'Costa Rica': 'CRI', 'Croatia': 'HRV', 'Cuba': 'CUB', 'Cyprus': 'CYP',
    'Czech Republic': 'CZE', 'Denmark': 'DNK', 'Djibouti': 'DJI', 'Dominican Republic': 'DOM',
    'Ecuador': 'ECU', 'Egypt': 'EGY', 'El Salvador': 'SLV', 'Eritrea': 'ERI',
    'Estonia': 'EST', 'Ethiopia': 'ETH', 'Finland': 'FIN', 'France': 'FRA',
    'Georgia': 'GEO', 'Germany': 'DEU', 'West Germany (FRG)': 'DEU', 'East Germany (GDR)': 'DEU',
    'Ghana': 'GHA', 'Greece': 'GRC', 'Guatemala': 'GTM', 'Guinea': 'GIN',
    'Haiti': 'HTI', 'Honduras': 'HND', 'Hong Kong': 'HKG', 'Hungary': 'HUN',
    'India': 'IND', 'Indonesia': 'IDN', 'Iran': 'IRN', 'Iraq': 'IRQ',
    'Ireland': 'IRL', 'Israel': 'ISR', 'Italy': 'ITA', 'Ivory Coast': 'CIV',
    'Jamaica': 'JAM', 'Japan': 'JPN', 'Jordan': 'JOR', 'Kazakhstan': 'KAZ',
    'Kenya': 'KEN', 'Kosovo': 'XKX', 'Kuwait': 'KWT', 'Kyrgyzstan': 'KGZ',
    'Laos': 'LAO', 'Latvia': 'LVA', 'Lebanon': 'LBN', 'Liberia': 'LBR',
    'Libya': 'LBY', 'Lithuania': 'LTU', 'Malaysia': 'MYS', 'Mali': 'MLI',
    'Mauritania': 'MRT', 'Mexico': 'MEX', 'Moldova': 'MDA', 'Morocco': 'MAR',
    'Mozambique': 'MOZ', 'Myanmar': 'MMR', 'Nepal': 'NPL', 'Netherlands': 'NLD',
    'New Zealand': 'NZL', 'Nicaragua': 'NIC', 'Niger': 'NER', 'Nigeria': 'NGA',
    'North Korea': 'PRK', 'Northern Ireland': 'GBR', 'Norway': 'NOR', 'Pakistan': 'PAK',
    'Panama': 'PAN', 'Papua New Guinea': 'PNG', 'Paraguay': 'PRY', 'Peru': 'PER',
    'Philippines': 'PHL', 'Poland': 'POL', 'Portugal': 'PRT', 'Qatar': 'QAT',
    'Romania': 'ROU', 'Russia': 'RUS', 'Rwanda': 'RWA', 'Saudi Arabia': 'SAU',
    'Senegal': 'SEN', 'Serbia': 'SRB', 'Sierra Leone': 'SLE', 'Singapore': 'SGP',
    'Slovakia': 'SVK', 'Slovenia': 'SVN', 'Somalia': 'SOM', 'South Africa': 'ZAF',
    'South Korea': 'KOR', 'South Sudan': 'SSD', 'Spain': 'ESP', 'Sri Lanka': 'LKA',
    'Sudan': 'SDN', 'Sweden': 'SWE', 'Switzerland': 'CHE', 'Syria': 'SYR',
    'Taiwan': 'TWN', 'Tajikistan': 'TJK', 'Tanzania': 'TZA', 'Thailand': 'THA',
    'Togo': 'TGO', 'Trinidad and Tobago': 'TTO', 'Tunisia': 'TUN', 'Turkey': 'TUR',
    'Turkmenistan': 'TKM', 'Uganda': 'UGA', 'Ukraine': 'UKR', 'United Arab Emirates': 'ARE',
    'United Kingdom': 'GBR', 'United States': 'USA', 'Uruguay': 'URY', 'Uzbekistan': 'UZB',
    'Venezuela': 'VEN', 'Vietnam': 'VNM', 'West Bank and Gaza Strip': 'PSE',
    'Yemen': 'YEM', 'Yugoslavia': 'SRB', 'Zambia': 'ZMB', 'Zimbabwe': 'ZWE'
}


@st.cache_data
def load_data():
    """Load and cache the GTD data."""
    return load_gtd_data()


# Load data
try:
    df = load_data()
except FileNotFoundError:
    st.error("Data file not found. Please run the preprocessing script first.")
    st.stop()

# ============================================
# YEAR SLIDER - Controls everything
# ============================================
min_year = int(df['iyear'].min())
max_year = int(df['iyear'].max())

selected_year = st.slider(
    "**Select Year** - Controls all visualizations below",
    min_value=min_year,
    max_value=max_year,
    value=2014,
    key="year_slider"
)

# Filter data for selected year
df_year = df[df['iyear'] == selected_year]

# ============================================
# KPI METRICS ROW
# ============================================
st.markdown("---")

incidents = len(df_year)
killed = int(df_year['nkill'].sum()) if 'nkill' in df_year.columns else 0
wounded = int(df_year['nwound'].sum()) if 'nwound' in df_year.columns else 0
countries = df_year['country_txt'].nunique()
groups = df_year['gname'].nunique() if 'gname' in df_year.columns else 0

# Calculate year-over-year change
df_prev = df[df['iyear'] == selected_year - 1]
prev_incidents = len(df_prev)
delta = f"{((incidents - prev_incidents) / prev_incidents * 100):+.1f}%" if prev_incidents > 0 else "N/A"

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Incidents", f"{incidents:,}", delta=delta)
kpi2.metric("Killed", f"{killed:,}")
kpi3.metric("Wounded", f"{wounded:,}")
kpi4.metric("Countries", countries)
kpi5.metric("Active Groups", groups)

# ============================================
# MAIN VISUALIZATION ROW
# ============================================
st.markdown("---")
map_col, chart_col = st.columns([2, 1])

with map_col:
    st.subheader(f"🗺️ Global Hotspots in {selected_year}")

    if len(df_year) > 0:
        # PyDeck 3D HexagonLayer
        hex_layer = pdk.Layer(
            "HexagonLayer",
            data=df_year,
            get_position=['longitude', 'latitude'],
            radius=50000,
            elevation_scale=500,
            elevation_range=[0, 10000],
            extruded=True,
            pickable=True,
            auto_highlight=True,
            color_range=[
                [255, 255, 178],
                [254, 217, 118],
                [254, 178, 76],
                [253, 141, 60],
                [240, 59, 32],
                [189, 0, 38]
            ]
        )

        view_state = pdk.ViewState(
            latitude=20,
            longitude=0,
            zoom=1.2,
            pitch=45,
            bearing=0
        )

        # Use Carto dark basemap (no token required) with light boundaries
        deck = pdk.Deck(
            layers=[hex_layer],
            initial_view_state=view_state,
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
            tooltip={
                "html": "<b>Incidents:</b> {elevationValue}",
                "style": {"backgroundColor": "steelblue", "color": "white"}
            }
        )

        st.pydeck_chart(deck, use_container_width=True)
    else:
        st.warning("No incidents recorded for this year.")

with chart_col:
    st.subheader("📊 Incidents by Region Over Time")

    # Prepare data for stacked area chart
    yearly_by_region = df.groupby(['iyear', 'region_txt']).size().reset_index(name='incidents')

    fig_area = px.area(
        yearly_by_region,
        x='iyear',
        y='incidents',
        color='region_txt',
        labels={'iyear': 'Year', 'incidents': 'Incidents', 'region_txt': 'Region'},
        color_discrete_map=REGION_COLORS
    )

    # Add vertical line for selected year
    fig_area.add_vline(
        x=selected_year,
        line_dash="dash",
        line_color="white",
        line_width=2,
        annotation_text=str(selected_year),
        annotation_position="top"
    )

    fig_area.update_layout(
        template='plotly_dark',
        height=450,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.5,
            xanchor="center",
            x=0.5,
            font=dict(size=9)
        ),
        showlegend=True
    )

    st.plotly_chart(fig_area, use_container_width=True)

# ============================================
# ANIMATED CHOROPLETH SECTION
# ============================================
st.markdown("---")
st.subheader("🌍 Country-Level Incident Density (Animated)")
st.markdown("*Press play to watch terrorism evolve across countries over time.*")

# Aggregate by year and country
country_yearly = df.groupby(['iyear', 'country_txt']).agg({
    'eventid': 'count',
    'nkill': 'sum',
    'nwound': 'sum'
}).reset_index()
country_yearly.columns = ['year', 'country', 'incidents', 'killed', 'wounded']

# Add ISO codes
country_yearly['iso_alpha'] = country_yearly['country'].map(COUNTRY_TO_ISO)
country_yearly = country_yearly.dropna(subset=['iso_alpha'])

# Create animated choropleth
fig_choropleth = px.choropleth(
    country_yearly,
    locations='iso_alpha',
    locationmode='ISO-3',
    color='incidents',
    hover_name='country',
    hover_data={'incidents': True, 'killed': True, 'wounded': True, 'iso_alpha': False},
    animation_frame='year',
    color_continuous_scale='Reds',
    range_color=[0, country_yearly['incidents'].quantile(0.95)],
    projection='natural earth'
)

fig_choropleth.update_layout(
    template='plotly_dark',
    height=500,
    margin=dict(l=0, r=0, t=30, b=0),
    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor='rgba(255,255,255,0.3)',
        bgcolor='rgba(0,0,0,0)'
    ),
    coloraxis_colorbar=dict(
        title="Incidents",
        thickness=15,
        len=0.7
    )
)

fig_choropleth.update_geos(
    visible=True,
    resolution=110,
    showcountries=True,
    countrycolor="rgba(255,255,255,0.2)"
)

st.plotly_chart(fig_choropleth, use_container_width=True)

# ============================================
# BOTTOM ROW: BAR CHART + PIE CHART
# ============================================
st.markdown("---")
bottom_left, bottom_right = st.columns(2)

with bottom_left:
    st.subheader(f"🏆 Top 10 Countries in {selected_year}")

    if len(df_year) > 0:
        top_countries = df_year.groupby('country_txt').size().reset_index(name='incidents')
        top_countries = top_countries.nlargest(10, 'incidents')

        fig_bar = px.bar(
            top_countries,
            x='incidents',
            y='country_txt',
            orientation='h',
            color='incidents',
            color_continuous_scale='Reds',
            labels={'country_txt': '', 'incidents': 'Incidents'}
        )

        fig_bar.update_layout(
            template='plotly_dark',
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            coloraxis_showscale=False
        )

        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No data for selected year.")

with bottom_right:
    st.subheader(f"💥 Attack Types in {selected_year}")

    if len(df_year) > 0:
        attack_types = df_year.groupby('attacktype1_txt').size().reset_index(name='incidents')

        fig_pie = px.pie(
            attack_types,
            values='incidents',
            names='attacktype1_txt',
            color_discrete_sequence=px.colors.sequential.RdBu,
            hole=0.4
        )

        fig_pie.update_layout(
            template='plotly_dark',
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5,
                font=dict(size=9)
            )
        )

        fig_pie.update_traces(textposition='inside', textinfo='percent')

        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No data for selected year.")

# ============================================
# REGIONAL TRENDS SECTION
# ============================================
st.markdown("---")
st.subheader("📈 Regional Trends Over Time")

region_yearly = df.groupby(['iyear', 'region_txt']).agg({
    'eventid': 'count'
}).reset_index()
region_yearly.columns = ['Year', 'Region', 'Incidents']

fig_region_trend = px.line(
    region_yearly,
    x='Year',
    y='Incidents',
    color='Region',
    color_discrete_map=REGION_COLORS
)

# Add vertical line for selected year
fig_region_trend.add_vline(
    x=selected_year,
    line_dash="dash",
    line_color="yellow",
    line_width=2,
    annotation_text=f"Selected: {selected_year}",
    annotation_position="top"
)

fig_region_trend.update_layout(
    template='plotly_dark',
    height=400,
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=-0.4,
        xanchor='center',
        x=0.5,
        font=dict(size=9)
    )
)

st.plotly_chart(fig_region_trend, use_container_width=True)

# ============================================
# KEY INSIGHTS
# ============================================
st.markdown("---")
st.subheader("📌 Key Observations")

# Calculate insights
yearly_totals = df.groupby('iyear').size()
peak_year_val = yearly_totals.idxmax()
peak_incidents = yearly_totals.max()

yearly_killed = df.groupby('iyear')['nkill'].sum()
deadliest_year = yearly_killed.idxmax()
deadliest_count = int(yearly_killed.max())

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **Peak Year for Incidents**

    {peak_year_val}: {peak_incidents:,} incidents
    """)

with col2:
    st.error(f"""
    **Deadliest Year**

    {deadliest_year}: {deadliest_count:,} killed
    """)

with col3:
    avg_per_year = len(df) / len(yearly_totals)
    st.warning(f"""
    **50-Year Average**

    {avg_per_year:,.0f} incidents/year
    """)
