#!/usr/bin/env python3
"""
Configuration example for VMSelect Data Processor

Copy this file to config.py and modify the values according to your setup.
"""

from vmselect_data_processor import VMSelectConfig, ThresholdConfig

# VMSelect Configuration
VMSELECT_CONFIG = VMSelectConfig(
    base_url="http://localhost:8481",  # Your VMSelect URL
    query_timeout=60,
    headers={
        'Content-Type': 'application/json',
        # Add authentication headers if needed
        # 'Authorization': 'Bearer your-token',
        # 'X-API-Key': 'your-api-key'
    }
)

# Threshold Configurations
THRESHOLDS = [
    # CPU metrics
    ThresholdConfig(
        metric_name="cpu_usage_percent",
        min_value=0,
        max_value=100,
        alert_threshold=80
    ),
    ThresholdConfig(
        metric_name="cpu_load_average",
        min_value=0,
        max_value=None,  # No upper limit
        alert_threshold=5.0
    ),
    
    # Memory metrics
    ThresholdConfig(
        metric_name="memory_usage_percent",
        min_value=0,
        max_value=100,
        alert_threshold=85
    ),
    ThresholdConfig(
        metric_name="memory_available_bytes",
        min_value=0,
        max_value=None,
        alert_threshold=1073741824  # 1GB in bytes
    ),
    
    # Disk metrics
    ThresholdConfig(
        metric_name="disk_usage_percent",
        min_value=0,
        max_value=100,
        alert_threshold=90
    ),
    ThresholdConfig(
        metric_name="disk_free_bytes",
        min_value=0,
        max_value=None,
        alert_threshold=5368709120  # 5GB in bytes
    ),
    
    # Network metrics
    ThresholdConfig(
        metric_name="network_bytes_total",
        min_value=0,
        max_value=None,
        alert_threshold=None  # No alerts for this metric
    ),
    
    # Custom application metrics
    ThresholdConfig(
        metric_name="response_time_seconds",
        min_value=0,
        max_value=60,  # Max 60 seconds
        alert_threshold=5.0  # Alert if response time > 5 seconds
    ),
    ThresholdConfig(
        metric_name="error_rate_percent",
        min_value=0,
        max_value=100,
        alert_threshold=5.0  # Alert if error rate > 5%
    )
]

# PromQL Queries to execute
QUERIES = [
    # System metrics
    'cpu_usage_percent{job="node_exporter"}',
    'memory_usage_percent{job="node_exporter"}',
    'disk_usage_percent{job="node_exporter"}',
    
    # Application metrics
    'http_requests_total{job="app"}',
    'http_request_duration_seconds{job="app"}',
    'up{job="app"}',
    
    # Database metrics
    'mysql_up{job="mysql"}',
    'mysql_global_status_threads_connected{job="mysql"}',
    
    # Custom business metrics
    'business_metric_orders_per_minute',
    'business_metric_revenue_usd'
]

# Export settings
EXPORT_SETTINGS = {
    'output_directory': 'exports',
    'export_formats': ['csv', 'json', 'sqlite'],
    'separate_alerts': True,
    'timestamp_format': '%Y%m%d_%H%M%S'
}

# Time range settings (can be overridden when calling run_pipeline)
TIME_SETTINGS = {
    'default_range_hours': 24,  # Default to last 24 hours
    'step_seconds': 60  # 1 minute step
}