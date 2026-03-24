"""Database connection utilities for DuckDB."""

import streamlit as st
import duckdb
import pandas as pd
from pathlib import Path


@st.cache_resource
def get_db():
    """
    Get cached DuckDB connection.

    Returns:
        duckdb.DuckDBPyConnection: Database connection
    """
    # Path to DuckDB file (relative to streamlit_app directory)
    db_path = Path(__file__).parent.parent.parent / "ferrodata.duckdb"

    if not db_path.exists():
        st.error(f"❌ Database not found at: {db_path}")
        st.stop()

    try:
        conn = duckdb.connect(str(db_path), read_only=True)
        return conn
    except Exception as e:
        st.error(f"❌ Failed to connect to database: {e}")
        st.stop()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def query_data_cached(_conn, query: str) -> pd.DataFrame:
    """
    Execute SQL query and return results as DataFrame.

    Args:
        _conn: DuckDB connection (prefixed with _ to avoid hashing)
        query: SQL query string

    Returns:
        pd.DataFrame: Query results
    """
    try:
        result = _conn.execute(query).df()
        return result
    except Exception as e:
        st.error(f"❌ Query failed: {e}")
        st.code(query, language="sql")
        return pd.DataFrame()


def query_data(query: str) -> pd.DataFrame:
    """
    Convenience function to execute query with cached connection.

    Args:
        query: SQL query string

    Returns:
        pd.DataFrame: Query results
    """
    conn = get_db()
    return query_data_cached(conn, query)


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_available_date_range() -> tuple:
    """
    Get the min and max dates available in the data.

    Returns:
        tuple: (min_date, max_date)
    """
    query = """
    SELECT
        MIN(date) as min_date,
        MAX(date) as max_date
    FROM analytics_analytics.fct_train_punctuality
    """
    result = query_data(query)

    if not result.empty:
        return (result['min_date'].iloc[0], result['max_date'].iloc[0])
    return (None, None)


@st.cache_data(ttl=3600)
def get_service_types() -> list:
    """
    Get list of available service types.

    Returns:
        list: Service type names
    """
    query = """
    SELECT DISTINCT service_type
    FROM analytics_analytics.fct_train_punctuality
    ORDER BY service_type
    """
    result = query_data(query)

    if not result.empty:
        return result['service_type'].tolist()
    return []


@st.cache_data(ttl=3600)
def get_all_stations() -> pd.DataFrame:
    """
    Get all stations with coordinates.

    Returns:
        pd.DataFrame: Station information
    """
    query = """
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
    FROM analytics_analytics.dim_stations
    WHERE has_passenger_service = true
        AND longitude IS NOT NULL
        AND latitude IS NOT NULL
    ORDER BY total_trains_handled DESC
    """
    return query_data(query)


@st.cache_data(ttl=3600)
def get_all_routes() -> list:
    """
    Get list of all unique routes.

    Returns:
        list: Route names
    """
    query = """
    SELECT DISTINCT route
    FROM analytics_analytics.agg_route_performance
    ORDER BY route
    """
    result = query_data( query)

    if not result.empty:
        return result['route'].tolist()
    return []


def test_connection() -> bool:
    """
    Test if database connection is working.

    Returns:
        bool: True if connection successful
    """
    try:
        conn = get_db()
        result = conn.execute("SELECT 1 as test").fetchone()
        return result[0] == 1
    except:
        return False
