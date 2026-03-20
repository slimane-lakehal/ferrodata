"""BigQuery loader with configuration-driven job settings."""

import time
import logging
from typing import Optional
from google.cloud import bigquery
import pandas as pd
from ingestion.models import LoadResult
from ingestion.config import SourceConfig

logger = logging.getLogger(__name__)


class BigQueryLoader:
    """Loader for Google BigQuery."""

    def __init__(self, project_id: str, dataset: str, location: str = "EU"):
        """
        Initialize BigQuery loader.

        Args:
            project_id: GCP project ID
            dataset: BigQuery dataset name (e.g., "raw_sncf")
            location: BigQuery location (default: "EU")
        """
        self.project_id = project_id
        self.dataset = dataset
        self.location = location
        self.client = bigquery.Client(project=project_id)

    def load(self, data: pd.DataFrame, source_name: str, source_config: Optional[SourceConfig] = None) -> LoadResult:
        """
        Load data to BigQuery table.

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

        table_id = f"{self.project_id}.{self.dataset}.{table_name}"

        try:
            # Build job configuration from source config
            job_config = self._build_job_config(source_config)

            # Load data
            job = self.client.load_table_from_dataframe(
                data, table_id, job_config=job_config, location=self.location
            )
            job.result()  # Wait for completion

            logger.info(f"Loaded {len(data)} rows to {table_id}")

            return LoadResult(
                success=True,
                destination="bigquery",
                source_name=source_name,
                rows_loaded=len(data),
                duration_seconds=time.time() - start_time,
                metadata={
                    "table_id": table_id,
                    "job_id": job.job_id,
                    "location": self.location,
                }
            )

        except Exception as e:
            logger.error(f"Failed to load {source_name} to BigQuery: {e}")

            return LoadResult(
                success=False,
                destination="bigquery",
                source_name=source_name,
                rows_loaded=0,
                duration_seconds=time.time() - start_time,
                error=str(e)
            )

    def _build_job_config(self, source_config: Optional[SourceConfig]) -> bigquery.LoadJobConfig:
        """
        Build BigQuery LoadJobConfig from SourceConfig.

        Args:
            source_config: Source configuration with BQ settings

        Returns:
            Configured LoadJobConfig
        """
        job_config = bigquery.LoadJobConfig()

        if source_config:
            # Write disposition from config
            job_config.write_disposition = source_config.write_disposition

            # Time partitioning if specified
            if source_config.partition_field:
                job_config.time_partitioning = bigquery.TimePartitioning(
                    field=source_config.partition_field
                )

            # Clustering if specified
            if source_config.clustering_fields:
                job_config.clustering_fields = source_config.clustering_fields
        else:
            # Default: replace table
            job_config.write_disposition = "WRITE_TRUNCATE"

        return job_config

    def exists(self, source_name: str) -> bool:
        """
        Check if BigQuery table exists.

        Args:
            source_name: Name of the source

        Returns:
            True if table exists, False otherwise
        """
        table_id = f"{self.project_id}.{self.dataset}.{source_name}"

        try:
            self.client.get_table(table_id)
            return True
        except Exception:
            return False

    def get_table_info(self, source_name: str) -> Optional[dict]:
        """
        Get information about a BigQuery table.

        Args:
            source_name: Name of the source

        Returns:
            Dict with table info or None if table doesn't exist
        """
        table_id = f"{self.project_id}.{self.dataset}.{source_name}"

        try:
            table = self.client.get_table(table_id)
            return {
                "num_rows": table.num_rows,
                "num_bytes": table.num_bytes,
                "created": table.created,
                "modified": table.modified,
                "schema": [{"name": field.name, "type": field.field_type} for field in table.schema],
            }
        except Exception as e:
            logger.warning(f"Could not get table info for {table_id}: {e}")
            return None
