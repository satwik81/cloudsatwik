#!/usr/bin/env python3
"""
Test script for VMSelect Data Processor (Simplified Version)

This script tests the functionality without requiring a live VMSelect instance
or external dependencies like requests.
"""

import json
import os
import sys
from datetime import datetime, timedelta

# Import our classes but avoid the VMSelectClient since we don't have requests
from vmselect_data_processor_simple import (
    ThresholdConfig, DataProcessor, DataExporter
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
                    [1705584180, '91.2'],  # 2024-01-18 12:03:00 - Alert!
                    [1705584240, '77.8'],  # 2024-01-18 12:04:00
                ]
            },
            {
                'metric': {'__name__': 'memory_usage_percent', 'instance': 'server1', 'job': 'node_exporter'},
                'values': [
                    [1705584000, '65.2'],
                    [1705584060, '70.1'],
                    [1705584120, '85.3'],
                    [1705584180, '92.7'],  # Alert!
                    [1705584240, '88.9'],
                ]
            },
            {
                'metric': {'__name__': 'disk_usage_percent', 'instance': 'server2', 'job': 'node_exporter'},
                'values': [
                    [1705584000, '45.0'],
                    [1705584060, '47.2'],
                    [1705584120, '89.1'],  # Alert!
                    [1705584180, '90.5'],  # Alert!
                    [1705584240, '82.3'],
                ]
            }
        ]
    }


def test_data_processor():
    """Test the DataProcessor class with mock data"""
    print("Testing DataProcessor...")
    
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
    
    # Create processor
    processor = DataProcessor(thresholds)
    
    # Process mock data
    mock_data = create_mock_vmselect_data()
    result = processor.process_vmselect_data(mock_data)
    
    print(f"✓ Normal data points: {len(result['normal'])}")
    print(f"✓ Alert data points: {len(result['alerts'])}")
    
    # Verify some data
    assert len(result['normal']) > 0, "Should have normal data points"
    assert len(result['alerts']) > 0, "Should have alert data points"
    
    # Check that alerts have the expected fields
    for alert in result['alerts']:
        assert 'alert_type' in alert, "Alert should have alert_type field"
        assert 'timestamp' in alert, "Alert should have timestamp field"
        assert 'metric_name' in alert, "Alert should have metric_name field"
        assert 'value' in alert, "Alert should have value field"
    
    print("✓ DataProcessor test passed!")
    return result


def test_data_exporter(test_data):
    """Test the DataExporter class"""
    print("\nTesting DataExporter...")
    
    # Create exporter with test output directory
    test_output_dir = "test_output"
    exporter = DataExporter(test_output_dir)
    
    # Test CSV export
    exporter.export_to_csv(test_data['normal'], "test_normal.csv")
    exporter.export_to_csv(test_data['alerts'], "test_alerts.csv")
    print("✓ CSV export completed")
    
    # Test JSON export
    exporter.export_to_json(test_data['normal'], "test_normal.json")
    exporter.export_to_json(test_data['alerts'], "test_alerts.json")
    print("✓ JSON export completed")
    
    # Test SQLite export
    exporter.export_to_sqlite(test_data['normal'], "test_metrics.db", "normal_data")
    exporter.export_to_sqlite(test_data['alerts'], "test_metrics.db", "alert_data")
    print("✓ SQLite export completed")
    
    # Verify files were created
    expected_files = [
        "test_normal.csv", "test_alerts.csv",
        "test_normal.json", "test_alerts.json",
        "test_metrics.db"
    ]
    
    for filename in expected_files:
        filepath = os.path.join(test_output_dir, filename)
        assert os.path.exists(filepath), f"File {filepath} should exist"
        assert os.path.getsize(filepath) > 0, f"File {filepath} should not be empty"
    
    print("✓ All export files created successfully")
    print(f"✓ Files saved in: {test_output_dir}/")
    
    # List the files for verification
    print("\nCreated files:")
    for filename in os.listdir(test_output_dir):
        filepath = os.path.join(test_output_dir, filename)
        size = os.path.getsize(filepath)
        print(f"  - {filename} ({size} bytes)")


def test_threshold_checks():
    """Test different threshold configurations"""
    print("\nTesting threshold configurations...")
    
    test_cases = [
        # Greater than threshold
        {
            'config': ThresholdConfig("test_metric", alert_threshold=80, comparison="greater_than"),
            'values': [70, 85, 90],
            'expected_alerts': [85, 90]
        },
        # Less than threshold
        {
            'config': ThresholdConfig("test_metric", alert_threshold=20, comparison="less_than"),
            'values': [30, 15, 10],
            'expected_alerts': [15, 10]
        },
        # Between range (should alert when NOT between min and max)
        {
            'config': ThresholdConfig("test_metric", min_value=20, max_value=80, comparison="between"),
            'values': [10, 50, 90],
            'expected_alerts': [10, 90]
        }
    ]
    
    processor = DataProcessor([])
    
    for i, test_case in enumerate(test_cases):
        config = test_case['config']
        alerts = []
        
        for value in test_case['values']:
            if processor._check_threshold(value, config):
                alerts.append(value)
        
        expected = test_case['expected_alerts']
        assert alerts == expected, f"Test case {i+1} failed: expected {expected}, got {alerts}"
        print(f"✓ Threshold test case {i+1} passed")


def clean_test_files():
    """Clean up test files"""
    test_output_dir = "test_output"
    if os.path.exists(test_output_dir):
        import shutil
        shutil.rmtree(test_output_dir)
        print(f"✓ Cleaned up test directory: {test_output_dir}")


def main():
    """Run all tests"""
    print("=" * 50)
    print("VMSelect Data Processor - Test Suite")
    print("=" * 50)
    
    try:
        # Test threshold logic
        test_threshold_checks()
        
        # Test data processing
        processed_data = test_data_processor()
        
        # Test data export
        test_data_exporter(processed_data)
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        
        # Show summary
        print(f"\nSummary:")
        print(f"- Processed {len(processed_data['normal'])} normal data points")
        print(f"- Detected {len(processed_data['alerts'])} alert conditions")
        print(f"- Exported data to CSV, JSON, and SQLite formats")
        print(f"- All threshold configurations working correctly")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    
    finally:
        # Clean up test files
        clean_test_files()


if __name__ == "__main__":
    exit(main())