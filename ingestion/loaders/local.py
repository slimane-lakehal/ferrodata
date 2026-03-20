"""Local parquet file loader."""

import time
import logging
from pathlib import Path
import pandas as pd
from ingestion.models import LoadResult

logger = logging.getLogger(__name__)


class LocalParquetLoader:
    """Loader for local parquet files."""

    def __init__(self, data_dir: Path):
        """
        Initialize local parquet loader.

        Args:
            data_dir: Directory to store parquet files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load(self, data: pd.DataFrame, source_name: str) -> LoadResult:
        """
        Load data to local parquet file.

        Args:
            data: DataFrame to save
            source_name: Name of the source (used as filename)

        Returns:
            LoadResult with success status and metadata
        """
        start_time = time.time()
        file_path = self.data_dir / f"{source_name}.parquet"

        try:
            data.to_parquet(file_path, index=False, compression="snappy")

            logger.info(f"Loaded {len(data)} rows to {file_path}")

            return LoadResult(
                success=True,
                destination="local",
                source_name=source_name,
                rows_loaded=len(data),
                duration_seconds=time.time() - start_time,
                metadata={
                    "file_path": str(file_path),
                    "file_size_bytes": file_path.stat().st_size,
                }
            )

        except Exception as e:
            logger.error(f"Failed to load {source_name} to local: {e}")

            return LoadResult(
                success=False,
                destination="local",
                source_name=source_name,
                rows_loaded=0,
                duration_seconds=time.time() - start_time,
                error=str(e)
            )

    def exists(self, source_name: str) -> bool:
        """
        Check if parquet file exists.

        Args:
            source_name: Name of the source

        Returns:
            True if file exists, False otherwise
        """
        file_path = self.data_dir / f"{source_name}.parquet"
        return file_path.exists()
