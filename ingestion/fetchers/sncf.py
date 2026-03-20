"""SNCF Open Data API fetcher."""

import io
import time
import requests
import pandas as pd
from typing import Dict


class SNCFFetcher:
    """Fetcher for SNCF Open Data API."""

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize SNCF fetcher.

        Args:
            base_url: Base URL for the SNCF API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout

    def fetch(self, dataset_id: str, format: str = "parquet", params: Dict = None) -> pd.DataFrame:
        """
        Fetch dataset from SNCF API.

        Args:
            dataset_id: SNCF dataset identifier (e.g., "regularite-mensuelle-tgv-aqst")
            format: Export format (default: "parquet")
            params: Additional query parameters

        Returns:
            DataFrame with fetched data

        Raises:
            requests.HTTPError: If API request fails
            requests.Timeout: If request times out
        """
        if params is None:
            params = {"limit": -1, "timezone": "UTC"}

        url = f"{self.base_url}/{dataset_id}/exports/{format}"

        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()

        # Parse parquet data from response
        df = pd.read_parquet(io.BytesIO(response.content))

        return df

    def fetch_with_metadata(self, dataset_id: str, format: str = "parquet", params: Dict = None) -> tuple[pd.DataFrame, dict]:
        """
        Fetch dataset and return data with metadata.

        Args:
            dataset_id: SNCF dataset identifier
            format: Export format (default: "parquet")
            params: Additional query parameters

        Returns:
            Tuple of (DataFrame, metadata dict)
        """
        start_time = time.time()

        df = self.fetch(dataset_id, format, params)

        metadata = {
            "dataset_id": dataset_id,
            "rows_fetched": len(df),
            "columns": list(df.columns),
            "duration_seconds": time.time() - start_time,
        }

        return df, metadata
