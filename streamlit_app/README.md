# 🚄 SNCF Train Punctuality Analytics - Streamlit App

Interactive dashboard for analyzing French train punctuality data across TGV, TER, and Intercités services.

## Features

### 📊 Main Dashboard (`app.py`)
- Executive summary with KPIs
- Punctuality and cancellation trends
- Service type comparison
- Best/worst performing routes

### 🗺️ Station Map (`pages/1_🗺️_Station_Map.py`)
- Interactive map of all French train stations
- Color-coded by station tier
- Sized by train volume
- Filterable by tier and traffic
- Searchable station details

### 🚄 Route Explorer (`pages/2_🚄_Route_Explorer.py`)
- Compare up to 5 routes side-by-side
- Historical performance trends
- Seasonal pattern analysis
- Detailed route metrics

### 🔍 Delay Analysis (`pages/3_🔍_Delay_Analysis.py`)
- Root cause breakdown for TGV delays
- 6 delay categories analyzed
- Time series trends
- Route-specific filtering

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Or use the provided script
./run.sh
```

The app will be available at http://localhost:8501

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Docker (manual)

```bash
# Build image
docker build -t sncf-analytics .

# Run container
docker run -p 8501:8501 \
  -v $(pwd)/../ferrodata.duckdb:/app/ferrodata.duckdb:ro \
  sncf-analytics
```

## Configuration

### Database Connection

The app expects to find `ferrodata.duckdb` in the parent directory (`../ferrodata.duckdb`).

To change the database path, edit `utils/db.py`:

```python
db_path = Path(__file__).parent.parent.parent / "ferrodata.duckdb"
```

### Streamlit Config

Customize appearance and behavior in `.streamlit/config.toml`:
- Theme colors
- Server port
- Upload limits
- Browser settings

## Project Structure

```
streamlit_app/
├── app.py                    # Main dashboard
├── pages/
│   ├── 1_🗺️_Station_Map.py
│   ├── 2_🚄_Route_Explorer.py
│   └── 3_🔍_Delay_Analysis.py
├── utils/
│   ├── __init__.py
│   ├── db.py                 # Database utilities
│   └── charts.py             # Chart components
├── .streamlit/
│   └── config.toml           # Streamlit configuration
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Data Sources

This app visualizes data from the **dbt analytics layer**:

- `dim_stations` - Station master data
- `fct_train_punctuality` - Unified punctuality facts
- `fct_tgv_delays_by_cause` - TGV delay root causes
- `agg_monthly_service_performance` - Monthly aggregations
- `agg_station_performance` - Station-level metrics
- `agg_route_performance` - Route-level metrics

All data sourced from [SNCF Open Data](https://ressources.data.sncf.com/).

## Performance

### Caching Strategy

The app uses Streamlit's caching decorators for optimal performance:

- `@st.cache_resource` - Database connections (persistent)
- `@st.cache_data(ttl=300)` - Query results (5-minute TTL)
- `@st.cache_data(ttl=3600)` - Reference data (1-hour TTL)

### Query Optimization

- Read-only database connection
- Pre-aggregated marts reduce query complexity
- Indexed columns for fast filtering

## Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Connect repository to [Streamlit Cloud](https://streamlit.io/cloud)
3. Upload `ferrodata.duckdb` as a data source
4. Deploy!

### Self-Hosted

Use Docker Compose for production deployments:

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

Consider:
- Reverse proxy (nginx) for SSL/TLS
- Load balancer for high traffic
- Database on separate volume/service
- Automated dbt pipeline to refresh data

## Troubleshooting

### Database Not Found

```
❌ Database not found at: /path/to/ferrodata.duckdb
```

**Solution:** Ensure `ferrodata.duckdb` exists and the path in `utils/db.py` is correct.

### Query Errors

```
❌ Query failed: Binder Error: Referenced column not found
```

**Solution:** Run `dbt run` to ensure all mart models are up to date.

### Slow Performance

- Check cache TTL settings in `utils/db.py`
- Verify database is on fast storage (SSD)
- Consider pre-aggregating more data in dbt

## Development

### Adding New Pages

1. Create new file: `pages/4_🎯_New_Page.py`
2. Follow naming convention: `{number}_{emoji}_{Name}.py`
3. Import utilities: `from utils.db import query_data`
4. Use consistent layout and styling

### Custom Queries

Add reusable queries to `utils/db.py`:

```python
@st.cache_data(ttl=3600)
def get_custom_metric():
    conn = get_db()
    query = "SELECT ..."
    return query_data(conn, query)
```

## License

This project uses SNCF Open Data which is available under Open License.

## Support

For issues or questions:
- Check dbt docs: `dbt docs serve`
- Review data lineage in dbt documentation
- Verify source data freshness: `dbt source freshness`

---

Built with ❤️ using Streamlit + dbt + DuckDB
