# Threshold Monitor System

A Python-based multiprocessing system for monitoring data sources and exporting data when threshold rules are violated. The system uses YAML configuration files to define data sources, threshold rules, and export settings.

## Features

- **Multiprocessing Architecture**: Uses Python's multiprocessing to monitor multiple data sources concurrently
- **Configurable Data Sources**: Support for system metrics (CPU, Memory, Disk, Network) and API endpoints
- **Flexible Threshold Rules**: Support for greater_than, less_than, and equals comparisons with consecutive violation tracking
- **Multiple Export Formats**: JSON and CSV export with optional compression
- **Multiple Export Destinations**: File system, webhooks, and email notifications
- **Comprehensive Logging**: Rotating log files with configurable levels
- **Auto-cleanup**: Automatic removal of old export files based on configured limits

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the system by editing `config.yaml`

3. Run the monitoring system:
```bash
python threshold_monitor.py
```

## Configuration

The system is configured through the `config.yaml` file. Here are the main sections:

### Data Sources

Define what data to monitor:

```yaml
data_sources:
  - name: "cpu_usage"
    type: "system_metric"
    source: "psutil.cpu_percent"
    interval: 5  # Check every 5 seconds
    enabled: true
```

Supported data source types:
- **system_metric**: CPU, memory, disk, and network metrics using psutil
- **api_endpoint**: HTTP API endpoints that return JSON data

### Threshold Rules

Define when to trigger exports:

```yaml
threshold_rules:
  - data_source: "cpu_usage"
    metric_name: "cpu_percent"
    threshold_type: "greater_than"
    threshold_value: 80.0
    consecutive_violations: 2  # Must exceed threshold 2 times in a row
    enabled: true
```

Supported threshold types:
- `greater_than`: Trigger when value > threshold
- `less_than`: Trigger when value < threshold
- `equals`: Trigger when value == threshold

### Export Settings

Configure how and where to export data:

```yaml
export_settings:
  enabled: true
  export_formats:
    - "json"
    - "csv"
  export_directory: "./exports"
  max_export_files: 100
  compress_exports: true
  
  destinations:
    - type: "file"
      enabled: true
    - type: "webhook"
      enabled: false
      url: "http://localhost:8081/webhook"
    - type: "email"
      enabled: false
      smtp_server: "smtp.gmail.com"
      # ... email configuration
```

## System Metrics

The system can monitor these built-in system metrics:

- **CPU Usage**: `psutil.cpu_percent` → `cpu_percent`
- **Memory Usage**: `psutil.virtual_memory` → `memory_percent`, `memory_total`, `memory_used`, `memory_available`
- **Disk Usage**: `psutil.disk_usage` → `disk_percent`, `disk_total_gb`, `disk_used_gb`, `disk_free_gb`
- **Network I/O**: `psutil.net_io_counters` → `bytes_sent_per_sec`, `bytes_recv_per_sec`

## Architecture

The system uses a multiprocessing architecture:

1. **Main Process**: Coordinates workers and handles shutdown
2. **Data Source Workers**: One process per enabled data source for concurrent monitoring
3. **Export Worker**: Dedicated process for handling all data exports
4. **Shared Memory**: Inter-process communication via queues and shared dictionaries

```
Main Process
├── Worker-cpu_usage (Process)
├── Worker-memory_usage (Process)
├── Worker-disk_usage (Process)
├── Worker-network_io (Process)
└── ExportWorker (Process)
```

## Usage Examples

### Basic Monitoring

1. Start with the default configuration:
```bash
python threshold_monitor.py
```

2. Monitor logs in real-time:
```bash
tail -f logs/monitor.log
```

### Testing the System

Run the test suite to validate configuration and functionality:

```bash
python test_monitor.py
```

The test script will:
- Validate the YAML configuration
- Test data collection from system metrics
- Test threshold checking logic
- Run a short monitoring session with sample exports

### Custom API Monitoring

Add custom API endpoints to your configuration:

```yaml
data_sources:
  - name: "api_metrics"
    type: "api_endpoint"
    source: "http://your-api.com/metrics"
    interval: 30
    enabled: true

threshold_rules:
  - data_source: "api_metrics"
    metric_name: "response_time_ms"
    threshold_type: "greater_than"
    threshold_value: 1000
    consecutive_violations: 1
    enabled: true
```

### Email Alerts

Configure email notifications for critical thresholds:

```yaml
export_settings:
  destinations:
    - type: "email"
      enabled: true
      smtp_server: "smtp.gmail.com"
      smtp_port: 587
      username: "your-email@gmail.com"
      password: "your-app-password"
      to_addresses:
        - "admin@company.com"
        - "alerts@company.com"
```

## File Structure

```
threshold_monitor/
├── config.yaml              # Main configuration file
├── threshold_monitor.py      # Main monitoring system
├── test_monitor.py          # Test suite
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── exports/                # Export files (created automatically)
├── logs/                   # Log files (created automatically)
└── test_exports/           # Test export files (created by tests)
```

## Export Data Format

When a threshold is violated, the system exports structured data:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "data_source": "cpu_usage",
  "metric_name": "cpu_percent",
  "value": 85.2,
  "threshold_violated": true,
  "threshold_value": 80.0,
  "metadata": {
    "rule": { /* threshold rule details */ },
    "all_metrics": { /* all collected metrics */ },
    "data_source_config": { /* data source configuration */ }
  }
}
```

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure the user has write permissions for the `exports/` and `logs/` directories

2. **Missing Dependencies**: Install all requirements with `pip install -r requirements.txt`

3. **High CPU Usage**: Reduce monitoring frequency by increasing `interval` values in data source configurations

4. **Memory Issues**: Adjust `max_export_files` and enable `compress_exports` to manage disk usage

### Monitoring Performance

- Check `logs/monitor.log` for system status and errors
- Monitor worker processes with `ps aux | grep python`
- Use `htop` or `top` to monitor system resource usage

### Configuration Validation

Use the test script to validate your configuration:

```bash
python test_monitor.py
```

## Advanced Configuration

### Custom Metrics

You can extend the system to support custom metrics by modifying the `DataCollector` class:

```python
def collect_custom_metric(self, source: str, **kwargs) -> Dict[str, Any]:
    # Implement your custom metric collection logic
    return {"custom_value": your_custom_logic()}
```

### Multiple Configuration Files

The system can be run with different configuration files:

```python
config_manager = ConfigManager("production_config.yaml")
```

### Performance Tuning

Adjust these settings for optimal performance:

```yaml
monitoring:
  max_workers: 4              # Number of concurrent data source workers
  check_interval: 1           # Main loop interval (seconds)
  data_retention_hours: 24    # How long to keep monitoring data
```

## License

This project is open source. Feel free to modify and extend it for your needs.