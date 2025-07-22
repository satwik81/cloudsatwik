#!/usr/bin/env python3
"""
Data Processor with Threshold-based Export System

This module reads configuration from config.yaml and processes data from various
datasources, applies threshold-based filtering, and exports data to appropriate
destinations when thresholds are met.
"""

import yaml
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio
import concurrent.futures
from dataclasses import dataclass
from abc import ABC, abstractmethod

from connectors.datasource_factory import DataSourceFactory
from connectors.export_factory import ExportFactory
from utils.threshold_processor import ThresholdProcessor
from utils.logger import setup_logger


@dataclass
class ProcessingResult:
    """Result of processing a batch of data"""
    rule_name: str
    processed_count: int
    exported_count: int
    errors: List[str]


class DataProcessor:
    """Main data processing engine"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.logger = setup_logger(self.config.get('settings', {}).get('log_level', 'INFO'))
        self.datasource_factory = DataSourceFactory()
        self.export_factory = ExportFactory()
        self.threshold_processor = ThresholdProcessor()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    async def process_all_sources(self) -> List[ProcessingResult]:
        """Process data from all configured datasources"""
        results = []
        
        # Get data from all datasources
        all_data = await self._collect_data_from_sources()
        
        if all_data.empty:
            self.logger.warning("No data collected from any datasource")
            return results
        
        # Process each rule
        for rule in self.config.get('processing_rules', []):
            try:
                result = await self._process_rule(all_data, rule)
                results.append(result)
                self.logger.info(f"Rule '{rule['name']}' processed: {result.exported_count} records exported")
            except Exception as e:
                self.logger.error(f"Error processing rule '{rule['name']}': {str(e)}")
                results.append(ProcessingResult(
                    rule_name=rule['name'],
                    processed_count=0,
                    exported_count=0,
                    errors=[str(e)]
                ))
        
        return results
    
    async def _collect_data_from_sources(self) -> pd.DataFrame:
        """Collect data from all configured datasources"""
        all_dataframes = []
        
        settings = self.config.get('settings', {})
        max_workers = settings.get('max_workers', 4)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            tasks = []
            
            for source_name, source_config in self.config.get('datasources', {}).items():
                task = executor.submit(self._get_data_from_source, source_name, source_config)
                tasks.append(task)
            
            for future in concurrent.futures.as_completed(tasks):
                try:
                    df = future.result()
                    if not df.empty:
                        all_dataframes.append(df)
                except Exception as e:
                    self.logger.error(f"Error collecting data from source: {str(e)}")
        
        if all_dataframes:
            return pd.concat(all_dataframes, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def _get_data_from_source(self, source_name: str, source_config: Dict[str, Any]) -> pd.DataFrame:
        """Get data from a single datasource"""
        try:
            self.logger.info(f"Collecting data from source: {source_name}")
            datasource = self.datasource_factory.create_datasource(source_config)
            df = datasource.get_data()
            self.logger.info(f"Collected {len(df)} records from {source_name}")
            return df
        except Exception as e:
            self.logger.error(f"Failed to collect data from {source_name}: {str(e)}")
            return pd.DataFrame()
    
    async def _process_rule(self, data: pd.DataFrame, rule: Dict[str, Any]) -> ProcessingResult:
        """Process a single rule and export matching data"""
        rule_name = rule['name']
        self.logger.info(f"Processing rule: {rule_name}")
        
        # Apply threshold filtering
        filtered_data = self.threshold_processor.apply_rule(data, rule)
        
        if filtered_data.empty:
            self.logger.info(f"No data matches rule '{rule_name}'")
            return ProcessingResult(
                rule_name=rule_name,
                processed_count=len(data),
                exported_count=0,
                errors=[]
            )
        
        # Export filtered data
        export_target_name = rule.get('export_target')
        if not export_target_name:
            raise ValueError(f"No export_target specified for rule '{rule_name}'")
        
        export_config = self.config.get('export_targets', {}).get(export_target_name)
        if not export_config:
            raise ValueError(f"Export target '{export_target_name}' not found in configuration")
        
        try:
            exporter = self.export_factory.create_exporter(export_config)
            exported_count = await exporter.export_data(filtered_data)
            
            return ProcessingResult(
                rule_name=rule_name,
                processed_count=len(data),
                exported_count=exported_count,
                errors=[]
            )
        except Exception as e:
            error_msg = f"Failed to export data for rule '{rule_name}': {str(e)}"
            self.logger.error(error_msg)
            return ProcessingResult(
                rule_name=rule_name,
                processed_count=len(data),
                exported_count=0,
                errors=[error_msg]
            )
    
    async def run_continuous(self, interval_seconds: int = 60):
        """Run the processor continuously at specified intervals"""
        self.logger.info(f"Starting continuous processing (interval: {interval_seconds}s)")
        
        while True:
            try:
                start_time = datetime.now()
                results = await self.process_all_sources()
                
                # Log summary
                total_exported = sum(r.exported_count for r in results)
                total_errors = sum(len(r.errors) for r in results)
                processing_time = (datetime.now() - start_time).total_seconds()
                
                self.logger.info(f"Processing cycle completed: {total_exported} records exported, "
                               f"{total_errors} errors, {processing_time:.2f}s")
                
                # Wait for next cycle
                await asyncio.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                self.logger.info("Stopping continuous processing")
                break
            except Exception as e:
                self.logger.error(f"Error in continuous processing: {str(e)}")
                await asyncio.sleep(interval_seconds)


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Data Processor with Threshold-based Export")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")
    parser.add_argument("--continuous", action="store_true", help="Run in continuous mode")
    parser.add_argument("--interval", type=int, default=60, help="Interval for continuous mode (seconds)")
    
    args = parser.parse_args()
    
    processor = DataProcessor(args.config)
    
    if args.continuous:
        await processor.run_continuous(args.interval)
    else:
        results = await processor.process_all_sources()
        
        # Print summary
        print("\n=== Processing Summary ===")
        for result in results:
            print(f"Rule: {result.rule_name}")
            print(f"  Exported: {result.exported_count} records")
            if result.errors:
                print(f"  Errors: {len(result.errors)}")
                for error in result.errors:
                    print(f"    - {error}")
            print()


if __name__ == "__main__":
    asyncio.run(main())