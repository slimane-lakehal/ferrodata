"""Database connection utilities — DuckDB (dev) or BigQuery (Streamlit Cloud)."""

from pathlib import Path

import pandas as pd
import streamlit as st


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
_MART_SCHEMA = "sncf_analytics" if _is_cloud() else "analytics_analytics"


# ---------------------------------------------------------------------------
# Connections
# ---------------------------------------------------------------------------

@st.cache_resource
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


def _get_bq():
    return st.connection("bigquery", type="bigquery")


# ---------------------------------------------------------------------------
# Query execution
# ---------------------------------------------------------------------------

@st.cache_data(ttl=300)
def query_data_cached(_conn, query: str) -> pd.DataFrame:
    """Execute a SQL query against DuckDB and return a DataFrame."""
    try:
        return _conn.execute(query).df()
    except Exception as e:
        st.error(f"❌ Query failed: {e}")
        with st.expander("🔍 View failed query"):
            st.code(query, language="sql")
        return pd.DataFrame()


def query_data(query: str, ttl: int = 300) -> pd.DataFrame:
    """
    Execute a SQL query against the active backend and return a DataFrame.

    Uses BigQuery on Streamlit Cloud (when gcp_service_account is in secrets),
    DuckDB otherwise.
    """
    if _is_cloud():
        try:
            return _get_bq().query(query, ttl=ttl)
        except Exception as e:
            st.error(f"❌ BigQuery query failed: {e}")
            with st.expander("🔍 View failed query"):
                st.code(query, language="sql")
            return pd.DataFrame()
    else:
        conn = _get_duckdb()
        return query_data_cached(conn, query)


# ---------------------------------------------------------------------------
# Domain helpers
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600)
def get_available_date_range() -> tuple:
    query = f"""
    SELECT
        MIN(date) as min_date,
        MAX(date) as max_date
    FROM {_MART_SCHEMA}.fct_train_punctuality
    """
    result = query_data(query, ttl=3600)
    if not result.empty:
        return (result["min_date"].iloc[0], result["max_date"].iloc[0])
    return (None, None)


@st.cache_data(ttl=3600)
def get_service_types() -> list:
    query = f"""
    SELECT DISTINCT service_type
    FROM {_MART_SCHEMA}.fct_train_punctuality
    ORDER BY service_type
    """
    result = query_data(query, ttl=3600)
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
    FROM {_MART_SCHEMA}.dim_stations
    WHERE has_passenger_service = true
        AND longitude IS NOT NULL
        AND latitude IS NOT NULL
    ORDER BY total_trains_handled DESC
    """
    return query_data(query, ttl=3600)


@st.cache_data(ttl=3600)
def get_all_routes() -> list:
    query = f"""
    SELECT DISTINCT route
    FROM {_MART_SCHEMA}.agg_route_performance
    ORDER BY route
    """
    result = query_data(query, ttl=3600)
    if not result.empty:
        return result["route"].tolist()
    return []


def test_connection() -> bool:
    try:
        if _is_cloud():
            result = _get_bq().query("SELECT 1 AS test", ttl=0)
            return not result.empty
        else:
            conn = _get_duckdb()
            return conn.execute("SELECT 1 AS test").fetchone()[0] == 1
    except Exception:
        return False
