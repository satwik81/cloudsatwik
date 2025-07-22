#!/usr/bin/env python3
"""
VMSelect Data Processor

This script fetches data from VMSelect, applies thresholds, and exports 
filtered data to separate datastores (CSV, JSON, Database).
"""

import requests
import pandas as pd
import json
import sqlite3
import logging
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
    

@dataclass
class VMSelectConfig:
    """Configuration for VMSelect connection"""
    base_url: str
    query_timeout: int = 30
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {'Content-Type': 'application/json'}


class VMSelectClient:
    """Client for interacting with VMSelect API"""
    
    def __init__(self, config: VMSelectConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(config.headers)
    
    def query(self, query: str, start_time: str = None, end_time: str = None) -> Dict[str, Any]:
        """
        Execute a PromQL query against VMSelect
        
        Args:
            query: PromQL query string
            start_time: Start time in RFC3339 format
            end_time: End time in RFC3339 format
            
        Returns:
            Query results as dictionary
        """
        url = urljoin(self.config.base_url, '/select/0/prometheus/api/v1/query_range')
        
        # Default time range if not provided
        if not end_time:
            end_time = datetime.now().isoformat() + 'Z'
        if not start_time:
            start_time = (datetime.now() - timedelta(hours=1)).isoformat() + 'Z'
        
        params = {
            'query': query,
            'start': start_time,
            'end': end_time,
            'step': '60s'  # 1 minute step
        }
        
        try:
            logger.info(f"Executing query: {query}")
            response = self.session.get(
                url, 
                params=params, 
                timeout=self.config.query_timeout
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') != 'success':
                raise ValueError(f"Query failed: {data.get('error', 'Unknown error')}")
            
            return data['data']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to execute query: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response: {e}")
            raise


class DataProcessor:
    """Process and filter data based on thresholds"""
    
    def __init__(self, thresholds: List[ThresholdConfig]):
        self.thresholds = {t.metric_name: t for t in thresholds}
    
    def process_vmselect_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert VMSelect response to pandas DataFrame
        
        Args:
            data: VMSelect query response data
            
        Returns:
            Processed DataFrame
        """
        records = []
        
        for result in data.get('result', []):
            metric_name = result['metric'].get('__name__', 'unknown')
            labels = {k: v for k, v in result['metric'].items() if k != '__name__'}
            
            for timestamp, value in result['values']:
                records.append({
                    'metric_name': metric_name,
                    'timestamp': pd.to_datetime(float(timestamp), unit='s'),
                    'value': float(value),
                    'labels': json.dumps(labels, sort_keys=True)
                })
        
        df = pd.DataFrame(records)
        logger.info(f"Processed {len(df)} data points")
        return df
    
    def apply_thresholds(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply threshold filters to the data
        
        Args:
            df: Input DataFrame
            
        Returns:
            Filtered DataFrame
        """
        filtered_df = df.copy()
        
        for metric_name, threshold in self.thresholds.items():
            metric_data = filtered_df[filtered_df['metric_name'] == metric_name]
            
            if metric_data.empty:
                continue
            
            # Apply min threshold
            if threshold.min_value is not None:
                mask = metric_data['value'] >= threshold.min_value
                logger.info(f"Applied min threshold {threshold.min_value} to {metric_name}: "
                          f"{mask.sum()}/{len(mask)} points passed")
            
            # Apply max threshold
            if threshold.max_value is not None:
                mask = mask & (metric_data['value'] <= threshold.max_value)
                logger.info(f"Applied max threshold {threshold.max_value} to {metric_name}: "
                          f"{mask.sum()}/{len(mask)} points passed")
            
            # Mark alerts
            if threshold.alert_threshold is not None:
                alert_mask = metric_data['value'] > threshold.alert_threshold
                filtered_df.loc[metric_data.index[alert_mask], 'alert'] = True
        
        # Add alert column if not exists
        if 'alert' not in filtered_df.columns:
            filtered_df['alert'] = False
        
        return filtered_df


class DataExporter:
    """Export processed data to various datastores"""
    
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_to_csv(self, df: pd.DataFrame, filename: str = None) -> str:
        """Export DataFrame to CSV file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vmselect_data_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Exported {len(df)} records to CSV: {filepath}")
        return filepath
    
    def export_to_json(self, df: pd.DataFrame, filename: str = None) -> str:
        """Export DataFrame to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vmselect_data_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert DataFrame to JSON with proper datetime handling
        json_data = []
        for _, row in df.iterrows():
            record = row.to_dict()
            record['timestamp'] = record['timestamp'].isoformat()
            json_data.append(record)
        
        with open(filepath, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)
        
        logger.info(f"Exported {len(df)} records to JSON: {filepath}")
        return filepath
    
    def export_to_sqlite(self, df: pd.DataFrame, db_path: str = None, table_name: str = "metrics") -> str:
        """Export DataFrame to SQLite database"""
        if db_path is None:
            db_path = os.path.join(self.output_dir, "vmselect_data.db")
        
        conn = sqlite3.connect(db_path)
        try:
            # Create table if not exists
            df.to_sql(table_name, conn, if_exists='append', index=False)
            logger.info(f"Exported {len(df)} records to SQLite: {db_path}")
        finally:
            conn.close()
        
        return db_path
    
    def export_alerts_only(self, df: pd.DataFrame) -> Dict[str, str]:
        """Export only alert data to separate files"""
        alert_df = df[df.get('alert', False) == True]
        
        if alert_df.empty:
            logger.info("No alerts to export")
            return {}
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exports = {}
        
        exports['csv'] = self.export_to_csv(alert_df, f"alerts_{timestamp}.csv")
        exports['json'] = self.export_to_json(alert_df, f"alerts_{timestamp}.json")
        exports['sqlite'] = self.export_to_sqlite(alert_df, table_name="alerts")
        
        return exports


class VMSelectDataProcessor:
    """Main class orchestrating the data processing pipeline"""
    
    def __init__(self, vmselect_config: VMSelectConfig, thresholds: List[ThresholdConfig]):
        self.client = VMSelectClient(vmselect_config)
        self.processor = DataProcessor(thresholds)
        self.exporter = DataExporter()
    
    def run_pipeline(self, queries: List[str], start_time: str = None, end_time: str = None) -> Dict[str, Any]:
        """
        Run the complete data processing pipeline
        
        Args:
            queries: List of PromQL queries to execute
            start_time: Start time for data retrieval
            end_time: End time for data retrieval
            
        Returns:
            Dictionary containing export file paths and statistics
        """
        all_data = []
        
        # Fetch data for all queries
        for query in queries:
            try:
                data = self.client.query(query, start_time, end_time)
                df = self.processor.process_vmselect_data(data)
                all_data.append(df)
            except Exception as e:
                logger.error(f"Failed to process query '{query}': {e}")
                continue
        
        if not all_data:
            logger.warning("No data retrieved from any queries")
            return {'error': 'No data retrieved'}
        
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"Combined data: {len(combined_df)} total records")
        
        # Apply thresholds
        filtered_df = self.processor.apply_thresholds(combined_df)
        
        # Export data
        exports = {}
        exports['all_data'] = {
            'csv': self.exporter.export_to_csv(filtered_df),
            'json': self.exporter.export_to_json(filtered_df),
            'sqlite': self.exporter.export_to_sqlite(filtered_df)
        }
        
        # Export alerts separately
        exports['alerts'] = self.exporter.export_alerts_only(filtered_df)
        
        # Calculate statistics
        stats = {
            'total_records': len(combined_df),
            'filtered_records': len(filtered_df),
            'alert_records': len(filtered_df[filtered_df.get('alert', False) == True]),
            'unique_metrics': filtered_df['metric_name'].nunique(),
            'time_range': {
                'start': filtered_df['timestamp'].min().isoformat() if not filtered_df.empty else None,
                'end': filtered_df['timestamp'].max().isoformat() if not filtered_df.empty else None
            }
        }
        
        return {
            'exports': exports,
            'statistics': stats
        }


def main():
    """Example usage of the VMSelect Data Processor"""
    
    # Configuration
    vmselect_config = VMSelectConfig(
        base_url="http://localhost:8481",  # Update with your VMSelect URL
        query_timeout=60
    )
    
    # Define thresholds
    thresholds = [
        ThresholdConfig(
            metric_name="cpu_usage",
            min_value=0,
            max_value=100,
            alert_threshold=80
        ),
        ThresholdConfig(
            metric_name="memory_usage",
            min_value=0,
            max_value=100,
            alert_threshold=85
        ),
        ThresholdConfig(
            metric_name="disk_usage",
            min_value=0,
            max_value=100,
            alert_threshold=90
        )
    ]
    
    # Initialize processor
    processor = VMSelectDataProcessor(vmselect_config, thresholds)
    
    # Define queries
    queries = [
        'cpu_usage{job="node_exporter"}',
        'memory_usage{job="node_exporter"}',
        'disk_usage{job="node_exporter"}'
    ]
    
    # Run pipeline
    try:
        result = processor.run_pipeline(queries)
        
        if 'error' in result:
            logger.error(f"Pipeline failed: {result['error']}")
            return
        
        # Print results
        print("\n=== VMSelect Data Processing Results ===")
        print(f"Statistics: {json.dumps(result['statistics'], indent=2)}")
        print(f"\nExported files:")
        for category, files in result['exports'].items():
            print(f"  {category}:")
            if isinstance(files, dict):
                for format_type, filepath in files.items():
                    print(f"    {format_type}: {filepath}")
            else:
                print(f"    {files}")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise


if __name__ == "__main__":
    main()