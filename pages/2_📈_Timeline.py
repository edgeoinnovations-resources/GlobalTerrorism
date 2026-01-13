"""
Timeline Page - Temporal analysis and animated visualizations.

Features:
- Animated scatter_geo visualization
- Year-by-year trend analysis
- Decade comparison charts
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_gtd_data, get_filtered_data, get_year_range
from utils.charts import create_decade_comparison_chart

# Page configuration
st.set_page_config(
    page_title="Timeline - GTD",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Timeline Analysis")
st.markdown("Explore how terrorism has evolved over 50 years.")

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

# Sidebar filters
st.sidebar.header("Filters")

year_range = get_year_range(df)
selected_years = st.sidebar.slider(
    "Year Range",
    min_value=year_range[0],
    max_value=year_range[1],
    value=year_range
)

regions = sorted(df['region_txt'].unique().tolist())
selected_regions = st.sidebar.multiselect(
    "Regions",
    options=regions,
    default=[]
)

# Filter data
filtered_df = get_filtered_data(
    df,
    year_range=selected_years,
    regions=selected_regions if selected_regions else None
)

st.sidebar.markdown(f"**Showing:** {len(filtered_df):,} incidents")

# Section 1: Animated Map
st.markdown("### Animated Global Visualization")
st.markdown("Press play to watch terrorism spread over time.")

# Aggregate by year and region
yearly_region = filtered_df.groupby(['iyear', 'region_txt']).agg({
    'eventid': 'count',
    'latitude': 'mean',
    'longitude': 'mean',
    'nkill': 'sum',
    'nwound': 'sum'
}).reset_index()

yearly_region.columns = ['Year', 'Region', 'Incidents', 'Latitude', 'Longitude', 'Killed', 'Wounded']

# Create animated scatter geo
if len(yearly_region) > 0:
    fig_scatter = px.scatter_geo(
        yearly_region,
        lat='Latitude',
        lon='Longitude',
        size='Incidents',
        color='Region',
        hover_name='Region',
        hover_data={
            'Incidents': True,
            'Killed': ':.0f',
            'Wounded': ':.0f',
            'Latitude': False,
            'Longitude': False
        },
        animation_frame='Year',
        projection='natural earth',
        color_discrete_map=REGION_COLORS,
        size_max=60,
        title='Global Terrorism Spread by Region'
    )

    fig_scatter.update_layout(
        template='plotly_dark',
        height=600,
        geo=dict(
            showland=True,
            landcolor='rgb(40, 40, 40)',
            countrycolor='rgb(60, 60, 60)',
            oceancolor='rgb(20, 20, 30)',
            showocean=True
        ),
        legend=dict(
            yanchor='top',
            y=0.99,
            xanchor='left',
            x=0.01
        )
    )

    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.warning("No data available for the selected filters.")

st.markdown("---")

# Section 2: Yearly Trends
st.markdown("### Yearly Trends")

yearly = filtered_df.groupby('iyear').agg({
    'eventid': 'count',
    'nkill': 'sum',
    'nwound': 'sum'
}).reset_index()
yearly.columns = ['Year', 'Incidents', 'Killed', 'Wounded']

# Create trend charts
col1, col2 = st.columns(2)

with col1:
    fig_incidents = go.Figure()
    fig_incidents.add_trace(go.Scatter(
        x=yearly['Year'],
        y=yearly['Incidents'],
        mode='lines+markers',
        name='Incidents',
        line=dict(color='#e41a1c', width=2),
        marker=dict(size=4)
    ))
    fig_incidents.update_layout(
        title='Incidents Per Year',
        xaxis_title='Year',
        yaxis_title='Number of Incidents',
        template='plotly_dark',
        height=350
    )
    st.plotly_chart(fig_incidents, use_container_width=True)

with col2:
    fig_casualties = go.Figure()
    fig_casualties.add_trace(go.Scatter(
        x=yearly['Year'],
        y=yearly['Killed'],
        mode='lines+markers',
        name='Killed',
        line=dict(color='#e41a1c', width=2),
        marker=dict(size=4)
    ))
    fig_casualties.add_trace(go.Scatter(
        x=yearly['Year'],
        y=yearly['Wounded'],
        mode='lines+markers',
        name='Wounded',
        line=dict(color='#377eb8', width=2),
        marker=dict(size=4)
    ))
    fig_casualties.update_layout(
        title='Casualties Per Year',
        xaxis_title='Year',
        yaxis_title='Count',
        template='plotly_dark',
        height=350,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig_casualties, use_container_width=True)

st.markdown("---")

# Section 3: Decade Comparison
st.markdown("### Decade Comparison")

# Create decade data
decade_df = filtered_df.copy()
decade_df['decade'] = (decade_df['iyear'] // 10) * 10
decade_df['decade_label'] = decade_df['decade'].astype(str) + 's'

decade_stats = decade_df.groupby(['decade', 'decade_label']).agg({
    'eventid': 'count',
    'nkill': 'sum',
    'nwound': 'sum'
}).reset_index()
decade_stats.columns = ['Decade_Num', 'Decade', 'Incidents', 'Killed', 'Wounded']
decade_stats = decade_stats.sort_values('Decade_Num')

col1, col2 = st.columns(2)

with col1:
    fig_decade_inc = px.bar(
        decade_stats,
        x='Decade',
        y='Incidents',
        color='Incidents',
        color_continuous_scale='Reds',
        title='Incidents by Decade'
    )
    fig_decade_inc.update_layout(
        template='plotly_dark',
        height=350,
        showlegend=False
    )
    st.plotly_chart(fig_decade_inc, use_container_width=True)

with col2:
    fig_decade_cas = go.Figure()
    fig_decade_cas.add_trace(go.Bar(
        x=decade_stats['Decade'],
        y=decade_stats['Killed'],
        name='Killed',
        marker_color='#e41a1c'
    ))
    fig_decade_cas.add_trace(go.Bar(
        x=decade_stats['Decade'],
        y=decade_stats['Wounded'],
        name='Wounded',
        marker_color='#377eb8'
    ))
    fig_decade_cas.update_layout(
        title='Casualties by Decade',
        barmode='group',
        template='plotly_dark',
        height=350,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig_decade_cas, use_container_width=True)

st.markdown("---")

# Section 4: Regional Trends Over Time
st.markdown("### Regional Trends Over Time")

region_yearly = filtered_df.groupby(['iyear', 'region_txt']).agg({
    'eventid': 'count'
}).reset_index()
region_yearly.columns = ['Year', 'Region', 'Incidents']

fig_region_trend = px.area(
    region_yearly,
    x='Year',
    y='Incidents',
    color='Region',
    color_discrete_map=REGION_COLORS,
    title='Regional Terrorism Trends'
)

fig_region_trend.update_layout(
    template='plotly_dark',
    height=450,
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=-0.4,
        xanchor='center',
        x=0.5
    )
)

st.plotly_chart(fig_region_trend, use_container_width=True)

st.markdown("---")

# Section 5: Attack Type Evolution
st.markdown("### Attack Type Evolution")

attack_yearly = filtered_df.groupby(['iyear', 'attacktype1_txt']).agg({
    'eventid': 'count'
}).reset_index()
attack_yearly.columns = ['Year', 'Attack Type', 'Incidents']

fig_attack_trend = px.line(
    attack_yearly,
    x='Year',
    y='Incidents',
    color='Attack Type',
    title='Attack Types Over Time'
)

fig_attack_trend.update_layout(
    template='plotly_dark',
    height=400,
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=-0.4,
        xanchor='center',
        x=0.5
    )
)

st.plotly_chart(fig_attack_trend, use_container_width=True)

# Key insights
st.markdown("---")
st.markdown("### Key Observations")

# Calculate some insights
peak_year = yearly.loc[yearly['Incidents'].idxmax()]
deadliest_year = yearly.loc[yearly['Killed'].idxmax()]

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **Peak Year for Incidents**

    {int(peak_year['Year'])}: {int(peak_year['Incidents']):,} incidents
    """)

with col2:
    st.error(f"""
    **Deadliest Year**

    {int(deadliest_year['Year'])}: {int(deadliest_year['Killed']):,} killed
    """)

with col3:
    total_incidents = filtered_df['eventid'].count()
    total_killed = filtered_df['nkill'].sum()
    avg_per_year = total_incidents / len(yearly)
    st.warning(f"""
    **Average per Year**

    {avg_per_year:,.0f} incidents
    """)
