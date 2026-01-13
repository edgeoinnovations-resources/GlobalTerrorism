"""Reusable Plotly chart components for the GTD dashboard."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.color_schemes import ATTACK_TYPE_COLORS, REGION_COLORS


def create_time_series_chart(
    df: pd.DataFrame,
    show_casualties: bool = False
) -> go.Figure:
    """
    Create a time series chart of incidents per year.

    Args:
        df: Filtered GTD dataframe
        show_casualties: Whether to show casualties instead of incident count

    Returns:
        Plotly figure object
    """
    yearly = df.groupby('iyear').agg({
        'eventid': 'count',
        'nkill': 'sum',
        'nwound': 'sum'
    }).reset_index()
    yearly.columns = ['Year', 'Incidents', 'Killed', 'Wounded']

    if show_casualties:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yearly['Year'],
            y=yearly['Killed'],
            name='Killed',
            mode='lines+markers',
            line=dict(color='#e41a1c', width=2),
            marker=dict(size=4)
        ))
        fig.add_trace(go.Scatter(
            x=yearly['Year'],
            y=yearly['Wounded'],
            name='Wounded',
            mode='lines+markers',
            line=dict(color='#377eb8', width=2),
            marker=dict(size=4)
        ))
        fig.update_layout(
            title='Casualties Over Time',
            yaxis_title='Count'
        )
    else:
        fig = px.line(
            yearly,
            x='Year',
            y='Incidents',
            markers=True,
            title='Terrorist Incidents Per Year'
        )
        fig.update_traces(
            line=dict(color='#e41a1c', width=2),
            marker=dict(size=4)
        )
        fig.update_layout(yaxis_title='Number of Incidents')

    fig.update_layout(
        xaxis_title='Year',
        template='plotly_dark',
        height=350,
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    return fig


def create_top_countries_chart(
    df: pd.DataFrame,
    top_n: int = 10
) -> go.Figure:
    """
    Create a horizontal bar chart of top countries by incident count.

    Args:
        df: Filtered GTD dataframe
        top_n: Number of countries to show

    Returns:
        Plotly figure object
    """
    country_counts = df['country_txt'].value_counts().head(top_n).sort_values()

    fig = go.Figure(go.Bar(
        x=country_counts.values,
        y=country_counts.index,
        orientation='h',
        marker_color='#e41a1c'
    ))

    fig.update_layout(
        title=f'Top {top_n} Countries by Incidents',
        xaxis_title='Number of Incidents',
        yaxis_title='',
        template='plotly_dark',
        height=350,
        margin=dict(l=120, r=40, t=50, b=40)
    )

    return fig


def create_attack_type_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a pie chart of attack types.

    Args:
        df: Filtered GTD dataframe

    Returns:
        Plotly figure object
    """
    attack_counts = df['attacktype1_txt'].value_counts()

    colors = [ATTACK_TYPE_COLORS.get(attack, '#999999') for attack in attack_counts.index]

    fig = go.Figure(go.Pie(
        labels=attack_counts.index,
        values=attack_counts.values,
        marker_colors=colors,
        hole=0.4,
        textinfo='percent+label',
        textposition='outside'
    ))

    fig.update_layout(
        title='Attack Types Distribution',
        template='plotly_dark',
        height=400,
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig


def create_groups_chart(
    df: pd.DataFrame,
    top_n: int = 20
) -> go.Figure:
    """
    Create a horizontal bar chart of top perpetrator groups.

    Args:
        df: Filtered GTD dataframe
        top_n: Number of groups to show

    Returns:
        Plotly figure object
    """
    # Filter out unknown groups
    known_groups = df[~df['gname'].isin(['Unknown', 'unknown', ''])]
    group_counts = known_groups['gname'].value_counts().head(top_n).sort_values()

    fig = go.Figure(go.Bar(
        x=group_counts.values,
        y=group_counts.index,
        orientation='h',
        marker_color='#377eb8'
    ))

    fig.update_layout(
        title=f'Top {top_n} Perpetrator Groups',
        xaxis_title='Number of Incidents',
        yaxis_title='',
        template='plotly_dark',
        height=max(400, top_n * 25),
        margin=dict(l=250, r=40, t=50, b=40)
    )

    return fig


def create_region_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a bar chart of incidents by region.

    Args:
        df: Filtered GTD dataframe

    Returns:
        Plotly figure object
    """
    region_counts = df['region_txt'].value_counts().sort_values(ascending=True)

    colors = [REGION_COLORS.get(region, '#999999') for region in region_counts.index]

    fig = go.Figure(go.Bar(
        x=region_counts.values,
        y=region_counts.index,
        orientation='h',
        marker_color=colors
    ))

    fig.update_layout(
        title='Incidents by Region',
        xaxis_title='Number of Incidents',
        yaxis_title='',
        template='plotly_dark',
        height=400,
        margin=dict(l=200, r=40, t=50, b=40)
    )

    return fig


def create_group_timeline_chart(
    df: pd.DataFrame,
    group_name: str
) -> go.Figure:
    """
    Create a timeline chart for a specific group's activity.

    Args:
        df: Full GTD dataframe
        group_name: Name of the perpetrator group

    Returns:
        Plotly figure object
    """
    group_data = df[df['gname'] == group_name]
    yearly = group_data.groupby('iyear').agg({
        'eventid': 'count',
        'nkill': 'sum'
    }).reset_index()
    yearly.columns = ['Year', 'Incidents', 'Killed']

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=yearly['Year'],
        y=yearly['Incidents'],
        name='Incidents',
        marker_color='#377eb8'
    ))

    fig.add_trace(go.Scatter(
        x=yearly['Year'],
        y=yearly['Killed'],
        name='Killed',
        mode='lines+markers',
        yaxis='y2',
        line=dict(color='#e41a1c', width=2)
    ))

    fig.update_layout(
        title=f'{group_name} - Activity Over Time',
        xaxis_title='Year',
        yaxis=dict(title='Incidents', side='left'),
        yaxis2=dict(title='Killed', side='right', overlaying='y'),
        template='plotly_dark',
        height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=60, r=60, t=80, b=40)
    )

    return fig


def create_decade_comparison_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a chart comparing incidents across decades.

    Args:
        df: Filtered GTD dataframe

    Returns:
        Plotly figure object
    """
    df = df.copy()
    df['decade'] = (df['iyear'] // 10) * 10
    df['decade_label'] = df['decade'].astype(str) + 's'

    decade_stats = df.groupby('decade_label').agg({
        'eventid': 'count',
        'nkill': 'sum',
        'nwound': 'sum'
    }).reset_index()
    decade_stats.columns = ['Decade', 'Incidents', 'Killed', 'Wounded']

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=decade_stats['Decade'],
        y=decade_stats['Incidents'],
        name='Incidents',
        marker_color='#377eb8'
    ))

    fig.update_layout(
        title='Incidents by Decade',
        xaxis_title='Decade',
        yaxis_title='Number of Incidents',
        template='plotly_dark',
        height=350,
        margin=dict(l=60, r=40, t=50, b=40)
    )

    return fig


