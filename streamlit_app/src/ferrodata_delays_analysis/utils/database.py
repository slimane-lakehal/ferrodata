"""Database connection utilities — DuckDB (dev) or BigQuery (Streamlit Cloud)."""

from pathlib import Path

import pandas as pd
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

# ---------------------------------------------------------------------------
# Backend detection
# ---------------------------------------------------------------------------


def _is_cloud() -> bool:
    """Return True when GCP credentials are present in Streamlit secrets."""
    try:
        return "gcp_service_account" in st.secrets
    except FileNotFoundError:
        return False


# Schema where dbt mart tables live in each backend:
#   DuckDB  → target schema "analytics" + custom "analytics" = "analytics_analytics"
#   BigQuery → target dataset "sncf"    + custom "analytics" = "sncf_analytics"
MART_SCHEMA = "sncf_analytics" if _is_cloud() else "analytics_analytics"


# ---------------------------------------------------------------------------
# Connections
# ---------------------------------------------------------------------------


@st.cache_resource
def _get_bq_client() -> bigquery.Client:
    sa_info = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(sa_info)
    return bigquery.Client(credentials=credentials, project=sa_info["project_id"])


def _get_duckdb():
    import duckdb

    db_path = Path(__file__).parent.parent.parent.parent.parent / "ferrodata.duckdb"
    if not db_path.exists():
        st.error(f"❌ Database not found at: {db_path}")
        st.stop()
    try:
        return duckdb.connect(str(db_path), read_only=True)
    except Exception as e:
        st.error(f"❌ Failed to connect to DuckDB: {e}")
        st.stop()


# ---------------------------------------------------------------------------
# Query execution
# ---------------------------------------------------------------------------


@st.cache_data(ttl=300)
def query_data(query: str) -> pd.DataFrame:
    """
    Execute a SQL query against the active backend and return a DataFrame.

    Uses BigQuery on Streamlit Cloud (when gcp_service_account is in secrets),
    DuckDB otherwise.
    """
    if _is_cloud():
        try:
            return _get_bq_client().query(query, location="EU").to_dataframe()
        except Exception as e:
            st.error(f"❌ BigQuery error: {type(e).__name__}: {e}")
            with st.expander("🔍 Query"):
                st.code(query, language="sql")
            return pd.DataFrame()
    else:
        try:
            conn = _get_duckdb()
            return conn.execute(query).df()
        except Exception as e:
            st.error(f"❌ DuckDB error: {type(e).__name__}: {e}")
            with st.expander("🔍 Query"):
                st.code(query, language="sql")
            return pd.DataFrame()


# ---------------------------------------------------------------------------
# Domain helpers
# ---------------------------------------------------------------------------


@st.cache_data(ttl=3600)
def get_available_date_range() -> tuple:
    query = f"""
    SELECT
        MIN(date) as min_date,
        MAX(date) as max_date
    FROM {MART_SCHEMA}.fct_train_punctuality
    """
    result = query_data(query)
    if not result.empty:
        return (result["min_date"].iloc[0], result["max_date"].iloc[0])
    return (None, None)


@st.cache_data(ttl=3600)
def get_service_types() -> list:
    query = f"""
    SELECT DISTINCT service_type
    FROM {MART_SCHEMA}.fct_train_punctuality
    ORDER BY service_type
    """
    result = query_data(query)
    if not result.empty:
        return result["service_type"].tolist()
    return []


@st.cache_data(ttl=3600)
def get_all_stations() -> pd.DataFrame:
    query = f"""
    SELECT
        station_id,
        station_name,
        city,
        department,
        longitude,
        latitude,
        station_tier,
        has_passenger_service,
        total_trains_handled
    FROM {MART_SCHEMA}.dim_stations
    WHERE has_passenger_service = true
        AND longitude IS NOT NULL
        AND latitude IS NOT NULL
    ORDER BY total_trains_handled DESC
    """
    return query_data(query)


@st.cache_data(ttl=3600)
def get_all_routes() -> list:
    query = f"""
    SELECT DISTINCT route
    FROM {MART_SCHEMA}.agg_route_performance
    ORDER BY route
    """
    result = query_data(query)
    if not result.empty:
        return result["route"].tolist()
    return []


def test_connection() -> bool:
    try:
        if _is_cloud():
            result = _get_bq_client().query("SELECT 1 AS test", location="EU").result()
            print("BigQuery connection successful")
            return True if result else False
        else:
            conn = _get_duckdb()
            print("DuckDB connection successful")
            return conn.execute("SELECT 1 AS test").fetchone()[0] == 1
    except Exception:
        return False


if __name__ == "__main__":
    print(test_connection())
    print(MART_SCHEMA)