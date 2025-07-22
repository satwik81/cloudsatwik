#!/usr/bin/env python3
"""
Example Usage of VMSelect Data Processor

This script demonstrates different ways to use the VMSelect Data Processor
for fetching, processing, and exporting monitoring data.
"""

import sys
from datetime import datetime, timedelta
from vmselect_data_processor_simple import (
    VMSelectConfig, ThresholdConfig, VMSelectDataProcessor
)


def example_basic_usage():
    """Basic usage example with CPU and memory monitoring"""
    print("=" * 60)
    print("Example 1: Basic CPU and Memory Monitoring")
    print("=" * 60)
    
    # Configure VMSelect connection
    vmselect_config = VMSelectConfig(
        base_url="http://localhost:8481",  # Change to your VMSelect URL
        query_timeout=60,
        headers={
            'Content-Type': 'application/json',
            # Add authentication if needed:
            # 'Authorization': 'Bearer your-token-here'
        }
    )
    
    # Define thresholds for alerting
    thresholds = [
        ThresholdConfig(
            metric_name="cpu_usage_percent",
            alert_threshold=80.0,
            comparison="greater_than"
        ),
        ThresholdConfig(
            metric_name="memory_usage_percent", 
            alert_threshold=90.0,
            comparison="greater_than"
        )
    ]
    
    # Define PromQL queries
    queries = [
        "cpu_usage_percent",
        "memory_usage_percent"
    ]
    
    # Create and run processor
    processor = VMSelectDataProcessor(
        vmselect_config=vmselect_config,
        thresholds=thresholds,
        output_dir="output_basic"
    )
    
    try:
        result = processor.process_and_export(
            queries=queries,
            hours_back=1,
            export_formats=['csv', 'json']
        )
        
        print(f"✓ Processing completed!")
        print(f"  Normal data points: {result['normal_count']}")
        print(f"  Alert data points: {result['alert_count']}")
        print(f"  Output files timestamp: {result['timestamp']}")
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        print("Note: This will fail without a running VMSelect instance")


def example_advanced_thresholds():
    """Advanced example with complex threshold configurations"""
    print("\n" + "=" * 60)
    print("Example 2: Advanced Threshold Configurations")
    print("=" * 60)
    
    # More complex threshold configurations
    thresholds = [
        # High CPU usage alert
        ThresholdConfig(
            metric_name="cpu_usage_percent",
            alert_threshold=85.0,
            comparison="greater_than"
        ),
        
        # Low disk space alert
        ThresholdConfig(
            metric_name="disk_free_percent",
            alert_threshold=10.0,
            comparison="less_than"
        ),
        
        # Network latency should be within acceptable range
        ThresholdConfig(
            metric_name="network_latency_ms",
            min_value=1.0,
            max_value=100.0,
            comparison="outside"  # Alert if outside 1-100ms range
        ),
        
        # Temperature monitoring - alert if NOT between normal range
        ThresholdConfig(
            metric_name="server_temperature_celsius",
            min_value=10.0,
            max_value=70.0,
            comparison="between"  # Alert if NOT between 10-70°C
        )
    ]
    
    print("Configured thresholds:")
    for threshold in thresholds:
        print(f"  - {threshold.metric_name}: {threshold.comparison}")
        if threshold.alert_threshold:
            print(f"    Alert if > {threshold.alert_threshold}")
        elif threshold.min_value and threshold.max_value:
            if threshold.comparison == "between":
                print(f"    Alert if NOT between {threshold.min_value} and {threshold.max_value}")
            else:
                print(f"    Alert if outside range {threshold.min_value} to {threshold.max_value}")


def example_custom_queries():
    """Example with custom PromQL queries"""
    print("\n" + "=" * 60)
    print("Example 3: Custom PromQL Queries")
    print("=" * 60)
    
    # More sophisticated PromQL queries
    queries = [
        # Average CPU usage across all instances
        'avg(cpu_usage_percent) by (instance)',
        
        # Memory usage with rate calculation
        'rate(memory_usage_bytes[5m])',
        
        # Disk I/O operations per second
        'rate(disk_io_operations_total[1m])',
        
        # Network traffic aggregated by interface
        'sum(rate(network_bytes_total[5m])) by (device)',
        
        # HTTP request error rate
        'rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100'
    ]
    
    print("Example PromQL queries:")
    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")


def example_multiple_datastores():
    """Example exporting to multiple datastores"""
    print("\n" + "=" * 60)
    print("Example 4: Multiple Datastore Export")
    print("=" * 60)
    
    vmselect_config = VMSelectConfig(
        base_url="http://localhost:8481"
    )
    
    thresholds = [
        ThresholdConfig(
            metric_name="response_time_ms",
            alert_threshold=1000.0,
            comparison="greater_than"
        )
    ]
    
    processor = VMSelectDataProcessor(
        vmselect_config=vmselect_config,
        thresholds=thresholds,
        output_dir="output_multiple"
    )
    
    print("Will export to multiple formats:")
    print("  - CSV files for spreadsheet analysis")
    print("  - JSON files for API consumption")
    print("  - SQLite database for SQL queries")
    
    # Example of how you would call it:
    # processor.process_and_export(
    #     queries=["response_time_ms"],
    #     hours_back=6,
    #     export_formats=['csv', 'json', 'sqlite']
    # )


def example_time_ranges():
    """Example with different time ranges"""
    print("\n" + "=" * 60)
    print("Example 5: Different Time Ranges")
    print("=" * 60)
    
    print("Time range options:")
    print("  - hours_back=1   : Last 1 hour of data")
    print("  - hours_back=24  : Last 24 hours of data")
    print("  - hours_back=168 : Last week of data")
    print("  - hours_back=720 : Last month of data")
    
    print("\nFor large time ranges, consider:")
    print("  - Using larger step intervals (e.g., '5m', '1h')")
    print("  - Processing data in chunks")
    print("  - Using SQLite export for better performance")


def show_output_structure():
    """Show the structure of output files"""
    print("\n" + "=" * 60)
    print("Output File Structure")
    print("=" * 60)
    
    print("CSV Files:")
    print("  - alert_type,label_instance,label_job,metric_name,timestamp,value")
    print("  - Easy to import into Excel or other spreadsheet tools")
    
    print("\nJSON Files:")
    print("  - Hierarchical structure with full metadata")
    print("  - Suitable for API consumption or further processing")
    
    print("\nSQLite Database:")
    print("  - Normalized tables: normal_data, alert_data")
    print("  - Supports SQL queries for complex analysis")
    print("  - Example query: SELECT * FROM alert_data WHERE value > 90")


def main():
    """Run all examples"""
    print("VMSelect Data Processor - Usage Examples")
    print("This script shows different ways to use the processor.")
    print("Note: Examples require a running VMSelect instance to work.")
    
    # Show configuration examples
    example_basic_usage()
    example_advanced_thresholds()
    example_custom_queries()
    example_multiple_datastores()
    example_time_ranges()
    show_output_structure()
    
    print("\n" + "=" * 60)
    print("Getting Started")
    print("=" * 60)
    print("1. Install dependencies: pip install -r requirements_simple.txt")
    print("2. Configure your VMSelect URL in the script")
    print("3. Modify thresholds and queries for your metrics")
    print("4. Run: python example_usage.py")
    print("5. Check the output/ directory for exported data")


if __name__ == "__main__":
    main()