def create_animated_scatter_geo(df: pd.DataFrame) -> go.Figure:
    """
    Create an animated scatter geo visualization.

    Args:
        df: GTD dataframe with latitude/longitude

    Returns:
        Plotly figure object
    """
    # Aggregate by year and region for animation
    yearly_region = df.groupby(['iyear', 'region_txt']).agg({
        'eventid': 'count',
        'latitude': 'mean',
        'longitude': 'mean',
        'nkill': 'sum'
    }).reset_index()
    yearly_region.columns = ['Year', 'Region', 'Incidents', 'Latitude', 'Longitude', 'Killed']

    fig = px.scatter_geo(
        yearly_region,
        lat='Latitude',
        lon='Longitude',
        size='Incidents',
        color='Region',
        animation_frame='Year',
        hover_name='Region',
        hover_data={'Incidents': True, 'Killed': True},
        projection='natural earth',
        color_discrete_map=REGION_COLORS,
        size_max=50
    )

    fig.update_layout(
        title='Global Terrorism Spread Over Time',
        template='plotly_dark',
        height=600,
        geo=dict(
            showland=True,
            landcolor='rgb(40, 40, 40)',
            countrycolor='rgb(60, 60, 60)',
            oceancolor='rgb(20, 20, 30)',
            showocean=True
        )
    )

    return fig


