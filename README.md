# Ferrodata

French railway analytics platform built on SNCF open data. Ingests train performance metrics, transforms them with dbt, and provides an interactive dashboard for analysis.

## Project Structure

```
ferrodata/
├── ingestion/          # Data pipeline (fetch from SNCF API, load to DuckDB)
├── ferrodata/          # dbt project (data transformation and modeling)
├── streamlit_app/      # Interactive dashboard
├── data/               # Raw data cache
├── ferrodata.duckdb    # Local database (gitignored)
└── pyproject.toml      # UV workspace configuration
```

## Architecture

1. **Ingestion**: Python scripts fetch data from SNCF Open Data API and load into DuckDB
2. **Transformation**: dbt models clean, transform, and build analytics tables
3. **Visualization**: Streamlit app queries DuckDB and renders interactive charts

## Data Sources

All data from [SNCF Open Data](https://ressources.data.sncf.com/):

- TGV punctuality by route (monthly, 2018-present)
- Intercites punctuality by route (monthly, 2014-present)
- TER punctuality by region (monthly, 2013-present)
- Station master list (network metadata)

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- [dbt](https://www.getdbt.com/) installed globally or via pipx

### Installation

```bash
# Clone repository
git clone <repository-url>
cd ferrodata

# Install dependencies (UV workspace)
uv sync

# Install dbt packages
cd ferrodata
dbtf deps
cd ..
```

### Environment Variables

Create `.env` files in each workspace if needed:

```bash
# ingestion/.env (optional - for BigQuery target)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GCP_PROJECT_ID=your-project-id

# ferrodata/.env (dbt profile if using BigQuery)
DBT_BIGQUERY_PROJECT=your-project-id
DBT_BIGQUERY_DATASET=your-dataset
```

## Usage

### 1. Ingest Data

Fetch data from SNCF API and load into DuckDB:

```bash
# Run from project root
uv run --package ferrodata-ingestion ferrodata-ingest
```

This creates `ferrodata.duckdb` with raw data in the `raw_sncf` schema.

### 2. Transform Data

Run dbt models to build staging and analytics tables:

```bash
cd ferrodata

# Run all models
dbt run

# Run specific model
dbt run --select stg_sncf__regularite_tgv

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

Output schemas:
- `analytics_staging`: Cleaned source data
- `analytics_analytics`: Marts and aggregations

### 3. Launch Dashboard

Start the Streamlit app:

```bash
# From project root
cd streamlit_app
uv run streamlit run Home.py

# Or using the streamlit command directly
streamlit run streamlit_app/Home.py
```

Access at http://localhost:8501

## dbt Models

### Staging

Cleaned and typed source data:

- `stg_sncf__gares`: Station master list
- `stg_sncf__regularite_tgv`: TGV punctuality
- `stg_sncf__regularite_intercites`: Intercites punctuality
- `stg_sncf__regularite_ter`: TER regional punctuality

### Marts

Analytics-ready tables:

- `dim_stations`: Station dimension with geography and service metadata
- `fct_train_punctuality`: Unified punctuality metrics across all services
- `fct_tgv_delays_by_cause`: Delay cause analysis for TGV
- `agg_monthly_service_performance`: Monthly trends by service type
- `agg_station_performance`: Station-level performance metrics
- `agg_route_performance`: Route-level performance ratings

## Dashboard Pages

- **Home**: Overview metrics and trends
- **Station Map**: Interactive map of all stations
- **Route Analysis**: Performance by origin-destination pair
- **Delay Causes**: Deep dive into delay attribution (TGV only)

## Development

### Code Quality

```bash
# Lint with ruff
uv run ruff check .

# Format
uv run ruff format .

# Run tests
uv run pytest
```

### Database Targets

The project supports both DuckDB (local) and BigQuery (cloud):

**DuckDB** (default):
- Fast local development
- No credentials needed
- Single-file database

**BigQuery**:
- Production-ready
- Requires GCP credentials
- Set `target: bigquery` in `ferrodata/profiles.yml`

## Cross-Database Compatibility

Models use dbt macros for database portability:

```sql
-- Instead of date_diff() or datediff()
{{ dbt.datediff("start_date", "end_date", "day") }}

-- Instead of current_timestamp()
{{ dbt.current_timestamp() }}

-- And more: dateadd, date_trunc, concat, split_part, etc.
```

## Troubleshooting

### Ingestion fails with 404

Check SNCF API status or update URLs in `ingestion/config.py`

### dbt can't find database

Ensure `ferrodata.duckdb` exists in project root after running ingestion

### Streamlit map not showing

- Check DuckDB file path in `streamlit_app/utils/db.py`
- Verify `dim_stations` table exists with lat/lon data
- Try clearing cache: Settings > Clear Cache

## License

MIT

## Author

Slimane Lakehal
