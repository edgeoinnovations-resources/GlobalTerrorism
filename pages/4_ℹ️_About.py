"""
About Page - Data source information and methodology.

Contains:
- Data source information
- GTD coding definitions
- Limitations and caveats
- Links to original data source
"""

import streamlit as st
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_gtd_data

# Page configuration
st.set_page_config(
    page_title="About - GTD",
    page_icon="ℹ️",
    layout="wide"
)

st.title("ℹ️ About This Dashboard")

st.markdown("---")

# Data Source
st.markdown("## Data Source")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    This dashboard visualizes data from the **Global Terrorism Database (GTD)**,
    maintained by the **National Consortium for the Study of Terrorism and Responses
    to Terrorism (START)** at the University of Maryland.

    The GTD is an open-source database that includes information on terrorist events
    around the world from 1970 through 2020 (with annual updates). It is the most
    comprehensive unclassified database on terrorist attacks in the world.

    **Key Features of the GTD:**
    - More than 200,000 cases of domestic and international terrorist attacks
    - Information on more than 88,000 bombings, 19,000 assassinations, and 11,000
      kidnappings since 1970
    - More than 135 variables on location, tactics, perpetrators, targets, and outcomes
    - Includes attacks attributed to more than 3,500 named perpetrator organizations
    """)

with col2:
    st.markdown("""
    ### Quick Links

    - [GTD Official Website](https://www.start.umd.edu/gtd/)
    - [GTD Codebook](https://www.start.umd.edu/gtd/downloads/Codebook.pdf)
    - [START Center](https://www.start.umd.edu/)
    - [Data Download](https://www.start.umd.edu/gtd/contact/)
    """)

st.markdown("---")

# Definition
st.markdown("## GTD Definition of Terrorism")

st.info("""
The GTD defines a terrorist attack as the **threatened or actual use of illegal force
and violence by a non-state actor** to attain a political, economic, religious, or social
goal through fear, coercion, or intimidation.

**To be included in the GTD, an incident must meet all three of the following criteria:**

1. The incident must be intentional
2. The incident must entail some level of violence or immediate threat of violence
3. The perpetrators must be sub-national actors

**Additionally, at least two of the following three criteria must be present:**

1. The act must be aimed at attaining a political, economic, religious, or social goal
2. There must be evidence of an intention to coerce, intimidate, or convey some other
   message to a larger audience than the immediate victims
3. The action must be outside the context of legitimate warfare activities
""")

st.markdown("---")

# Coding Definitions
st.markdown("## Key Variable Definitions")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Attack Types

    | Type | Description |
    |------|-------------|
    | **Assassination** | Deliberate killing of a specific person |
    | **Hijacking** | Taking control of a vehicle (aircraft, boat, bus, etc.) |
    | **Kidnapping** | Taking a person hostage for ransom or political demands |
    | **Barricade Incident** | Hostage-taking where perpetrators barricade themselves |
    | **Bombing/Explosion** | Use of explosive devices |
    | **Armed Assault** | Attack using firearms or incendiary devices |
    | **Unarmed Assault** | Attack without weapons (e.g., chemical/biological agents) |
    | **Facility Attack** | Attack on a building or infrastructure |
    """)

with col2:
    st.markdown("""
    ### Target Types

    | Type | Description |
    |------|-------------|
    | **Business** | Commercial entities |
    | **Government (General)** | Government buildings, officials |
    | **Police** | Law enforcement personnel/facilities |
    | **Military** | Armed forces personnel/facilities |
    | **Abortion Related** | Abortion clinics, staff |
    | **Airports & Airlines** | Aviation infrastructure |
    | **Educational Institution** | Schools, universities |
    | **Private Citizens** | Civilians not affiliated with institutions |
    | **Religious Figures/Institutions** | Churches, mosques, clergy |
    | **Journalists & Media** | News organizations, reporters |
    """)

st.markdown("---")

# Regions
st.markdown("## Geographic Regions")

st.markdown("""
The GTD uses the following regional classifications:

| Region | Countries Included |
|--------|-------------------|
| **North America** | United States, Canada, Mexico |
| **Central America & Caribbean** | Guatemala, Honduras, El Salvador, Nicaragua, etc. |
| **South America** | Brazil, Colombia, Peru, Argentina, Chile, etc. |
| **Western Europe** | UK, France, Germany, Spain, Italy, etc. |
| **Eastern Europe** | Russia, Ukraine, Poland, Czech Republic, etc. |
| **Middle East & North Africa** | Iraq, Syria, Egypt, Israel, Saudi Arabia, etc. |
| **Sub-Saharan Africa** | Nigeria, Somalia, Kenya, South Africa, etc. |
| **South Asia** | India, Pakistan, Afghanistan, Bangladesh, Sri Lanka |
| **Southeast Asia** | Philippines, Thailand, Indonesia, Myanmar, etc. |
| **East Asia** | China, Japan, South Korea, North Korea |
| **Central Asia** | Kazakhstan, Uzbekistan, Tajikistan, etc. |
| **Australasia & Oceania** | Australia, New Zealand, Fiji, etc. |
""")

st.markdown("---")

# Limitations
st.markdown("## Limitations and Caveats")

st.warning("""
**Important considerations when using this data:**

1. **Data Collection Gaps (1993)**: The GTD was compiled from different sources before and
   after 1997, resulting in some inconsistencies. Data for 1993 was lost prior to START's
   compilation of the GTD, so that year is excluded from analysis.

2. **Underreporting**: Some terrorist attacks, especially in conflict zones with limited
   media coverage, may not be captured in the database.

3. **Attribution Uncertainty**: Many attacks are claimed by multiple groups or remain
   unclaimed. The "Unknown" category contains a significant portion of incidents.

4. **Coordinate Precision**: Location data varies in precision. The `specificity` field
   in the original data indicates whether coordinates are approximate.

5. **Casualty Estimates**: Casualty figures (killed/wounded) may be incomplete or
   approximate, especially for historical incidents or those in remote areas.

6. **Definitional Changes**: The criteria for inclusion may have evolved over time,
   affecting comparability across decades.

7. **Data Processing**: This visualization uses a subset of the full GTD columns and
   excludes incidents with missing coordinate data.
""")

st.markdown("---")

# Technical Details
st.markdown("## Technical Details")

# Try to load data stats
try:
    df = load_gtd_data()
    data_loaded = True
except:
    data_loaded = False

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Visualization Tools")
    st.markdown("""
    This dashboard was built using:

    - **Streamlit**: Interactive web application framework
    - **PyDeck**: High-performance WebGL map visualizations
    - **Plotly**: Interactive charts and animated maps
    - **Pandas**: Data processing and analysis
    - **PyArrow/Parquet**: Efficient data storage and loading

    **Additional notebooks available:**
    - KeplerGL interactive exploration
    - Lonboard high-performance rendering
    - Plotly animated timelines
    """)

with col2:
    st.markdown("### Data Statistics")
    if data_loaded:
        st.markdown(f"""
        **Current Dataset:**

        - **Total Incidents:** {len(df):,}
        - **Date Range:** {df['iyear'].min()} - {df['iyear'].max()}
        - **Countries:** {df['country_txt'].nunique()}
        - **Regions:** {df['region_txt'].nunique()}
        - **Perpetrator Groups:** {df['gname'].nunique()}
        - **Attack Types:** {df['attacktype1_txt'].nunique()}
        - **Total Killed:** {df['nkill'].sum():,.0f}
        - **Total Wounded:** {df['nwound'].sum():,.0f}
        """)
    else:
        st.markdown("*Data statistics unavailable - run preprocessing first*")

st.markdown("---")

# Citation
st.markdown("## Citation")

st.code("""
National Consortium for the Study of Terrorism and Responses to Terrorism (START).
(2022). Global Terrorism Database 1970-2020 [Data set].
University of Maryland. https://www.start.umd.edu/gtd
""", language=None)

st.markdown("---")

# Footer
st.markdown("""
### Disclaimer

This dashboard is provided for **educational and research purposes only**.
The visualizations are based on publicly available data from the GTD.
The creators of this dashboard are not affiliated with START or the
University of Maryland.

For official data, methodology, and research, please visit the
[Global Terrorism Database](https://www.start.umd.edu/gtd/) website.
""")
