"""
Groups Page - Perpetrator group analysis.

Features:
- Top perpetrator groups by incident count
- Group activity over time
- Geographic distribution per group
- Attack type preferences by group
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_gtd_data, get_filtered_data, get_year_range
from utils.charts import create_groups_chart, create_group_timeline_chart

# Page configuration
st.set_page_config(
    page_title="Groups - GTD",
    page_icon="👥",
    layout="wide"
)

st.title("👥 Perpetrator Group Analysis")
st.markdown("Explore terrorist organizations and their activities.")

# Attack type colors
ATTACK_COLORS = {
    'Bombing/Explosion': '#e41a1c',
    'Armed Assault': '#377eb8',
    'Assassination': '#4daf4a',
    'Hostage Taking (Kidnapping)': '#984ea3',
    'Hostage Taking (Barricade Incident)': '#ff7f00',
    'Facility/Infrastructure Attack': '#ffff33',
    'Unarmed Assault': '#a65628',
    'Hijacking': '#f781bf',
    'Unknown': '#999999'
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

# Filter out unknown groups
known_groups_df = filtered_df[
    ~filtered_df['gname'].isin(['Unknown', 'unknown', '', None])
]

st.sidebar.markdown(f"**Showing:** {len(known_groups_df):,} incidents")
st.sidebar.markdown(f"**Groups:** {known_groups_df['gname'].nunique():,}")

# Section 1: Top Groups
st.markdown("### Top Perpetrator Groups")

top_n = st.slider("Number of groups to display", 10, 50, 20)

# Calculate group statistics
group_stats = known_groups_df.groupby('gname').agg({
    'eventid': 'count',
    'nkill': 'sum',
    'nwound': 'sum',
    'country_txt': 'nunique',
    'iyear': ['min', 'max']
}).reset_index()

group_stats.columns = ['Group', 'Incidents', 'Killed', 'Wounded', 'Countries', 'First_Year', 'Last_Year']
group_stats['Total_Casualties'] = group_stats['Killed'] + group_stats['Wounded']
group_stats['Years_Active'] = group_stats['Last_Year'] - group_stats['First_Year'] + 1
group_stats = group_stats.sort_values('Incidents', ascending=False)

# Display top groups chart
top_groups = group_stats.head(top_n)

fig_groups = go.Figure(go.Bar(
    x=top_groups['Incidents'],
    y=top_groups['Group'],
    orientation='h',
    marker_color='#377eb8',
    text=top_groups['Incidents'].apply(lambda x: f'{x:,}'),
    textposition='outside'
))

fig_groups.update_layout(
    title=f'Top {top_n} Perpetrator Groups by Incident Count',
    xaxis_title='Number of Incidents',
    yaxis_title='',
    template='plotly_dark',
    height=max(400, top_n * 25),
    margin=dict(l=300, r=100, t=50, b=40),
    yaxis=dict(autorange='reversed')
)

st.plotly_chart(fig_groups, use_container_width=True)

st.markdown("---")

# Section 2: Group Details
st.markdown("### Group Deep Dive")

# Select a group
selected_group = st.selectbox(
    "Select a group to analyze",
    options=top_groups['Group'].tolist()
)

if selected_group:
    group_data = known_groups_df[known_groups_df['gname'] == selected_group]
    group_info = group_stats[group_stats['Group'] == selected_group].iloc[0]

    # Group metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Incidents", f"{int(group_info['Incidents']):,}")

    with col2:
        st.metric("People Killed", f"{int(group_info['Killed']):,}")

    with col3:
        st.metric("People Wounded", f"{int(group_info['Wounded']):,}")

    with col4:
        st.metric("Countries", f"{int(group_info['Countries'])}")

    with col5:
        st.metric("Years Active", f"{int(group_info['Years_Active'])}")

    # Group timeline
    st.markdown(f"#### {selected_group} - Activity Over Time")

    group_yearly = group_data.groupby('iyear').agg({
        'eventid': 'count',
        'nkill': 'sum',
        'nwound': 'sum'
    }).reset_index()
    group_yearly.columns = ['Year', 'Incidents', 'Killed', 'Wounded']

    fig_timeline = go.Figure()

    fig_timeline.add_trace(go.Bar(
        x=group_yearly['Year'],
        y=group_yearly['Incidents'],
        name='Incidents',
        marker_color='#377eb8'
    ))

    fig_timeline.add_trace(go.Scatter(
        x=group_yearly['Year'],
        y=group_yearly['Killed'],
        name='Killed',
        mode='lines+markers',
        yaxis='y2',
        line=dict(color='#e41a1c', width=2)
    ))

    fig_timeline.update_layout(
        title=f'{selected_group} - Incidents and Casualties',
        xaxis_title='Year',
        yaxis=dict(title='Incidents', side='left'),
        yaxis2=dict(title='Killed', side='right', overlaying='y'),
        template='plotly_dark',
        height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    st.plotly_chart(fig_timeline, use_container_width=True)

    # Two columns for additional analysis
    col1, col2 = st.columns(2)

    with col1:
        # Attack type preferences
        st.markdown(f"#### Attack Type Preferences")

        attack_counts = group_data['attacktype1_txt'].value_counts()

        colors = [ATTACK_COLORS.get(at, '#999999') for at in attack_counts.index]

        fig_attacks = go.Figure(go.Pie(
            labels=attack_counts.index,
            values=attack_counts.values,
            marker_colors=colors,
            hole=0.4,
            textinfo='percent+label',
            textposition='outside'
        ))

        fig_attacks.update_layout(
            title='Attack Type Distribution',
            template='plotly_dark',
            height=350,
            showlegend=False
        )

        st.plotly_chart(fig_attacks, use_container_width=True)

    with col2:
        # Geographic focus
        st.markdown(f"#### Geographic Focus")

        country_counts = group_data['country_txt'].value_counts().head(10)

        fig_countries = go.Figure(go.Bar(
            x=country_counts.values,
            y=country_counts.index,
            orientation='h',
            marker_color='#4daf4a'
        ))

        fig_countries.update_layout(
            title='Top Countries',
            xaxis_title='Incidents',
            template='plotly_dark',
            height=350,
            yaxis=dict(autorange='reversed'),
            margin=dict(l=150)
        )

        st.plotly_chart(fig_countries, use_container_width=True)

st.markdown("---")

# Section 3: Group Comparison
st.markdown("### Group Comparison")

comparison_groups = st.multiselect(
    "Select groups to compare",
    options=top_groups['Group'].tolist(),
    default=top_groups['Group'].head(5).tolist()
)

if len(comparison_groups) > 0:
    comparison_data = group_stats[group_stats['Group'].isin(comparison_groups)]

    col1, col2 = st.columns(2)

    with col1:
        # Incidents comparison
        fig_comp_inc = go.Figure(go.Bar(
            x=comparison_data['Group'],
            y=comparison_data['Incidents'],
            marker_color='#377eb8',
            text=comparison_data['Incidents'].apply(lambda x: f'{x:,}'),
            textposition='outside'
        ))

        fig_comp_inc.update_layout(
            title='Incidents Comparison',
            xaxis_title='',
            yaxis_title='Incidents',
            template='plotly_dark',
            height=350,
            xaxis_tickangle=-45
        )

        st.plotly_chart(fig_comp_inc, use_container_width=True)

    with col2:
        # Casualties comparison
        fig_comp_cas = go.Figure()

        fig_comp_cas.add_trace(go.Bar(
            x=comparison_data['Group'],
            y=comparison_data['Killed'],
            name='Killed',
            marker_color='#e41a1c'
        ))

        fig_comp_cas.add_trace(go.Bar(
            x=comparison_data['Group'],
            y=comparison_data['Wounded'],
            name='Wounded',
            marker_color='#377eb8'
        ))

        fig_comp_cas.update_layout(
            title='Casualties Comparison',
            xaxis_title='',
            yaxis_title='Count',
            template='plotly_dark',
            height=350,
            barmode='group',
            xaxis_tickangle=-45,
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )

        st.plotly_chart(fig_comp_cas, use_container_width=True)

    # Timeline comparison
    st.markdown("#### Activity Timeline Comparison")

    comparison_yearly = known_groups_df[
        known_groups_df['gname'].isin(comparison_groups)
    ].groupby(['iyear', 'gname']).agg({
        'eventid': 'count'
    }).reset_index()
    comparison_yearly.columns = ['Year', 'Group', 'Incidents']

    fig_timeline_comp = px.line(
        comparison_yearly,
        x='Year',
        y='Incidents',
        color='Group',
        title='Group Activity Over Time'
    )

    fig_timeline_comp.update_layout(
        template='plotly_dark',
        height=400,
        legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5)
    )

    st.plotly_chart(fig_timeline_comp, use_container_width=True)

st.markdown("---")

# Section 4: Full Group List
st.markdown("### Complete Group Statistics")

# Format for display
display_stats = group_stats.head(100).copy()
display_stats['Killed'] = display_stats['Killed'].astype(int)
display_stats['Wounded'] = display_stats['Wounded'].astype(int)
display_stats['Active Period'] = display_stats.apply(
    lambda r: f"{int(r['First_Year'])}-{int(r['Last_Year'])}", axis=1
)

display_cols = ['Group', 'Incidents', 'Killed', 'Wounded', 'Countries', 'Active Period']

st.dataframe(
    display_stats[display_cols],
    use_container_width=True,
    height=400
)

# Download button
csv = group_stats.to_csv(index=False)
st.download_button(
    label="Download Full Group Statistics (CSV)",
    data=csv,
    file_name="gtd_group_statistics.csv",
    mime="text/csv"
)
