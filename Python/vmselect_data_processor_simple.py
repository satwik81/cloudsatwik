#!/usr/bin/env python3
"""
VMSelect Data Processor (Simplified Version)

This script fetches data from VMSelect, applies thresholds, and exports 
filtered data to separate datastores using only built-in Python libraries.
"""

import requests
import json
import sqlite3
import logging
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os
from urllib.parse import urljoin


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ThresholdConfig:
    """Configuration for data thresholds"""
    metric_name: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    alert_threshold: Optional[float] = None
    comparison: str = "greater_than"  # greater_than, less_than, between, outside


@dataclass
class VMSelectConfig:
    """Configuration for VMSelect connection"""
    base_url: str
    query_timeout: int = 60
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {'Content-Type': 'application/json'}


class VMSelectClient:
    """Client for interacting with VMSelect"""
    
    def __init__(self, config: VMSelectConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(config.headers)
    
    def query(self, query: str, start_time: datetime, end_time: datetime, step: str = "1m") -> Dict[str, Any]:
        """
        Execute a PromQL query against VMSelect
        
        Args:
            query: PromQL query string
            start_time: Start time for the query
            end_time: End time for the query
            step: Query step interval
            
        Returns:
            Query result as dictionary
        """
        try:
            # Convert datetime to Unix timestamp
            start_timestamp = int(start_time.timestamp())
            end_timestamp = int(end_time.timestamp())
            
            # Construct query URL
            url = urljoin(self.config.base_url, '/api/v1/query_range')
            
            params = {
                'query': query,
                'start': start_timestamp,
                'end': end_timestamp,
                'step': step
            }
            
            logger.info(f"Executing query: {query}")
            logger.info(f"Time range: {start_time} to {end_time}")
            
            response = self.session.get(
                url, 
                params=params, 
                timeout=self.config.query_timeout
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('status') != 'success':
                raise ValueError(f"Query failed: {result.get('error', 'Unknown error')}")
            
            logger.info(f"Query executed successfully, returned {len(result.get('data', {}).get('result', []))} series")
            return result.get('data', {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise


class DataProcessor:
    """Process and filter data based on thresholds"""
    
    def __init__(self, thresholds: List[ThresholdConfig]):
        self.thresholds = {t.metric_name: t for t in thresholds}
    
    def process_vmselect_data(self, raw_data: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Process raw VMSelect data and apply thresholds
        
        Args:
            raw_data: Raw data from VMSelect query
            
        Returns:
            Dictionary with 'normal' and 'alerts' data
        """
        processed_data = {
            'normal': [],
            'alerts': []
        }
        
        try:
            for series in raw_data.get('result', []):
                metric_info = series.get('metric', {})
                metric_name = metric_info.get('__name__', 'unknown')
                values = series.get('values', [])
                
                threshold_config = self.thresholds.get(metric_name)
                
                for timestamp, value in values:
                    try:
                        numeric_value = float(value)
                        
                        # Convert timestamp to readable format
                        dt = datetime.fromtimestamp(timestamp)
                        
                        data_point = {
                            'timestamp': dt.isoformat(),
                            'metric_name': metric_name,
                            'value': numeric_value,
                            'labels': {k: v for k, v in metric_info.items() if k != '__name__'}
                        }
                        
                        # Apply thresholds if configured
                        if threshold_config:
                            is_alert = self._check_threshold(numeric_value, threshold_config)
                            if is_alert:
                                data_point['alert_type'] = self._get_alert_type(numeric_value, threshold_config)
                                processed_data['alerts'].append(data_point)
                            else:
                                processed_data['normal'].append(data_point)
                        else:
                            processed_data['normal'].append(data_point)
                            
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Failed to process value {value}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            raise
        
        logger.info(f"Processed {len(processed_data['normal'])} normal points and {len(processed_data['alerts'])} alerts")
        return processed_data
    
    def _check_threshold(self, value: float, config: ThresholdConfig) -> bool:
        """Check if value violates threshold"""
        if config.comparison == "greater_than" and config.alert_threshold:
            return value > config.alert_threshold
        elif config.comparison == "less_than" and config.alert_threshold:
            return value < config.alert_threshold
        elif config.comparison == "between" and config.min_value and config.max_value:
            return not (config.min_value <= value <= config.max_value)
        elif config.comparison == "outside" and config.min_value and config.max_value:
            return value < config.min_value or value > config.max_value
        
        return False
    
    def _get_alert_type(self, value: float, config: ThresholdConfig) -> str:
        """Get alert type based on threshold violation"""
        if config.comparison == "greater_than":
            return "high_threshold"
        elif config.comparison == "less_than":
            return "low_threshold"
        elif config.comparison in ["between", "outside"]:
            if config.min_value and value < config.min_value:
                return "below_range"
            elif config.max_value and value > config.max_value:
                return "above_range"
        
        return "threshold_violation"


class DataExporter:
    """Export processed data to various formats"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_to_csv(self, data: List[Dict], filename: str):
        """Export data to CSV file"""
        if not data:
            logger.warning(f"No data to export to {filename}")
            return
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # Get all unique keys for CSV headers
            all_keys = set()
            for item in data:
                all_keys.update(item.keys())
                if 'labels' in item and isinstance(item['labels'], dict):
                    for label_key in item['labels'].keys():
                        all_keys.add(f"label_{label_key}")
            
            # Remove 'labels' from keys since we'll flatten it
            all_keys.discard('labels')
            fieldnames = sorted(list(all_keys))
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in data:
                    # Flatten the data
                    flattened = {k: v for k, v in item.items() if k != 'labels'}
                    
                    # Add flattened labels
                    if 'labels' in item and isinstance(item['labels'], dict):
                        for label_key, label_value in item['labels'].items():
                            flattened[f"label_{label_key}"] = label_value
                    
                    writer.writerow(flattened)
            
            logger.info(f"Exported {len(data)} records to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            raise
    
    def export_to_json(self, data: List[Dict], filename: str):
        """Export data to JSON file"""
        if not data:
            logger.warning(f"No data to export to {filename}")
            return
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(data)} records to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export JSON: {e}")
            raise
    
    def export_to_sqlite(self, data: List[Dict], db_filename: str, table_name: str):
        """Export data to SQLite database"""
        if not data:
            logger.warning(f"No data to export to {table_name}")
            return
        
        db_path = os.path.join(self.output_dir, db_filename)
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Create table based on first record
                sample_record = data[0]
                columns = []
                
                for key, value in sample_record.items():
                    if key == 'labels':
                        continue
                    if isinstance(value, (int, float)):
                        columns.append(f"{key} REAL")
                    else:
                        columns.append(f"{key} TEXT")
                
                # Add columns for labels
                if 'labels' in sample_record and isinstance(sample_record['labels'], dict):
                    for label_key in sample_record['labels'].keys():
                        columns.append(f"label_{label_key} TEXT")
                
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {', '.join(columns)}
                )
                """
                
                cursor.execute(create_table_sql)
                
                # Insert data
                for item in data:
                    # Flatten the data
                    flattened = {k: v for k, v in item.items() if k != 'labels'}
                    
                    # Add flattened labels
                    if 'labels' in item and isinstance(item['labels'], dict):
                        for label_key, label_value in item['labels'].items():
                            flattened[f"label_{label_key}"] = label_value
                    
                    placeholders = ', '.join(['?' for _ in flattened])
                    insert_sql = f"INSERT INTO {table_name} ({', '.join(flattened.keys())}) VALUES ({placeholders})"
                    
                    cursor.execute(insert_sql, list(flattened.values()))
                
                conn.commit()
            
            logger.info(f"Exported {len(data)} records to SQLite table {table_name}")
            
        except Exception as e:
            logger.error(f"Failed to export to SQLite: {e}")
            raise


class VMSelectDataProcessor:
    """Main class to orchestrate data processing"""
    
    def __init__(self, vmselect_config: VMSelectConfig, thresholds: List[ThresholdConfig], output_dir: str = "output"):
        self.vmselect_client = VMSelectClient(vmselect_config)
        self.data_processor = DataProcessor(thresholds)
        self.data_exporter = DataExporter(output_dir)
    
    def process_and_export(self, queries: List[str], hours_back: int = 1, export_formats: List[str] = None):
        """
        Main method to process queries and export data
        
        Args:
            queries: List of PromQL queries to execute
            hours_back: Number of hours to look back for data
            export_formats: List of export formats ('csv', 'json', 'sqlite')
        """
        if export_formats is None:
            export_formats = ['csv', 'json']
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        all_normal_data = []
        all_alert_data = []
        
        try:
            for query in queries:
                logger.info(f"Processing query: {query}")
                
                # Fetch data from VMSelect
                raw_data = self.vmselect_client.query(query, start_time, end_time)
                
                # Process and filter data
                processed_data = self.data_processor.process_vmselect_data(raw_data)
                
                all_normal_data.extend(processed_data['normal'])
                all_alert_data.extend(processed_data['alerts'])
            
            # Export data in requested formats
            timestamp_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if 'csv' in export_formats:
                self.data_exporter.export_to_csv(all_normal_data, f"normal_data_{timestamp_suffix}.csv")
                self.data_exporter.export_to_csv(all_alert_data, f"alert_data_{timestamp_suffix}.csv")
            
            if 'json' in export_formats:
                self.data_exporter.export_to_json(all_normal_data, f"normal_data_{timestamp_suffix}.json")
                self.data_exporter.export_to_json(all_alert_data, f"alert_data_{timestamp_suffix}.json")
            
            if 'sqlite' in export_formats:
                self.data_exporter.export_to_sqlite(all_normal_data, f"metrics_{timestamp_suffix}.db", "normal_data")
                self.data_exporter.export_to_sqlite(all_alert_data, f"metrics_{timestamp_suffix}.db", "alert_data")
            
            logger.info("Data processing and export completed successfully")
            return {
                'normal_count': len(all_normal_data),
                'alert_count': len(all_alert_data),
                'timestamp': timestamp_suffix
            }
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise


def main():
    """Example usage of the VMSelect Data Processor"""
    
    # Configuration
    vmselect_config = VMSelectConfig(
        base_url="http://localhost:8481",
        query_timeout=60
    )
    
    # Define thresholds
    thresholds = [
        ThresholdConfig(
            metric_name="cpu_usage",
            alert_threshold=80,
            comparison="greater_than"
        ),
        ThresholdConfig(
            metric_name="memory_usage_percent",
            alert_threshold=90,
            comparison="greater_than"
        ),
        ThresholdConfig(
            metric_name="disk_usage_percent",
            alert_threshold=85,
            comparison="greater_than"
        )
    ]
    
    # Define queries
    queries = [
        "cpu_usage",
        "memory_usage_percent",
        "disk_usage_percent"
    ]
    
    # Create processor and run
    processor = VMSelectDataProcessor(vmselect_config, thresholds)
    
    try:
        result = processor.process_and_export(
            queries=queries,
            hours_back=1,
            export_formats=['csv', 'json', 'sqlite']
        )
        
        print(f"Processing completed successfully!")
        print(f"Normal data points: {result['normal_count']}")
        print(f"Alert data points: {result['alert_count']}")
        print(f"Files created with timestamp: {result['timestamp']}")
        
    except Exception as e:
        print(f"Processing failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())