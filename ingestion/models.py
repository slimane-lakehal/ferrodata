"""Data models for the ingestion pipeline."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class LoadResult:
    """Result of a load operation to a destination."""
    success: bool
    destination: str  # "local", "duckdb" or "bigquery"
    source_name: str
    rows_loaded: int
    duration_seconds: float
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.utcnow())


@dataclass
class FetchResult:
    """Result of a fetch operation from an API."""
    success: bool
    source_name: str
    rows_fetched: int
    duration_seconds: float
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.utcnow())


@dataclass
class PipelineResult:
    """Result of a complete pipeline run (fetch + load)."""
    source_name: str
    fetch_result: FetchResult
    load_results: List[LoadResult]

    @property
    def success(self) -> bool:
        """Pipeline succeeds if fetch succeeded and at least one load succeeded."""
        return self.fetch_result.success and any(r.success for r in self.load_results)

    @property
    def fully_successful(self) -> bool:
        """All operations succeeded."""
        return self.fetch_result.success and all(r.success for r in self.load_results)

    @property
    def total_duration(self) -> float:
        """Total duration of all operations."""
        load_duration = sum(r.duration_seconds for r in self.load_results)
        return self.fetch_result.duration_seconds + load_duration
