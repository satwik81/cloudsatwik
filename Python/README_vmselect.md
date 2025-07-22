# VMSelect Data Processor

A comprehensive Python solution for fetching data from VMSelect, applying thresholds, and exporting filtered data to separate datastores.

## Features

- 🔍 **Fetch data from VMSelect** using PromQL queries
- 📊 **Apply configurable thresholds** for data filtering and alerting
- 💾 **Export to multiple formats**: CSV, JSON, SQLite
- 🚨 **Separate alert handling** with dedicated exports
- ⚙️ **Flexible configuration** via Python files or command line
- 📝 **Comprehensive logging** and error handling
- 🏗️ **Modular architecture** for easy extension

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Make the scripts executable:
```bash
chmod +x vmselect_data_processor.py
chmod +x run_vmselect_processor.py
```

## Quick Start

### Basic Usage

Run with default configuration (connects to localhost:8481):
```bash
python run_vmselect_processor.py
```

### Custom VMSelect URL

```bash
python run_vmselect_processor.py --base-url http://your-vmselect:8481
```

### Fetch specific time range

```bash
python run_vmselect_processor.py --hours 24  # Last 24 hours
```

### Custom queries

```bash
python run_vmselect_processor.py --queries 'up' 'cpu_usage_percent' 'memory_usage_percent'
```

### With custom configuration file

```bash
# Copy and modify the example config
cp config_example.py config.py
# Edit config.py with your settings
python run_vmselect_processor.py --config config.py
```

## Configuration

### VMSelect Configuration

```python
vmselect_config = VMSelectConfig(
    base_url="http://your-vmselect:8481",
    query_timeout=60,
    headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your-token'  # If authentication is required
    }
)
```

### Threshold Configuration

Define thresholds for different metrics:

```python
thresholds = [
    ThresholdConfig(
        metric_name="cpu_usage_percent",
        min_value=0,           # Minimum acceptable value
        max_value=100,         # Maximum acceptable value  
        alert_threshold=80     # Alert if value exceeds this
    ),
    ThresholdConfig(
        metric_name="response_time_seconds",
        min_value=0,
        max_value=60,
        alert_threshold=5.0
    )
]
```

### PromQL Queries

Configure the metrics you want to fetch:

```python
queries = [
    'cpu_usage_percent{job="node_exporter"}',
    'memory_usage_percent{job="node_exporter"}',
    'http_request_duration_seconds{job="app"}',
    'up{job="database"}'
]
```

## API Usage

### Programmatic Usage

```python
from vmselect_data_processor import VMSelectDataProcessor, VMSelectConfig, ThresholdConfig
from datetime import datetime, timedelta

# Configure VMSelect connection
config = VMSelectConfig(base_url="http://localhost:8481")

# Define thresholds
thresholds = [
    ThresholdConfig("cpu_usage", max_value=100, alert_threshold=80)
]

# Initialize processor
processor = VMSelectDataProcessor(config, thresholds)

# Define time range
end_time = datetime.now()
start_time = end_time - timedelta(hours=1)

# Run pipeline
result = processor.run_pipeline(
    queries=['cpu_usage{job="node_exporter"}'],
    start_time=start_time.isoformat() + 'Z',
    end_time=end_time.isoformat() + 'Z'
)

print(result['statistics'])
```

### Individual Components

```python
# Use individual components
from vmselect_data_processor import VMSelectClient, DataProcessor, DataExporter

# Fetch data only
client = VMSelectClient(config)
data = client.query('up', start_time, end_time)

# Process data
processor = DataProcessor(thresholds)
df = processor.process_vmselect_data(data)
filtered_df = processor.apply_thresholds(df)

# Export data
exporter = DataExporter(output_dir="my_exports")
exporter.export_to_csv(filtered_df)
```

## Output Formats

### CSV Export
- Human-readable format
- Easy to import into spreadsheet applications
- Columns: metric_name, timestamp, value, labels, alert

### JSON Export
- Machine-readable format
- Preserves data types
- Easy to consume by other applications

