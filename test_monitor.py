#!/usr/bin/env python3
"""
Test script for the Threshold Monitor system.
This script validates the configuration and can be used to test the monitoring system.
"""

import yaml
import time
import json
from pathlib import Path
from threshold_monitor import ConfigManager, DataCollector, ThresholdChecker


def test_config():
    """Test configuration loading."""
    print("Testing configuration loading...")
    try:
        config_manager = ConfigManager()
        config = config_manager.config
        print(f"✓ Configuration loaded successfully")
        print(f"  - Data sources: {len(config['data_sources'])}")
        print(f"  - Threshold rules: {len(config['threshold_rules'])}")
        print(f"  - Export enabled: {config['export_settings']['enabled']}")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def test_data_collection():
    """Test data collection from system metrics."""
    print("\nTesting data collection...")
    collector = DataCollector()
    
    try:
        # Test CPU usage
        cpu_data = collector.collect_system_metric("psutil.cpu_percent")
        print(f"✓ CPU data: {cpu_data}")
        
        # Test memory usage
        mem_data = collector.collect_system_metric("psutil.virtual_memory")
        print(f"✓ Memory data: {mem_data}")
        
        # Test disk usage
        disk_data = collector.collect_system_metric("psutil.disk_usage", path="/")
        print(f"✓ Disk data: {disk_data}")
        
        return True
    except Exception as e:
        print(f"✗ Data collection error: {e}")
        return False


def test_threshold_checking():
    """Test threshold checking logic."""
    print("\nTesting threshold checking...")
    checker = ThresholdChecker()
    
    # Test rule
    rule = {
        "data_source": "test",
        "metric_name": "test_value",
        "threshold_type": "greater_than",
        "threshold_value": 50.0,
        "consecutive_violations": 1
    }
    
    # Test data below threshold
    data_low = {"test_value": 30.0}
    result1 = checker.check_threshold(rule, data_low)
    print(f"✓ Below threshold (30.0 > 50.0): {result1} (expected: False)")
    
    # Test data above threshold
    data_high = {"test_value": 80.0}
    result2 = checker.check_threshold(rule, data_high)
    print(f"✓ Above threshold (80.0 > 50.0): {result2} (expected: True)")
    
    return result1 == False and result2 == True


def create_test_config():
    """Create a test configuration with lower thresholds for testing."""
    test_config = {
        "data_sources": [
            {
                "name": "cpu_usage",
                "type": "system_metric",
                "source": "psutil.cpu_percent",
                "interval": 2,
                "enabled": True
            }
        ],
        "threshold_rules": [
            {
                "data_source": "cpu_usage",
                "metric_name": "cpu_percent",
                "threshold_type": "greater_than",
                "threshold_value": 0.1,  # Very low threshold for testing
                "consecutive_violations": 1,
                "enabled": True
            }
        ],
        "export_settings": {
            "enabled": True,
            "export_formats": ["json"],
            "export_directory": "./test_exports",
            "max_export_files": 10,
            "compress_exports": False,
            "destinations": [
                {
                    "type": "file",
                    "enabled": True
                }
            ]
        },
        "logging": {
            "level": "INFO",
            "file": "./test_logs/monitor.log",
            "max_size_mb": 1,
            "backup_count": 2
        },
        "monitoring": {
            "max_workers": 2,
            "check_interval": 1,
            "data_retention_hours": 1
        }
    }
    
    with open("test_config.yaml", "w") as f:
        yaml.dump(test_config, f, default_flow_style=False)
    
    print("✓ Created test_config.yaml with low thresholds for easy testing")


def run_short_test():
    """Run a short test of the monitoring system."""
    print("\nRunning short monitoring test (10 seconds)...")
    
    # Create test config
    create_test_config()
    
    # Import and run the monitor with test config
    import threshold_monitor
    
    # Temporarily replace the config path
    original_config_path = "config.yaml"
    threshold_monitor.ConfigManager.__init__ = lambda self, config_path="test_config.yaml": setattr(self, 'config_path', config_path) or setattr(self, 'config', self.load_config())
    
    try:
        from multiprocessing import Process
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Test timeout")
        
        # Set timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second timeout
        
        # Run monitor
        process = Process(target=threshold_monitor.main)
        process.start()
        
        # Wait for test duration
        time.sleep(8)
        
        # Terminate process
        process.terminate()
        process.join(timeout=2)
        
        signal.alarm(0)  # Cancel timeout
        
        print("✓ Short test completed successfully")
        
        # Check if any exports were created
        export_dir = Path("test_exports")
        if export_dir.exists():
            export_files = list(export_dir.glob("*.json"))
            print(f"✓ Created {len(export_files)} export files")
            
            # Show sample export if any
            if export_files:
                with open(export_files[0]) as f:
                    sample_export = json.load(f)
                print(f"✓ Sample export: {sample_export['data_source']}.{sample_export['metric_name']} = {sample_export['value']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Short test error: {e}")
        return False


def main():
    """Run all tests."""
    print("=== Threshold Monitor Test Suite ===")
    
    tests = [
        test_config,
        test_data_collection,
        test_threshold_checking,
        run_short_test
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{len(tests)} tests")
    
    if passed == len(tests):
        print("✓ All tests passed! The monitoring system is ready to use.")
        print("\nTo start monitoring:")
        print("1. Adjust thresholds in config.yaml as needed")
        print("2. Run: python threshold_monitor.py")
    else:
        print("✗ Some tests failed. Please check the configuration and dependencies.")


if __name__ == "__main__":
    main()