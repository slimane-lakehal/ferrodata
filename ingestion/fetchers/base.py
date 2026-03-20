"""Base protocol for data fetchers."""

from typing import Protocol
import pandas as pd


class DataFetcher(Protocol):
    """Protocol for fetching data from an API."""

    def fetch(self, dataset_id: str) -> pd.DataFrame:
        """
        Fetch data from the API.

        Args:
            dataset_id: API dataset identifier

        Returns:
            DataFrame with fetched data

        Raises:
            requests.HTTPError: If API request fails
        """
        ...
    