def create_choropleth_animation(df: pd.DataFrame) -> go.Figure:
    """
    Create an animated choropleth map showing country-level incident counts.

    Args:
        df: GTD dataframe

    Returns:
        Plotly figure object
    """
    # Country name to ISO code mapping (simplified)
    country_mapping = {
        'United States': 'USA',
        'United Kingdom': 'GBR',
        'Russia': 'RUS',
        'Germany': 'DEU',
        'France': 'FRA',
        'Spain': 'ESP',
        'Italy': 'ITA',
        'Iraq': 'IRQ',
        'Afghanistan': 'AFG',
        'Pakistan': 'PAK',
        'India': 'IND',
        'Colombia': 'COL',
        'Peru': 'PER',
        'Philippines': 'PHL',
        'Nigeria': 'NGA',
        'Somalia': 'SOM',
        'Syria': 'SYR',
        'Turkey': 'TUR',
        'Israel': 'ISR',
        'Egypt': 'EGY',
        'Algeria': 'DZA',
        'Thailand': 'THA',
        'Yemen': 'YEM',
        'Libya': 'LBY',
        'Sudan': 'SDN',
        'Bangladesh': 'BGD',
        'Sri Lanka': 'LKA',
        'Nepal': 'NPL',
        'El Salvador': 'SLV',
        'Guatemala': 'GTM',
        'Nicaragua': 'NIC',
        'Mexico': 'MEX',
        'Brazil': 'BRA',
        'Argentina': 'ARG',
        'Chile': 'CHL',
        'Greece': 'GRC',
        'Northern Ireland': 'GBR',
        'South Africa': 'ZAF',
        'Kenya': 'KEN',
        'Democratic Republic of the Congo': 'COD',
        'Cameroon': 'CMR',
        'Mali': 'MLI',
        'Niger': 'NER',
        'Burkina Faso': 'BFA',
        'Central African Republic': 'CAF',
        'Chad': 'TCD',
        'Ukraine': 'UKR',
        'Lebanon': 'LBN',
        'Iran': 'IRN',
        'Saudi Arabia': 'SAU',
        'Indonesia': 'IDN',
        'Myanmar': 'MMR'
    }

    # Add ISO codes
    df_copy = df.copy()
    df_copy['iso_alpha'] = df_copy['country_txt'].map(country_mapping)

    # Aggregate by year and country
    yearly_country = df_copy.groupby(['iyear', 'country_txt', 'iso_alpha']).agg({
        'eventid': 'count'
    }).reset_index()
    yearly_country.columns = ['Year', 'Country', 'ISO', 'Incidents']

    # Filter to countries with ISO codes
    yearly_country = yearly_country.dropna(subset=['ISO'])

    fig = px.choropleth(
        yearly_country,
        locations='ISO',
        color='Incidents',
        animation_frame='Year',
        hover_name='Country',
        color_continuous_scale='Reds',
        range_color=[0, yearly_country['Incidents'].quantile(0.95)]
    )

    fig.update_layout(
        title='Terrorist Incidents by Country Over Time',
        template='plotly_dark',
        height=600,
        geo=dict(
            showland=True,
            landcolor='rgb(40, 40, 40)',
            countrycolor='rgb(60, 60, 60)'
        )
    )

    return fig
