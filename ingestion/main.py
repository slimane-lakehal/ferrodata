"""CLI entrypoint for the SNCF data ingestion pipeline."""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import SOURCES, SOURCES_MAP, AppConfig
from fetchers.sncf import SNCFFetcher
from loaders.local import LocalParquetLoader
from loaders.duckdb import DuckDBLoader
from loaders.bigquery import BigQueryLoader
from pipeline import FetchPipeline


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def build_pipeline(app_config: AppConfig) -> FetchPipeline:
    """
    Build the pipeline with configured loaders.

    Args:
        app_config: Application configuration

    Returns:
        Configured FetchPipeline
    """
    # Create fetcher
    fetcher = SNCFFetcher(base_url=app_config.sncf_base_url)

    # Create loaders based on config
    loaders = []

    if app_config.local_enabled:
        loaders.append(LocalParquetLoader(data_dir=app_config.local_data_dir))

    if app_config.duckdb_enabled:
        if not app_config.duckdb_path:
            raise ValueError("DuckDB enabled but duckdb_path not set")

        loaders.append(
            DuckDBLoader(
                db_path=app_config.duckdb_path,
                schema="raw_sncf"
            )
        )

    if app_config.bq_enabled:
        if not app_config.bq_project_id:
            raise ValueError("BigQuery enabled but GCP_PROJECT_ID not set")

        loaders.append(
            BigQueryLoader(
                project_id=app_config.bq_project_id,
                dataset=app_config.bq_dataset
            )
        )

    if not loaders:
        raise ValueError("No loaders enabled. Enable at least one destination.")

    return FetchPipeline(fetcher=fetcher, loaders=loaders)


def main() -> int:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="SNCF Data Ingestion Pipeline - Fetch and load train data to local/BigQuery"
    )

    parser.add_argument(
        "--env",
        choices=["dev", "prod"],
        default="dev",
        help="Environment (default: dev)"
    )

    parser.add_argument(
        "--sources",
        nargs="+",
        help="Specific sources to fetch (e.g., regularite_tgv gares). If not specified, fetches all."
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available sources and exit"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Only save to local files (disable BigQuery)"
    )

    parser.add_argument(
        "--bq-only",
        action="store_true",
        help="Only load to BigQuery (disable local files and DuckDB)"
    )

    parser.add_argument(
        "--duckdb-only",
        action="store_true",
        help="Only load to DuckDB (disable local files and BigQuery)"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)

    # List sources and exit
    if args.list:
        print("\nAvailable sources:")
        print("-" * 60)
        for source in SOURCES:
            print(f"  {source.name}")
            print(f"    Description: {source.description}")
            print(f"    API ID: {source.api_dataset_id}")
            print()
        return 0

    try:
        # Load configuration
        app_config = AppConfig.from_env(args.env)
        logger.info(f"Running in {args.env} environment")

        # Override based on flags
        if args.local_only:
            app_config.duckdb_enabled = False
            app_config.bq_enabled = False
        if args.bq_only:
            app_config.local_enabled = False
            app_config.duckdb_enabled = False
        if args.duckdb_only:
            app_config.local_enabled = False
            app_config.bq_enabled = False

        # Determine which sources to process
        if args.sources:
            source_configs = []
            for source_name in args.sources:
                if source_name not in SOURCES_MAP:
                    logger.error(f"Unknown source: {source_name}")
                    logger.info(f"Available sources: {list(SOURCES_MAP.keys())}")
                    return 1
                source_configs.append(SOURCES_MAP[source_name])
        else:
            source_configs = SOURCES

        logger.info(f"Processing {len(source_configs)} sources")

        # Build and run pipeline
        pipeline = build_pipeline(app_config)
        results = pipeline.run_multiple(source_configs)

        # Exit code based on results
        if all(r.fully_successful for r in results):
            return 0  # All succeeded
        elif any(r.success for r in results):
            return 2  # Partial success
        else:
            return 1  # All failed

    except KeyboardInterrupt:
        logger.warning("\nInterrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
