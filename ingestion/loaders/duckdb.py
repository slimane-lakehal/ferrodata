"""DuckDB loader for local development."""

import duckdb
from pathlib import Path
from typing import Optional
import pandas as pd
import time
import logging
from config import SourceConfig
from models import LoadResult

logger = logging.getLogger(__name__)


class DuckDBLoader:
    """Loader for DuckDB (local SQL database)."""

    def __init__(self, db_path: Path, schema: str = "raw_sncf"):
        """
        Initialize DuckDB loader.

        Args:
            db_path: Path to DuckDB database file
            schema: Schema name (default: "raw_sncf")
        """
        self.db_path = Path(db_path)
        self.schema = schema

        # Create parent directory if needed
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Connect to DuckDB
        self.conn = duckdb.connect(str(self.db_path))

        # Create schema if not exists
        self.conn.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema}")

        logger.info(f"Connected to DuckDB at {self.db_path}")
    
    def load(self, data: pd.DataFrame, source_name: str,
             source_config: Optional[SourceConfig] = None) -> LoadResult:
        """
        Load data to DuckDB table.

        Args:
            data: DataFrame to load
            source_name: Name of the source
            source_config: Optional SourceConfig for advanced settings

        Returns:
            LoadResult with success status and metadata
        """
        start_time = time.time()

        # Determine table name
        if source_config and source_config.table_name:
            table_name = source_config.table_name
        else:
            table_name = source_name

        full_table = f"{self.schema}.{table_name}"

        try:
            # Determine write strategy
            if source_config and source_config.write_disposition == "WRITE_APPEND":
                # Append mode: insert new rows
                if self._table_exists(table_name):
                    self.conn.execute(f"INSERT INTO {full_table} SELECT * FROM data")
                    logger.info(f"Appended to existing table {full_table}")
                else:
                    # Table doesn't exist, create it
                    self.conn.execute(f"CREATE TABLE {full_table} AS SELECT * FROM data")
                    logger.info(f"Created new table {full_table}")
            else:
                # Replace mode (default): drop and recreate
                self.conn.execute(f"CREATE OR REPLACE TABLE {full_table} AS SELECT * FROM data")
                logger.info(f"Replaced table {full_table}")

            # Get row count for verification
            result = self.conn.execute(f"SELECT COUNT(*) FROM {full_table}").fetchone()
            rows_in_table = result[0] if result else 0

            logger.info(f"Loaded {len(data)} rows to {full_table} (total: {rows_in_table})")

            return LoadResult(
                success=True,
                destination="duckdb",
                source_name=source_name,
                rows_loaded=len(data),
                duration_seconds=time.time() - start_time,
                metadata={
                    "database": str(self.db_path),
                    "schema": self.schema,
                    "table": table_name,
                    "full_table": full_table,
                    "total_rows": rows_in_table,
                }
            )

        except Exception as e:
            logger.error(f"Failed to load {source_name} to DuckDB: {e}")

            return LoadResult(
                success=False,
                destination="duckdb",
                source_name=source_name,
                rows_loaded=0,
                duration_seconds=time.time() - start_time,
                error=str(e)
            )

    def _table_exists(self, table_name: str) -> bool:
        """Check if table exists in schema."""
        try:
            result = self.conn.execute(f"""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = '{self.schema}'
                AND table_name = '{table_name}'
            """).fetchone()
            return result[0] > 0 if result else False
        except Exception:
            return False

    def exists(self, source_name: str) -> bool:
        """
        Check if table exists.

        Args:
            source_name: Name of the source

        Returns:
            True if table exists, False otherwise
        """
        return self._table_exists(source_name)

    def get_table_info(self, source_name: str) -> Optional[dict]:
        """
        Get information about a DuckDB table.

        Args:
            source_name: Name of the source

        Returns:
            Dict with table info or None if table doesn't exist
        """
        full_table = f"{self.schema}.{source_name}"

        try:
            # Get row count
            count_result = self.conn.execute(f"SELECT COUNT(*) FROM {full_table}").fetchone()
            row_count = count_result[0] if count_result else 0

            # Get column info
            columns_result = self.conn.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = '{self.schema}'
                AND table_name = '{source_name}'
                ORDER BY ordinal_position
            """).fetchall()

            columns = [{"name": col[0], "type": col[1]} for col in columns_result]

            return {
                "num_rows": row_count,
                "num_columns": len(columns),
                "columns": columns,
                "database": str(self.db_path),
            }

        except Exception as e:
            logger.warning(f"Could not get table info for {full_table}: {e}")
            return None

    def close(self):
        """Close the DuckDB connection."""
        if hasattr(self, 'conn'):
            self.conn.close()
            logger.info("Closed DuckDB connection")

    def __del__(self):
        """Cleanup on deletion."""
        self.close()