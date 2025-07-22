# Data Processing Configuration System

A configurable data processing system that reads data from various sources, applies threshold-based filtering, and exports matching data to separate destinations.

## Features

- **Multiple Data Sources**: PostgreSQL, CSV files, REST APIs
- **Flexible Threshold Processing**: Support for various comparison operators and conditions
- **Multiple Export Destinations**: PostgreSQL, REST APIs, S3, Redis
- **Asynchronous Processing**: High-performance async data processing
- **Configurable Rules**: YAML-based configuration for easy management
- **Logging & Monitoring**: Comprehensive logging and error handling

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Your Data Pipeline**
   Edit `config.yaml` to define your datasources, processing rules, and export targets.

3. **Run the Processor**
   ```bash
   # Single run
   python data_processor.py
   
   # Continuous mode (runs every 60 seconds)
   python data_processor.py --continuous
   
   # Custom interval (runs every 30 seconds)
   python data_processor.py --continuous --interval 30
   
   # Custom config file
   python data_processor.py --config my_config.yaml
   ```

## Configuration

### Data Sources

Supported datasource types:

- **PostgreSQL**: Query database tables
- **CSV**: Read from local or network CSV files
- **REST API**: Fetch data from HTTP endpoints

### Processing Rules

Define threshold-based filtering rules:

- **Simple Thresholds**: `greater_than`, `less_than`, `equals`, etc.
- **Complex Conditions**: Multiple AND conditions
- **Time-based**: Filter records within time windows

### Export Destinations

Send processed data to:

- **PostgreSQL**: Insert into database tables
- **REST API**: POST to HTTP endpoints
- **S3**: Upload as files (Parquet, CSV, JSON)
- **Redis**: Store as hashes, lists, or strings

## Example Configuration

```yaml
datasources:
  my_database:
    type: "postgresql"
    host: "localhost"
    port: 5432
    database: "analytics"
    username: "user"
    password: "password"
    query: "SELECT * FROM metrics WHERE created_at > NOW() - INTERVAL '1 hour'"

processing_rules:
  - name: "high_value_alerts"
    description: "Alert on high value records"
    threshold_field: "value"
    threshold_type: "greater_than"
    threshold_value: 1000
    export_target: "alert_api"

export_targets:
  alert_api:
    type: "rest_api"
    url: "https://alerts.example.com/api/alerts"
    method: "POST"
    headers:
      Authorization: "Bearer your_token"
```

## Project Structure

```
├── config.yaml                 # Main configuration file
├── data_processor.py           # Main processor application
├── requirements.txt            # Python dependencies
├── connectors/                 # Data connectors
│   ├── base.py                # Abstract base classes
│   ├── datasource_factory.py  # Datasource factory
│   ├── export_factory.py      # Export factory
│   ├── sources/               # Data source implementations
│   └── exporters/             # Export implementations
└── utils/                     # Utilities
    ├── threshold_processor.py  # Threshold processing logic
    └── logger.py              # Logging configuration
```

## Extending the System

### Adding New Data Sources

1. Create a new class inheriting from `DataSource`
2. Implement the `get_data()` and `test_connection()` methods
3. Register in `DataSourceFactory`

### Adding New Export Destinations

1. Create a new class inheriting from `DataExporter`
2. Implement the `export_data()` and `test_connection()` methods
3. Register in `ExportFactory`

## Error Handling

The system includes comprehensive error handling:

- Connection failures are logged and retried
- Invalid configurations are validated at startup
- Processing errors don't stop the entire pipeline
- Detailed logging for troubleshooting

## Performance

- Asynchronous processing for high throughput
- Configurable batch sizes for memory management
- Parallel data collection from multiple sources
- Connection pooling for database operations

## License

This project is open source and available under the MIT License.