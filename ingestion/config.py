"""Configuration for the SNCF data ingestion pipeline."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, List


# ============= Source Definitions =============

@dataclass
class SourceConfig:
    """Configuration for a data source."""

    name: str                          # Internal name: "regularite_tgv"
    api_dataset_id: str                # API identifier: "regularite-mensuelle-tgv-aqst"
    description: str

    api_format: str = "parquet"
    api_params: Dict = field(default_factory=lambda: {"limit": -1, "timezone": "UTC"})

    table_name: str = None
    write_disposition: str = "WRITE_TRUNCATE"
    partition_field: Optional[str] = None
    clustering_fields: Optional[List[str]] = None

    def __post_init__(self):
        """Set defaults after initialization."""
        if self.table_name is None:
            self.table_name = self.name


# Define all data sources
SOURCES = [
    SourceConfig(
        name="regularite_tgv",
        api_dataset_id="regularite-mensuelle-tgv-aqst",
        description="Régularité mensuelle TGV par liaisons (AQST).",
    ),
    SourceConfig(
        name="regularite_ter",
        api_dataset_id="regularite-mensuelle-ter",
        description="Régularité mensuelle TER depuis janvier 2013.",
    ),
    SourceConfig(
        name="regularite_intercites",
        api_dataset_id="regularite-mensuelle-intercites",
        description="Régularité mensuelle des trains Intercités depuis janvier 2014.",
    ),
    SourceConfig(
        name="gares",
        api_dataset_id="liste-des-gares",
        description="Liste des gares du Réseau Ferré National.",
    ),
]

# Map for easy lookup by name
SOURCES_MAP: Dict[str, SourceConfig] = {s.name: s for s in SOURCES}


# ============= Application Configuration =============

@dataclass
class AppConfig:
    """Runtime configuration for the application."""
    # API settings
    sncf_base_url: str

    # Local storage (parquet files)
    local_data_dir: Path
    local_enabled: bool

    # DuckDB (local SQL database)
    duckdb_path: Optional[Path]
    duckdb_enabled: bool

    # BigQuery settings
    bq_project_id: Optional[str]
    bq_dataset: str
    bq_enabled: bool

    @classmethod
    def from_env(cls, env: Optional[str] = None) -> 'AppConfig':
        """
        Load configuration based on environment.

        Args:
            env: Environment name ("dev" or "prod").
                 If None, reads from ENV environment variable.
        """
        if env is None:
            env = os.getenv("ENV", "dev")

        if env == "dev":
            return cls(
                sncf_base_url="https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets",
                local_data_dir=Path(__file__).parent.parent / "data",
                local_enabled=True,  # Keep parquet files as backup
                duckdb_path=Path(__file__).parent.parent / "ferrodata.duckdb",
                duckdb_enabled=True,  # Main dev target for SQL queries
                bq_project_id=os.getenv("GCP_PROJECT_ID"),
                bq_dataset=os.getenv("BQ_DATASET", "raw_sncf"),
                bq_enabled=False,  # Disabled by default in dev
            )
        elif env == "prod":
            return cls(
                sncf_base_url="https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets",
                local_data_dir=Path("data/sncf/backups"),
                local_enabled=True,  # Keep parquet files as backup
                duckdb_path=None,
                duckdb_enabled=False,  # Not needed in production
                bq_project_id=os.getenv("GCP_PROJECT_ID"),
                bq_dataset=os.getenv("BQ_DATASET", "raw_sncf"),
                bq_enabled=True,  # Main prod target
            )
        else:
            raise ValueError(f"Unknown environment: {env}. Use 'dev' or 'prod'.")



DATASETS = {s.name: s.api_dataset_id for s in SOURCES}
SNCF_BASE_URL = "https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets"
