"""Base protocol for data loaders."""

from typing import Protocol
import pandas as pd
from models import LoadResult


class DataLoader(Protocol):
    """Protocol for loading data to a destination."""

    def load(self, data: pd.DataFrame, source_name: str) -> LoadResult:
        """
        Load data to the destination.

        Args:
            data: DataFrame to load
            source_name: Name of the source (e.g., "regularite_tgv")

        Returns:
            LoadResult with success status and metadata
        """
        ...

    def exists(self, source_name: str) -> bool:
        """
        Check if data already exists at destination.

        Args:
            source_name: Name of the source to check

        Returns:
            True if data exists, False otherwise
        """
        ...