### SQLite Export
- Relational database format
- Supports complex queries
- Can append multiple runs to same database

## File Structure

```
exports/
├── vmselect_data_20240115_143022.csv    # All data
├── vmselect_data_20240115_143022.json   # All data  
├── vmselect_data.db                     # SQLite database
├── alerts_20240115_143022.csv           # Alerts only
├── alerts_20240115_143022.json          # Alerts only
└── alerts table in vmselect_data.db     # Alerts in database
```

## Error Handling

The processor includes comprehensive error handling:

- **Connection errors**: Retries and clear error messages
- **Query errors**: Individual query failures don't stop the pipeline
- **Data processing errors**: Graceful handling of malformed data
- **Export errors**: Detailed error reporting

## Logging

Configure logging levels:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)  # Verbose output
```

Or use the command line:
```bash
python run_vmselect_processor.py --verbose
```

## Advanced Features

### Custom Data Processing

Extend the `DataProcessor` class:

```python
class CustomDataProcessor(DataProcessor):
    def apply_custom_logic(self, df):
        # Your custom processing logic
        return processed_df
```

### Custom Export Formats

Extend the `DataExporter` class:

```python
class CustomDataExporter(DataExporter):
    def export_to_influxdb(self, df):
        # Export to InfluxDB
        pass
    
    def export_to_elasticsearch(self, df):
        # Export to Elasticsearch
        pass
```

### Batch Processing

Process multiple time ranges:

```python
from datetime import datetime, timedelta

# Process last 7 days in daily batches
for i in range(7):
    end_time = datetime.now() - timedelta(days=i)
    start_time = end_time - timedelta(days=1)
    
    result = processor.run_pipeline(
        queries,
        start_time=start_time.isoformat() + 'Z',
        end_time=end_time.isoformat() + 'Z'
    )
```

## Integration Examples

### Cron Job Setup

Add to crontab for regular processing:

```bash
# Run every hour
0 * * * * cd /path/to/vmselect-processor && python run_vmselect_processor.py --hours 1

# Run daily with 24-hour data
0 2 * * * cd /path/to/vmselect-processor && python run_vmselect_processor.py --hours 24
```

### Docker Usage

Create a Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "run_vmselect_processor.py"]
```

### Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: vmselect-processor
spec:
  schedule: "0 */1 * * *"  # Every hour
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: processor
            image: vmselect-processor:latest
            command: ["python", "run_vmselect_processor.py"]
          restartPolicy: OnFailure
```

## Troubleshooting

### Common Issues

1. **Connection refused**: Check VMSelect URL and port
2. **Authentication errors**: Verify headers and credentials
3. **No data returned**: Check PromQL query syntax and time range
4. **Permission denied**: Ensure write permissions for export directory

### Debug Mode

Enable verbose logging to troubleshoot issues:

```bash
python run_vmselect_processor.py --verbose
```

### Testing Connectivity

Test VMSelect connection:

```python
from vmselect_data_processor import VMSelectClient, VMSelectConfig

config = VMSelectConfig(base_url="http://your-vmselect:8481")
client = VMSelectClient(config)

try:
    data = client.query('up')
    print("✅ Connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## Performance Considerations

- **Query optimization**: Use specific label selectors to reduce data volume
- **Time range**: Smaller time ranges process faster
- **Concurrent queries**: The processor handles multiple queries efficiently
- **Memory usage**: Large datasets may require chunked processing

## Security

- Store credentials in environment variables or secure configuration files
- Use HTTPS for VMSelect connections in production
- Restrict file permissions on configuration files
- Consider using authentication tokens with limited scope

## Contributing

To extend the processor:

1. Follow the existing class structure
2. Add comprehensive error handling
3. Include logging statements
4. Update configuration examples
5. Add tests for new functionality

## Dependencies

- `requests`: HTTP client for VMSelect API
- `pandas`: Data processing and manipulation
- `numpy`: Numerical operations (pandas dependency)

## License

This project is provided as-is for educational and practical use.