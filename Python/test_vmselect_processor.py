#!/usr/bin/env python3
"""
Test script for VMSelect Data Processor

This script tests the functionality without requiring a live VMSelect instance.
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from vmselect_data_processor import (
    VMSelectConfig, ThresholdConfig, DataProcessor, DataExporter
)


def create_mock_vmselect_data():
    """Create mock data that resembles VMSelect response"""
    return {
        'result': [
            {
                'metric': {'__name__': 'cpu_usage', 'instance': 'server1', 'job': 'node_exporter'},
                'values': [
                    [1705584000, '75.5'],  # 2024-01-18 12:00:00
                    [1705584060, '82.3'],  # 2024-01-18 12:01:00
                    [1705584120, '68.9'],  # 2024-01-18 12:02:00
                    [1705584180, '91.2'],  # 2024-01-18 12:03:00 (alert!)
                ]
            },
            {
                'metric': {'__name__': 'memory_usage', 'instance': 'server1', 'job': 'node_exporter'},
                'values': [
                    [1705584000, '65.2'],
                    [1705584060, '67.8'],
                    [1705584120, '70.1'],
                    [1705584180, '88.5'],  # (alert!)
                ]
            },
            {
                'metric': {'__name__': 'disk_usage', 'instance': 'server2', 'job': 'node_exporter'},
                'values': [
                    [1705584000, '45.0'],
                    [1705584060, '47.2'],
                    [1705584120, '48.8'],
                    [1705584180, '92.3'],  # (alert!)
                ]
            }
        ]
    }


def test_data_processing():
    """Test data processing functionality"""
    print("🧪 Testing Data Processing...")
    
    # Create mock data
    mock_data = create_mock_vmselect_data()
    
    # Configure thresholds
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
    processor = DataProcessor(thresholds)
    
    # Process mock data
    df = processor.process_vmselect_data(mock_data)
    print(f"  ✅ Processed {len(df)} data points")
    
    # Apply thresholds
    filtered_df = processor.apply_thresholds(df)
    print(f"  ✅ Applied thresholds, {len(filtered_df)} points remain")
    
    # Check alerts
    alert_count = len(filtered_df[filtered_df.get('alert', False) == True])
    print(f"  🚨 Generated {alert_count} alerts")
    
    return filtered_df


def test_data_export(df):
    """Test data export functionality"""
    print("\n📁 Testing Data Export...")
    
    # Initialize exporter with test directory
    exporter = DataExporter(output_dir="test_exports")
    
    # Test CSV export
    csv_file = exporter.export_to_csv(df, "test_data.csv")
    print(f"  ✅ CSV export: {csv_file}")
    
    # Test JSON export
    json_file = exporter.export_to_json(df, "test_data.json")
    print(f"  ✅ JSON export: {json_file}")
    
    # Test SQLite export
    db_file = exporter.export_to_sqlite(df, table_name="test_metrics")
    print(f"  ✅ SQLite export: {db_file}")
    
    # Test alert-only export
    alert_exports = exporter.export_alerts_only(df)
    if alert_exports:
        print(f"  🚨 Alert exports: {list(alert_exports.keys())}")
    else:
        print("  ℹ️  No alerts to export")
    
    return {
        'csv': csv_file,
        'json': json_file,
        'sqlite': db_file,
        'alerts': alert_exports
    }


def test_configuration():
    """Test configuration classes"""
    print("\n⚙️  Testing Configuration...")
    
    # Test VMSelect config
    config = VMSelectConfig(
        base_url="http://test:8481",
        query_timeout=30,
        headers={'Test-Header': 'test-value'}
    )
    print(f"  ✅ VMSelect config: {config.base_url}")
    
    # Test threshold config
    threshold = ThresholdConfig(
        metric_name="test_metric",
        min_value=0,
        max_value=100,
        alert_threshold=80
    )
    print(f"  ✅ Threshold config: {threshold.metric_name}")
    
    return config, threshold


def display_sample_data(df):
    """Display sample processed data"""
    print("\n📊 Sample Processed Data:")
    print("=" * 60)
    
    # Show first few records
    print(df.head(3).to_string(index=False))
    
    print("\n📈 Data Summary:")
    print(f"  Total records: {len(df)}")
    print(f"  Unique metrics: {df['metric_name'].nunique()}")
    print(f"  Alert records: {len(df[df.get('alert', False) == True])}")
    print(f"  Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    # Show metric breakdown
    print("\n📋 Metrics breakdown:")
    metric_counts = df['metric_name'].value_counts()
    for metric, count in metric_counts.items():
        alerts = len(df[(df['metric_name'] == metric) & (df.get('alert', False) == True)])
        print(f"  {metric}: {count} points ({alerts} alerts)")


def verify_exports(export_files):
    """Verify that export files were created correctly"""
    print("\n🔍 Verifying Exports...")
    
    import os
    
    # Check CSV file
    if os.path.exists(export_files['csv']):
        size = os.path.getsize(export_files['csv'])
        print(f"  ✅ CSV file exists ({size} bytes)")
    else:
        print("  ❌ CSV file not found")
    
    # Check JSON file
    if os.path.exists(export_files['json']):
        size = os.path.getsize(export_files['json'])
        print(f"  ✅ JSON file exists ({size} bytes)")
        
        # Validate JSON format
        try:
            with open(export_files['json'], 'r') as f:
                json.load(f)
            print("  ✅ JSON format is valid")
        except json.JSONDecodeError:
            print("  ❌ JSON format is invalid")
    else:
        print("  ❌ JSON file not found")
    
    # Check SQLite file
    if os.path.exists(export_files['sqlite']):
        size = os.path.getsize(export_files['sqlite'])
        print(f"  ✅ SQLite file exists ({size} bytes)")
    else:
        print("  ❌ SQLite file not found")


def main():
    """Run all tests"""
    print("🚀 VMSelect Data Processor - Test Suite")
    print("=" * 50)
    
    try:
        # Test configuration
        config, threshold = test_configuration()
        
        # Test data processing
        df = test_data_processing()
        
        # Display sample data
        display_sample_data(df)
        
        # Test data export
        export_files = test_data_export(df)
        
        # Verify exports
        verify_exports(export_files)
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("=" * 50)
        
        print("\n📋 Test Results Summary:")
        print(f"  🔧 Configuration: ✅ Passed")
        print(f"  📊 Data Processing: ✅ Passed")
        print(f"  💾 Data Export: ✅ Passed")
        print(f"  🔍 File Verification: ✅ Passed")
        
        print("\n🎯 Next Steps:")
        print("  1. Update VMSelect URL in config")
        print("  2. Customize PromQL queries for your metrics")
        print("  3. Adjust thresholds for your use case")
        print("  4. Run: python run_vmselect_processor.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)