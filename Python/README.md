# VMSelect Data Processor

A comprehensive Python solution for fetching data from VMSelect, applying configurable thresholds, and exporting filtered data to multiple datastores.

## Overview

This toolkit provides a complete solution for:
- 🔍 **Fetching data from VMSelect** using PromQL queries
- 📊 **Applying configurable thresholds** for data filtering and alerting
- 💾 **Exporting to multiple formats**: CSV, JSON, SQLite
- 🚨 **Separating normal data from alerts** for targeted analysis
- ⚙️ **Flexible configuration** for different monitoring scenarios
- 📝 **Comprehensive logging** and error handling

## Features

### Data Processing
- Executes PromQL queries against VMSelect API
- Processes time-series data with configurable time ranges
- Applies multiple threshold types: greater_than, less_than, between, outside
- Separates normal metrics from alert conditions
- Handles metric labels and metadata preservation

### Export Formats
- **CSV**: Easy import into spreadsheets and analysis tools
- **JSON**: Structured data for API consumption
- **SQLite**: Relational database for complex queries

### Threshold Types
- **Greater Than**: Alert when value exceeds threshold
- **Less Than**: Alert when value falls below threshold
- **Between**: Alert when value is NOT within specified range
- **Outside**: Alert when value is outside specified range

## Files Structure

```
Python/
├── vmselect_data_processor_simple.py    # Main processor (no pandas dependency)
├── test_simple_processor.py             # Test suite
├── example_usage.py                     # Usage examples
├── requirements_simple.txt              # Minimal dependencies
└── README.md                           # This file
```

## Quick Start

### 1. Install Dependencies

```bash
# For Python environments that allow pip
pip install requests

# Or use the requirements file
pip install -r requirements_simple.txt
```

### 2. Basic Usage

```python
from vmselect_data_processor_simple import (
    VMSelectConfig, ThresholdConfig, VMSelectDataProcessor
)

# Configure VMSelect connection
vmselect_config = VMSelectConfig(
    base_url="http://your-vmselect:8481",
    query_timeout=60
)

# Define thresholds
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

# Create processor
processor = VMSelectDataProcessor(vmselect_config, thresholds)

# Process and export data
result = processor.process_and_export(
    queries=["cpu_usage_percent", "memory_usage_percent"],
    hours_back=1,
    export_formats=['csv', 'json', 'sqlite']
)

print(f"Normal data points: {result['normal_count']}")
print(f"Alert data points: {result['alert_count']}")
```

### 3. Run Tests

```bash
python3 test_simple_processor.py
```

### 4. View Examples

```bash
python3 example_usage.py
```

## Configuration

### VMSelect Configuration

```python
vmselect_config = VMSelectConfig(
    base_url="http://localhost:8481",
    query_timeout=60,
    headers={
        'Content-Type': 'application/json',
        # Add authentication if needed:
        'Authorization': 'Bearer your-token',
        'X-API-Key': 'your-api-key'
    }
)
```

### Threshold Configuration Examples

```python
# CPU usage alert when > 80%
ThresholdConfig(
    metric_name="cpu_usage_percent",
    alert_threshold=80.0,
    comparison="greater_than"
)

# Disk space alert when < 10%
ThresholdConfig(
    metric_name="disk_free_percent", 
    alert_threshold=10.0,
    comparison="less_than"
)

# Network latency alert when outside 1-100ms range
ThresholdConfig(
    metric_name="network_latency_ms",
    min_value=1.0,
    max_value=100.0,
    comparison="outside"
)

# Temperature alert when NOT between 10-70°C
ThresholdConfig(
    metric_name="server_temperature_celsius",
    min_value=10.0,
    max_value=70.0, 
    comparison="between"
)
```

## PromQL Query Examples

