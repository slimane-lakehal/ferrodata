"""Pipeline orchestration for fetch and load operations."""

import time
import logging
from typing import List, Optional
import pandas as pd
from models import FetchResult, LoadResult, PipelineResult
from config import SourceConfig
from fetchers.base import DataFetcher
from loaders.base import DataLoader

logger = logging.getLogger(__name__)


class FetchPipeline:
    """Orchestrates the fetch and load pipeline."""

    def __init__(
        self,
        fetcher: DataFetcher,
        loaders: list[DataLoader],
    ):
        """
        Initialize the pipeline.

        Args:
            fetcher: Data fetcher implementation
            loaders: List of data loaders (e.g., local, BigQuery)
        """
        self.fetcher = fetcher
        self.loaders = loaders

    def run(self, source_config: SourceConfig) -> PipelineResult:
        """
        Run the complete pipeline for a source.

        Workflow:
        1. Fetch data from API
        2. Validate data
        3. Load to all configured destinations

        Args:
            source_config: Source configuration

        Returns:
            PipelineResult with fetch and load results
        """
        logger.info(f"Starting pipeline for {source_config.name}")

        # Step 1: Fetch data
        fetch_result, data = self._fetch_data(source_config)

        if not fetch_result.success:
            logger.error(f"Fetch failed for {source_config.name}: {fetch_result.error}")
            return PipelineResult(
                source_name=source_config.name,
                fetch_result=fetch_result,
                load_results=[]
            )

        # Step 2: Load to all destinations
        load_results = self._load_data(data, source_config)

        # Step 3: Build final result
        result = PipelineResult(
            source_name=source_config.name,
            fetch_result=fetch_result,
            load_results=load_results
        )

        # Log summary
        if result.fully_successful:
            logger.info(f"Pipeline completed successfully for {source_config.name}")
        elif result.success:
            logger.warning(f"Pipeline partially successful for {source_config.name}")
        else:
            logger.error(f"Pipeline failed for {source_config.name}")

        return result

    def _fetch_data(self, source_config: SourceConfig) -> tuple[FetchResult, pd.DataFrame | None]:
        """
        Fetch data from API.

        Args:
            source_config: Source configuration

        Returns:
            Tuple of (FetchResult, DataFrame or None)
        """
        start_time = time.time()

        try:
            logger.info(f"Fetching {source_config.api_dataset_id}")

            data = self.fetcher.fetch(
                dataset_id=source_config.api_dataset_id,
                format=source_config.api_format,
                params=source_config.api_params
            )

            # Basic validation
            if data is None or len(data) == 0:
                raise ValueError("Fetched data is empty")

            logger.info(f"Fetched {len(data)} rows, {len(data.columns)} columns")

            return FetchResult(
                success=True,
                source_name=source_config.name,
                rows_fetched=len(data),
                duration_seconds=time.time() - start_time,
                metadata={
                    "columns": list(data.columns),
                    "dataset_id": source_config.api_dataset_id,
                }
            ), data

        except Exception as e:
            logger.error(f"Fetch failed: {e}")

            return FetchResult(
                success=False,
                source_name=source_config.name,
                rows_fetched=0,
                duration_seconds=time.time() - start_time,
                error=str(e)
            ), None

    def _load_data(self, data: pd.DataFrame, source_config: SourceConfig) -> list[LoadResult]:
        """
        Load data to all configured destinations.

        Args:
            data: DataFrame to load
            source_config: Source configuration

        Returns:
            List of LoadResults
        """
        load_results = []

        for loader in self.loaders:
            logger.info(f"Loading to {loader.__class__.__name__}")

            # Check if loader supports source_config parameter
            if hasattr(loader, 'load') and 'source_config' in loader.load.__code__.co_varnames:
                # BigQueryLoader - pass source_config for advanced settings
                result = loader.load(data, source_config.name, source_config=source_config)
            else:
                # Simple loaders - just pass data and name
                result = loader.load(data, source_config.name)

            load_results.append(result)

            if result.success:
                logger.info(f"Loaded to {result.destination}")
            else:
                logger.error(f"Failed to load to {result.destination}: {result.error}")

        return load_results

    def run_multiple(self, source_configs: list[SourceConfig]) -> list[PipelineResult]:
        """
        Run pipeline for multiple sources sequentially.

        Args:
            source_configs: List of source configurations

        Returns:
            List of PipelineResults
        """
        results = []

        for source_config in source_configs:
            result = self.run(source_config)
            results.append(result)

        # Print summary
        self._print_summary(results)

        return results

    def _print_summary(self, results: List[PipelineResult]) -> None:
        """Print pipeline execution summary."""
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE SUMMARY")
        logger.info("=" * 60)

        total_success = sum(1 for r in results if r.fully_successful)
        total_partial = sum(1 for r in results if r.success and not r.fully_successful)
        total_failed = sum(1 for r in results if not r.success)

        logger.info(f"Total sources: {len(results)}")
        logger.info(f"  Fully successful: {total_success}")
        logger.info(f"  Partially successful: {total_partial}")
        logger.info(f"  Failed: {total_failed}")

        total_duration = sum(r.total_duration for r in results)
        logger.info(f"\nTotal duration: {total_duration:.2f}s")

        # Per-source details
        logger.info("\nDetails:")
        for result in results:
            status = "SUCCESS" if result.fully_successful else ("PARTIAL" if result.success else "FAILED")
            logger.info(f"  {status}: {result.source_name} - "
                       f"{result.fetch_result.rows_fetched} rows, "
                       f"{result.total_duration:.2f}s")

        logger.info("=" * 60)
