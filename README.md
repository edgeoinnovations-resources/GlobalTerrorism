# Global Terrorism Database (GTD) Visualization Suite

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://globalterrorism.streamlit.app)

An interactive geospatial visualization suite for exploring the Global Terrorism Database (GTD), containing ~210,000 terrorist incidents from 1970-2020.

![Dashboard Preview](assets/dashboard_preview.png)

## Features

- **Interactive 3D Maps**: PyDeck HexagonLayer visualization showing incident density with full pan/zoom/rotate support
- **Animated Timelines**: Watch terrorism spread across the globe over 50 years
- **Group Analysis**: Deep-dive into perpetrator organizations, their methods, and geographic focus
- **Multi-filter Dashboard**: Filter by year, region, attack type, target type, and more
- **High-Performance Rendering**: Lonboard GPU-accelerated visualization of 200K+ points
- **KeplerGL Exploration**: Full-featured interactive exploration with time animation

## Quick Start

### Prerequisites

- Python 3.9+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/edgeoinnovations-resources/GlobalTerrorism.git
   cd GlobalTerrorism
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Obtain the GTD data**

   Download the Global Terrorism Database from [START](https://www.start.umd.edu/gtd/contact/) and place the Excel file in the project root directory.

4. **Run preprocessing**
   ```bash
   python scripts/preprocess_data.py
   ```

5. **Launch the dashboard**
   ```bash
   streamlit run streamlit_app.py
   ```

## Project Structure

```
GlobalTerrorism/
├── streamlit_app.py              # Main Streamlit entry point
├── pages/
│   ├── 1_🗺️_Dashboard.py        # Interactive dashboard with 3D map
│   ├── 2_📈_Timeline.py          # Animated timeline visualizations
│   ├── 3_👥_Groups.py            # Perpetrator group analysis
│   └── 4_ℹ️_About.py             # Data source and methodology
├── notebooks/
│   ├── 01_data_preprocessing.ipynb   # Data cleaning notebook
│   ├── 02_kepler_exploration.ipynb   # KeplerGL interactive maps
│   ├── 03_lonboard_performance.ipynb # High-performance visualization
│   └── 04_plotly_animations.ipynb    # Animated Plotly charts
├── scripts/
│   └── preprocess_data.py        # Standalone preprocessing script
├── utils/
│   ├── data_loader.py            # Cached data loading
│   ├── charts.py                 # Reusable chart components
│   └── maps.py                   # Map layer configurations
├── config/
│   ├── kepler_config.json        # KeplerGL map configuration
│   └── color_schemes.py          # Consistent color palettes
├── exports/                      # Generated HTML visualizations
├── data/
│   └── processed/                # Parquet files (gitignored)
└── .streamlit/
    └── config.toml               # Streamlit theme configuration
```

## Components

### Streamlit Dashboard

A multi-page interactive dashboard with:
- **Dashboard**: KPIs, 3D hexagon map, trend charts, and data table
- **Timeline**: Animated scatter_geo and regional trend analysis
- **Groups**: Perpetrator statistics, timelines, and attack preferences
- **About**: Data source information and methodology

### Jupyter Notebooks

1. **Data Preprocessing** (`01_data_preprocessing.ipynb`)
   - Loads and cleans the GTD Excel file
   - Creates proper datetime columns
   - Exports to efficient Parquet format

2. **KeplerGL Exploration** (`02_kepler_exploration.ipynb`)
   - Interactive web-based map exploration
   - Time animation with year slider
   - Multiple layer types (points, hexbin, heatmap)

3. **Lonboard Performance** (`03_lonboard_performance.ipynb`)
   - GPU-accelerated rendering of 200K+ points
   - Color-coded by attack type
   - Size-scaled by casualties

4. **Plotly Animations** (`04_plotly_animations.ipynb`)
   - Animated scatter_geo by region
   - Animated choropleth by country
   - Regional trend analysis

### HTML Exports

Static HTML files in `exports/`:
- `gtd_kepler_interactive.html` - Full KeplerGL interface
- `gtd_lonboard_map.html` - High-performance point map
- `gtd_timeline_animation.html` - Animated regional spread
- `gtd_choropleth_animation.html` - Country-level animation
- `gtd_pydeck_3d.html` - 3D hexagon visualization

## Data Source

This project visualizes data from the **Global Terrorism Database (GTD)**, maintained by the **National Consortium for the Study of Terrorism and Responses to Terrorism (START)** at the University of Maryland.

> The GTD defines a terrorist attack as the threatened or actual use of illegal force and violence by a non-state actor to attain a political, economic, religious, or social goal through fear, coercion, or intimidation.

**Citation:**
```
National Consortium for the Study of Terrorism and Responses to Terrorism (START).
(2022). Global Terrorism Database 1970-2020 [Data set].
University of Maryland. https://www.start.umd.edu/gtd
```

## Configuration

### Environment Variables

Create a `.env` file with your Mapbox token:
```
MAPBOX_TOKEN=your_mapbox_token_here
```

### Streamlit Secrets

For Streamlit Cloud deployment, add to `.streamlit/secrets.toml`:
```toml
MAPBOX_TOKEN = "your_mapbox_token_here"
```

## Deployment

### Streamlit Community Cloud

1. Push to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set secrets in the Streamlit dashboard
5. Deploy!

**Note**: The processed Parquet file is too large for GitHub. For cloud deployment, either:
- Use GitHub LFS
- Host data on external storage (S3, GCS)
- Provide a data download script

## Technologies

- **[Streamlit](https://streamlit.io/)** - Interactive dashboard framework
- **[PyDeck](https://pydeck.gl/)** - WebGL map visualizations
- **[Plotly](https://plotly.com/)** - Interactive charts
- **[KeplerGL](https://kepler.gl/)** - Geospatial data exploration
- **[Lonboard](https://github.com/developmentseed/lonboard)** - High-performance maps
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation
- **[PyArrow](https://arrow.apache.org/docs/python/)** - Efficient data storage

## License

This project is for educational and research purposes. The GTD data is subject to [START's terms of use](https://www.start.umd.edu/gtd/terms-of-use/).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [START](https://www.start.umd.edu/) for maintaining the Global Terrorism Database
- The open-source geospatial Python community
