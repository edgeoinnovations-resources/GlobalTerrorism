"""
Global Terrorism Database (GTD) Interactive Dashboard

Main entry point for the Streamlit application.
"""

import streamlit as st
from pathlib import Path
import pandas as pd

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Global Terrorism Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/edgeoinnovations-resources/GlobalTerrorism',
        'Report a bug': 'https://github.com/edgeoinnovations-resources/GlobalTerrorism/issues',
        'About': """
        # Global Terrorism Database Visualization

        This dashboard provides interactive visualizations of the Global Terrorism Database (GTD),
        maintained by the National Consortium for the Study of Terrorism and Responses to Terrorism (START).

        **Data Range:** 1970-2020
        **Incidents:** ~210,000
        """
    }
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #e41a1c;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #999;
        margin-top: 0;
    }
    .metric-card {
        background-color: #262730;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .stMetric {
        background-color: #262730;
        border-radius: 10px;
        padding: 15px;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_summary():
    """Load summary statistics from the data."""
    data_path = Path("data/processed/gtd_processed.parquet")
    if data_path.exists():
        df = pd.read_parquet(data_path)
        return {
            'incidents': len(df),
            'countries': df['country_txt'].nunique(),
            'years': f"{df['iyear'].min()}-{df['iyear'].max()}",
            'groups': df['gname'].nunique() if 'gname' in df.columns else 0,
            'killed': int(df['nkill'].sum()) if 'nkill' in df.columns else 0,
            'wounded': int(df['nwound'].sum()) if 'nwound' in df.columns else 0
        }
    return None


def main():
    """Main application entry point."""
    # Header
    st.markdown('<p class="main-header">🌍 Global Terrorism Database Explorer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive Visualization Suite (1970-2020)</p>', unsafe_allow_html=True)

    st.markdown("---")

    # Load stats
    stats = load_summary()

    # Quick Stats Row
    if stats:
        st.subheader("📊 Database Overview")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Total Incidents", f"{stats['incidents']:,}")
        c2.metric("Countries", stats['countries'])
        c3.metric("Time Span", stats['years'])
        c4.metric("Groups", f"{stats['groups']:,}")
        c5.metric("Total Killed", f"{stats['killed']:,}")
        c6.metric("Total Wounded", f"{stats['wounded']:,}")

        st.markdown("---")

    # Welcome content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        ### Welcome to the GTD Visualization Dashboard

        This dashboard provides comprehensive visualizations of terrorist incidents
        from 1970 to 2020, based on the Global Terrorism Database maintained by
        START (National Consortium for the Study of Terrorism and Responses to Terrorism).

        **Navigate using the sidebar to explore:**

        - 🗺️ **Dashboard** - Overview with 3D maps and key metrics
        - 📈 **Timeline** - Animated temporal analysis with year slider
        - 👥 **Groups** - Perpetrator organization analysis
        - 🔍 **Country Deep Dive** - Detailed country-level exploration
        - ℹ️ **About** - Data sources and methodology

        **Use the filters** to focus on specific time periods, regions, attack types, and more.
        """)

    with col2:
        st.markdown("""
        ### What's New

        **Enhanced Timeline Page:**
        - Year slider controls all visualizations
        - 3D HexagonLayer hotspot map
        - Animated country choropleth
        - Regional stacked area chart
        - Attack type breakdown

        **Country Deep Dive:**
        - Select any country for detailed analysis
        - City-level incident mapping
        - Perpetrator group statistics
        - Decade-by-decade trends
        """)

    st.markdown("---")

    # Feature cards
    st.markdown("### Dashboard Features")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        #### 🗺️ Interactive Maps
        3D hexagon density maps and scatterplot visualizations with full pan/zoom support.
        """)

    with col2:
        st.markdown("""
        #### 📈 Time Analysis
        Animated timelines showing the spread and evolution of terrorism over 50 years.
        """)

    with col3:
        st.markdown("""
        #### 👥 Group Analysis
        Detailed breakdowns of perpetrator groups, their methods, and geographic focus.
        """)

    with col4:
        st.markdown("""
        #### 🔍 Country Drill-Down
        Deep dive into any country with city-level maps and historical trends.
        """)

    st.markdown("---")

    # Data attribution
    st.markdown("""
    ### Data Source

    This visualization uses data from the **Global Terrorism Database (GTD)**,
    an open-source database maintained by the National Consortium for the Study of
    Terrorism and Responses to Terrorism (START) at the University of Maryland.

    *The GTD defines a terrorist attack as the threatened or actual use of illegal force
    and violence by a non-state actor to attain a political, economic, religious, or social
    goal through fear, coercion, or intimidation.*

    [Learn more about GTD](https://www.start.umd.edu/gtd/)
    """)


if __name__ == "__main__":
    main()
