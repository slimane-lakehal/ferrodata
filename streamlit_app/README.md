# Ferrodata - SNCF Train Punctuality Analytics

Interactive Streamlit dashboard for analyzing French railway performance across TGV, TER, and Intercités services.

## 🎯 Features

- 🏠 **Executive Dashboard** - KPIs, trends, and performance overview
- 🗺️ **Interactive Station Map** - PyDeck visualization of all stations
- 🚄 **Route Explorer** - Compare routes and analyze historical performance
- 🔍 **Delay Analysis** - TGV delay cause breakdown and insights
- 📊 **Real-time Analytics** - Powered by dbt + DuckDB pipeline

## 🚀 Quick Start

```bash
# Navigate to app directory
cd streamlit_app

# Install dependencies with uv
uv sync

# Run the application
uv run streamlit run main.py

# Or use streamlit directly
streamlit run main.py
```

## 📁 Project Structure

```
streamlit_app/
├── main.py                          # Application entry point
├── pyproject.toml                   # Dependencies and metadata
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── src/
│   └── ferrodata_delays_analysis/
│       ├── pages/                  # Application pages
│       │   ├── 1_home.py          # Executive dashboard
│       │   ├── 4_station_map.py   # Interactive map
│       │   ├── 5_route_explorer.py # Route analysis
│       │   └── 6_delay_analysis.py # Delay causes
│       ├── components/             # Reusable components
│       │   ├── footer.py
│       │   └── charts.py
│       └── utils/                  # Utility functions
│           ├── database.py         # DuckDB connection
│           └── helpers.py
└── static/                         # Static assets
```

## 🎨 Technology Stack

- **Streamlit** - Interactive web framework
- **DuckDB** - Embedded analytics database
- **dbt** - Data transformation pipeline
- **PyDeck** - WebGL-powered map visualizations
- **Plotly** - Interactive charts and graphs
- **uv** - Fast Python package manager

## 📊 Data Pipeline

The app connects to analytics tables built by dbt:

- `dim_stations` - Station master dimension
- `fct_train_punctuality` - Unified punctuality metrics
- `fct_tgv_delays_by_cause` - Delay attribution
- `agg_monthly_service_performance` - Monthly trends
- `agg_route_performance` - Route-level analytics
- `agg_station_performance` - Station metrics

## 🔧 Configuration

### Theme

Default theme is configured in `.streamlit/config.toml`. Modify as needed:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
```

### Adding Pages

Create new pages in `src/ferrodata_delays_analysis/pages/` following the naming pattern.
Pages are automatically registered in `main.py`.

## 🐍 Requirements

- Python 3.12+
- Streamlit 1.28.0+
- DuckDB 1.0.0+
- PyDeck 0.8.1+

## 👨‍💻 Credits

**Author:** Slimane Lakehal - lakehalslimane@gmail.com

**Template:** Based on Gaël Penessot's modern Streamlit template
🔗 [GitHub](https://github.com/gpenessot)

**Data Source:** SNCF Open Data
🔗 [https://ressources.data.sncf.com/](https://ressources.data.sncf.com/)

## 📝 License

MIT

---

⭐ Built with Streamlit + dbt + DuckDB
