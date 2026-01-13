"""
Country Deep Dive Page - Detailed country-level analysis.

Features:
- Country selector with incident counts
- KPI metrics for selected country
- Time series analysis
- Attack type and target breakdowns
- Top perpetrator groups
- City-level map
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_gtd_data

# Page configuration
st.set_page_config(
    page_title="Country Deep Dive - GTD",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Country Deep Dive")
st.markdown("Select a country to explore detailed terrorism patterns and trends.")


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
# COUNTRY SELECTOR
# ============================================
# Sort countries by incident count for better UX
country_counts = df['country_txt'].value_counts()
sorted_countries = country_counts.index.tolist()

col1, col2 = st.columns([2, 1])
with col1:
    selected_country = st.selectbox(
        "Select a Country",
        options=sorted_countries,
        index=0,
        help="Countries are sorted by total incident count"
    )

# Filter data
df_country = df[df['country_txt'] == selected_country]

with col2:
    rank = sorted_countries.index(selected_country) + 1
    st.metric(
        "Total Incidents",
        f"{len(df_country):,}",
        help=f"Rank: #{rank} globally"
    )

# ============================================
# KPI ROW FOR SELECTED COUNTRY
# ============================================
st.markdown("---")
k1, k2, k3, k4, k5 = st.columns(5)

total_killed = int(df_country['nkill'].sum()) if 'nkill' in df_country.columns else 0
total_wounded = int(df_country['nwound'].sum()) if 'nwound' in df_country.columns else 0
year_span = f"{df_country['iyear'].min()} - {df_country['iyear'].max()}"
peak_year = df_country['iyear'].value_counts().idxmax() if len(df_country) > 0 else "N/A"
active_groups = df_country['gname'].nunique() if 'gname' in df_country.columns else 0

k1.metric("Total Killed", f"{total_killed:,}")
k2.metric("Total Wounded", f"{total_wounded:,}")
k3.metric("Active Years", year_span)
k4.metric("Peak Year", peak_year)
k5.metric("Perpetrator Groups", active_groups)

# ============================================
# TIME SERIES ANALYSIS
# ============================================
st.markdown("---")
st.subheader(f"📈 Incident Trends in {selected_country}")

yearly = df_country.groupby('iyear').agg({
    'eventid': 'count',
    'nkill': 'sum',
    'nwound': 'sum'
}).reset_index()
yearly.columns = ['Year', 'Incidents', 'Killed', 'Wounded']

# Create multi-line chart
fig_trend = go.Figure()

fig_trend.add_trace(go.Scatter(
    x=yearly['Year'],
    y=yearly['Incidents'],
    name='Incidents',
    mode='lines+markers',
    line=dict(color='#e41a1c', width=3),
    fill='tozeroy',
    fillcolor='rgba(228, 26, 28, 0.2)'
))

fig_trend.add_trace(go.Scatter(
    x=yearly['Year'],
    y=yearly['Killed'],
    name='Killed',
    mode='lines+markers',
    line=dict(color='#377eb8', width=2),
    yaxis='y2'
))

fig_trend.update_layout(
    template='plotly_dark',
    height=400,
    hovermode='x unified',
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    yaxis=dict(title='Incidents', side='left'),
    yaxis2=dict(title='Casualties', side='right', overlaying='y'),
    margin=dict(l=60, r=60, t=40, b=40)
)

st.plotly_chart(fig_trend, use_container_width=True)

# ============================================
# BREAKDOWN CHARTS ROW
# ============================================
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("💥 Attack Types")

    attack_data = df_country['attacktype1_txt'].value_counts().reset_index()
    attack_data.columns = ['Attack Type', 'Count']

    fig_attack = px.bar(
        attack_data.head(8),
        x='Count',
        y='Attack Type',
        orientation='h',
        color='Count',
        color_continuous_scale='Reds'
    )
    fig_attack.update_layout(
        template='plotly_dark',
        height=350,
        showlegend=False,
        coloraxis_showscale=False,
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_attack, use_container_width=True)

with col_right:
    st.subheader("🎯 Target Types")

    target_data = df_country['targtype1_txt'].value_counts().reset_index()
    target_data.columns = ['Target Type', 'Count']

    fig_target = px.pie(
        target_data.head(8),
        values='Count',
        names='Target Type',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Plasma_r
    )
    fig_target.update_layout(
        template='plotly_dark',
        height=350,
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
    fig_target.update_traces(textposition='inside', textinfo='percent')
    st.plotly_chart(fig_target, use_container_width=True)

# ============================================
# TOP PERPETRATOR GROUPS
# ============================================
st.markdown("---")
st.subheader(f"👥 Top Perpetrator Groups in {selected_country}")

if 'gname' in df_country.columns:
    # Exclude "Unknown"
    groups = df_country[df_country['gname'] != 'Unknown']
    if len(groups) > 0:
        group_data = groups.groupby('gname').agg({
            'eventid': 'count',
            'nkill': 'sum',
            'iyear': ['min', 'max']
        }).reset_index()
        group_data.columns = ['Group', 'Incidents', 'Killed', 'First Year', 'Last Year']
        group_data = group_data.nlargest(10, 'Incidents')
        group_data['Active Period'] = group_data['First Year'].astype(str) + ' - ' + group_data['Last Year'].astype(str)
        group_data['Killed'] = group_data['Killed'].astype(int)

        # Display as styled dataframe
        st.dataframe(
            group_data[['Group', 'Incidents', 'Killed', 'Active Period']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Group": st.column_config.TextColumn("Perpetrator Group", width="large"),
                "Incidents": st.column_config.NumberColumn("Incidents", format="%d"),
                "Killed": st.column_config.NumberColumn("Killed", format="%d"),
                "Active Period": st.column_config.TextColumn("Active Period")
            }
        )
    else:
        st.info("No known perpetrator groups for this country.")
else:
    st.info("Group data not available.")

# ============================================
# CITY-LEVEL MAP
# ============================================
st.markdown("---")
st.subheader(f"🏙️ Most Affected Cities in {selected_country}")

if 'city' in df_country.columns:
    city_data = df_country.groupby('city').agg({
        'eventid': 'count',
        'nkill': 'sum',
        'latitude': 'first',
        'longitude': 'first'
    }).reset_index()
    city_data.columns = ['City', 'Incidents', 'Killed', 'lat', 'lon']
    city_data = city_data.dropna(subset=['lat', 'lon'])
    city_data = city_data[city_data['City'] != 'Unknown']
    city_data['Killed'] = city_data['Killed'].fillna(0).astype(int)

    if len(city_data) > 0:
        top_cities = city_data.nlargest(20, 'Incidents')

        # Calculate center of the country
        center_lat = top_cities['lat'].mean()
        center_lon = top_cities['lon'].mean()

        fig_cities = px.scatter_mapbox(
            top_cities,
            lat='lat',
            lon='lon',
            size='Incidents',
            color='Killed',
            hover_name='City',
            hover_data={'Incidents': True, 'Killed': True, 'lat': False, 'lon': False},
            color_continuous_scale='Reds',
            size_max=40,
            zoom=4,
            center=dict(lat=center_lat, lon=center_lon),
            mapbox_style='carto-darkmatter'
        )

        fig_cities.update_layout(
            height=500,
            margin=dict(l=0, r=0, t=0, b=0)
        )

        st.plotly_chart(fig_cities, use_container_width=True)

        # Also show table of top cities
        st.markdown("**Top 10 Cities by Incident Count:**")
        display_cities = top_cities.head(10)[['City', 'Incidents', 'Killed']].copy()
        st.dataframe(display_cities, use_container_width=True, hide_index=True)
    else:
        st.info("No city-level data available for this country.")
else:
    st.info("City data not available.")

# ============================================
# DECADE BREAKDOWN
# ============================================
st.markdown("---")
st.subheader(f"📊 Decade Breakdown for {selected_country}")

decade_df = df_country.copy()
decade_df['decade'] = (decade_df['iyear'] // 10) * 10
decade_labels = {1970: '1970s', 1980: '1980s', 1990: '1990s', 2000: '2000s', 2010: '2010s', 2020: '2020s'}
decade_df['decade_label'] = decade_df['decade'].map(decade_labels)

decade_stats = decade_df.groupby(['decade', 'decade_label']).agg({
    'eventid': 'count',
    'nkill': 'sum',
    'nwound': 'sum'
}).reset_index()
decade_stats.columns = ['Decade_Num', 'Decade', 'Incidents', 'Killed', 'Wounded']
decade_stats = decade_stats.sort_values('Decade_Num')

fig_decade = px.bar(
    decade_stats,
    x='Decade',
    y=['Incidents', 'Killed', 'Wounded'],
    barmode='group',
    color_discrete_sequence=['#e41a1c', '#377eb8', '#4daf4a']
)

fig_decade.update_layout(
    template='plotly_dark',
    height=350,
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    margin=dict(l=40, r=40, t=40, b=40)
)

st.plotly_chart(fig_decade, use_container_width=True)
