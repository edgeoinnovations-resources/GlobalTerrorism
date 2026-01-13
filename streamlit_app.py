"""
Global Terrorism Database (GTD) Interactive Dashboard

Main entry point for the Streamlit application.
"""

import streamlit as st

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


def main():
    """Main application entry point."""
    # Header
    st.markdown('<p class="main-header">Global Terrorism Database</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive Visualization Suite (1970-2020)</p>', unsafe_allow_html=True)

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

        - **Dashboard**: Interactive 3D map with incident density, KPIs, and trend charts
        - **Timeline**: Animated visualizations showing terrorism spread over time
        - **Groups**: Analysis of perpetrator groups and their activities
        - **About**: Data source information and methodology

        **Use the filters in the sidebar** to focus on specific:
        - Time periods (years)
        - Geographic regions
        - Attack types
        - Target types
        """)

    with col2:
        st.markdown("""
        ### Quick Stats

        The GTD contains information on:
        - **210,000+** terrorist incidents
        - **50 years** of data (1970-2020)
        - **200+** countries
        - **3,500+** perpetrator groups

        Use the pages in the sidebar to explore the data interactively.
        """)

    st.markdown("---")

    # Feature cards
    st.markdown("### Dashboard Features")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        #### Interactive Maps
        3D hexagon density maps and scatterplot visualizations with full pan/zoom support.
        """)

    with col2:
        st.markdown("""
        #### Time Analysis
        Animated timelines showing the spread and evolution of terrorism over 50 years.
        """)

    with col3:
        st.markdown("""
        #### Group Analysis
        Detailed breakdowns of perpetrator groups, their methods, and geographic focus.
        """)

    with col4:
        st.markdown("""
        #### Dynamic Filtering
        Real-time filtering by region, attack type, time period, and more.
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
