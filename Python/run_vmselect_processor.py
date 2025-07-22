#!/usr/bin/env python3
"""
Simple script to run the VMSelect Data Processor

Usage:
    python run_vmselect_processor.py
    python run_vmselect_processor.py --config config.py
    python run_vmselect_processor.py --hours 6 --base-url http://your-vmselect:8481
"""

import argparse
import sys
import json
from datetime import datetime, timedelta
from vmselect_data_processor import VMSelectDataProcessor, VMSelectConfig, ThresholdConfig


def create_default_config():
    """Create default configuration if no config file is provided"""
    vmselect_config = VMSelectConfig(
        base_url="http://localhost:8481",
        query_timeout=60
    )
    
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
    
    queries = [
        'up',  # Simple availability check
        'cpu_usage{job="node_exporter"}',
        'memory_usage{job="node_exporter"}'
    ]
    
    return vmselect_config, thresholds, queries


def load_config_from_file(config_file):
    """Load configuration from a Python config file"""
    import importlib.util
    
    spec = importlib.util.spec_from_file_location("config", config_file)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    
    return (
        config_module.VMSELECT_CONFIG,
        config_module.THRESHOLDS,
        config_module.QUERIES
    )


def main():
    parser = argparse.ArgumentParser(description='VMSelect Data Processor')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--base-url', help='VMSelect base URL')
    parser.add_argument('--hours', type=int, default=1, help='Hours of data to fetch (default: 1)')
    parser.add_argument('--queries', nargs='+', help='Custom PromQL queries')
    parser.add_argument('--output-dir', default='exports', help='Output directory for exports')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Load configuration
        if args.config:
            print(f"Loading configuration from {args.config}")
            vmselect_config, thresholds, queries = load_config_from_file(args.config)
        else:
            print("Using default configuration")
            vmselect_config, thresholds, queries = create_default_config()
        
        # Override with command line arguments
        if args.base_url:
            vmselect_config.base_url = args.base_url
        
        if args.queries:
            queries = args.queries
        
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=args.hours)
        
        print(f"VMSelect URL: {vmselect_config.base_url}")
        print(f"Time range: {start_time.isoformat()} to {end_time.isoformat()}")
        print(f"Queries to execute: {len(queries)}")
        print(f"Thresholds configured: {len(thresholds)}")
        
        # Initialize and run processor
        processor = VMSelectDataProcessor(vmselect_config, thresholds)
        
        # Override output directory if specified
        if args.output_dir != 'exports':
            processor.exporter.output_dir = args.output_dir
            import os
            os.makedirs(args.output_dir, exist_ok=True)
        
        result = processor.run_pipeline(
            queries,
            start_time=start_time.isoformat() + 'Z',
            end_time=end_time.isoformat() + 'Z'
        )
        
        if 'error' in result:
            print(f"❌ Pipeline failed: {result['error']}")
            sys.exit(1)
        
        # Display results
        stats = result['statistics']
        print("\n" + "="*50)
        print("📊 PROCESSING RESULTS")
        print("="*50)
        print(f"📈 Total records processed: {stats['total_records']}")
        print(f"✅ Records after filtering: {stats['filtered_records']}")
        print(f"🚨 Alert records: {stats['alert_records']}")
        print(f"📋 Unique metrics: {stats['unique_metrics']}")
        
        if stats['time_range']['start']:
            print(f"⏰ Data time range: {stats['time_range']['start']} to {stats['time_range']['end']}")
        
        print("\n📁 EXPORTED FILES:")
        exports = result['exports']
        
        # All data exports
        if 'all_data' in exports:
            print("  📊 All Data:")
            for format_type, filepath in exports['all_data'].items():
                print(f"    {format_type.upper()}: {filepath}")
        
        # Alert exports
        if 'alerts' in exports and exports['alerts']:
            print("  🚨 Alerts Only:")
            for format_type, filepath in exports['alerts'].items():
                print(f"    {format_type.upper()}: {filepath}")
        else:
            print("  ✅ No alerts generated")
        
        print("\n✅ Processing completed successfully!")
        
    except KeyboardInterrupt:
        print("\n❌ Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()