```python
queries = [
    # Simple metric queries
    "cpu_usage_percent",
    "memory_usage_percent",
    
    # Aggregated queries
    "avg(cpu_usage_percent) by (instance)",
    
    # Rate calculations
    "rate(memory_usage_bytes[5m])",
    "rate(disk_io_operations_total[1m])",
    
    # Complex aggregations
    "sum(rate(network_bytes_total[5m])) by (device)",
    
    # Error rate calculations
    "rate(http_requests_total{status=~'5..'}[5m]) / rate(http_requests_total[5m]) * 100"
]
```

## Output Format

### CSV Files
```csv
alert_type,label_instance,label_job,metric_name,timestamp,value
high_threshold,server1,node_exporter,cpu_usage,2024-01-18T12:03:00,91.2
high_threshold,server1,node_exporter,memory_usage_percent,2024-01-18T12:03:00,92.7
```

### JSON Files
```json
[
  {
    "timestamp": "2024-01-18T12:03:00",
    "metric_name": "cpu_usage",
    "value": 91.2,
    "labels": {
      "instance": "server1",
      "job": "node_exporter"
    },
    "alert_type": "high_threshold"
  }
]
```

### SQLite Database
```sql
-- Query normal data
SELECT * FROM normal_data WHERE metric_name = 'cpu_usage_percent';

-- Query alerts with high values
SELECT * FROM alert_data WHERE value > 90;

-- Count alerts by metric
SELECT metric_name, COUNT(*) as alert_count 
FROM alert_data 
GROUP BY metric_name;
```

## Advanced Usage

### Custom Time Ranges

```python
# Last hour
processor.process_and_export(queries, hours_back=1)

# Last day
processor.process_and_export(queries, hours_back=24)

# Last week
processor.process_and_export(queries, hours_back=168)
```

### Multiple Export Formats

```python
# Export to all formats
processor.process_and_export(
    queries=queries,
    export_formats=['csv', 'json', 'sqlite']
)

# Export only to JSON
processor.process_and_export(
    queries=queries,
    export_formats=['json']
)
```

### Custom Output Directory

```python
processor = VMSelectDataProcessor(
    vmselect_config=config,
    thresholds=thresholds,
    output_dir="custom_output_directory"
)
```

## Error Handling

The system includes comprehensive error handling for:
- VMSelect connection failures
- Invalid PromQL queries
- Data processing errors
- File export failures
- Threshold configuration errors

All errors are logged with detailed information for troubleshooting.

## Performance Considerations

### For Large Datasets
- Use larger step intervals (e.g., '5m', '1h') for long time ranges
- Process data in smaller time chunks
- Use SQLite export for better performance with large datasets
- Consider limiting the number of series returned by queries

### Memory Usage
- The simplified version uses minimal memory by processing data in streaming fashion
- For very large datasets, consider implementing data pagination

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```
   Error: Connection refused to localhost:8481
   ```
   - Verify VMSelect is running and accessible
   - Check the base_url configuration
   - Verify network connectivity and firewall settings

2. **Authentication Errors**
   ```
   Error: 401 Unauthorized
   ```
   - Add proper authentication headers to VMSelectConfig
   - Verify API keys or tokens are valid

3. **Query Errors**
   ```
   Error: Query failed: invalid query
   ```
   - Validate PromQL syntax
   - Verify metric names exist in your VMSelect instance
   - Check time range parameters

4. **No Data Returned**
   - Verify metrics exist in the specified time range
   - Check if metric names match exactly
   - Ensure step interval is appropriate for the time range

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Dependencies

- `requests`: HTTP client for VMSelect API
- `sqlite3`: Built-in SQLite support
- `csv`, `json`: Built-in Python modules
- `datetime`, `logging`: Built-in Python modules

## License

This project is provided as-is for educational and development purposes.

## Contributing

To extend the functionality:
1. Add new threshold comparison types in `DataProcessor._check_threshold()`
2. Add new export formats in `DataExporter`
3. Add authentication methods in `VMSelectClient`
4. Add data transformation methods in `DataProcessor`

## Support

For issues or questions:
1. Check the test suite for examples: `python3 test_simple_processor.py`
2. Review the usage examples: `python3 example_usage.py`
3. Enable debug logging for detailed error information