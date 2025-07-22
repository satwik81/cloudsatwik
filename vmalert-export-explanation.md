# How Data Exporting Works in vmalert Rules

## Overview
The data exporting in vmalert rules works through multiple mechanisms that allow you to send metric data to external datastores when specific conditions are met. Here's how it works:

## 1. Export Triggering Mechanisms

### A. Alert-Based Export (Event-Driven)
```yaml
- alert: HighCPUUsage
  expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
  for: 2m
  labels:
    export_to_datastore: "true"  # Triggers export when alert fires
  annotations:
    export_query: 'avg by(instance) (100 - (irate(node_cpu_seconds_total{mode="idle"}[5m]) * 100))'
    export_datastore: "influxdb"
    export_database: "alerts_db"
```

**How it works:**
- Export is triggered ONLY when the alert condition is met (CPU > 80%)
- Data is exported when the alert transitions to "firing" state
- Includes the current metric value and all relevant labels

### B. Recording Rule Export (Continuous)
```yaml
- record: node_cpu_usage_percent
  expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
  labels:
    export_to_datastore: "true"  # Triggers continuous export
  annotations:
    export_interval: "60s"  # Export every 60 seconds
```

**How it works:**
- Continuously evaluates and exports data at specified intervals
- Creates new time series that can be exported to external systems
- Runs regardless of threshold values

### C. Threshold-Based Export (Conditional Recording)
```yaml
- record: high_cpu_threshold_data
  expr: (100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80) * on(instance) group_left() (100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100))
  labels:
    export_to_datastore: "true"
    threshold_type: "cpu_high"
```

**How it works:**
- Uses boolean logic to export data ONLY when thresholds are breached
- The expression returns the actual value only when condition is true, otherwise 0
- More efficient than continuous export for threshold-based scenarios

## 2. Export Configuration Structure

### Labels for Export Control
```yaml
labels:
  export_to_datastore: "true"     # Master switch for export
  severity: "warning"             # Alert severity level
  threshold_type: "cpu_high"      # Type of threshold breach
```

### Annotations for Export Metadata
```yaml
annotations:
  export_query: 'metric_expression'           # Query to export
  export_datastore: "influxdb"               # Target datastore type
  export_database: "alerts_db"               # Target database
  export_measurement: "cpu_alerts"           # Target measurement/table
  export_interval: "60s"                     # Export frequency (for recording rules)
  threshold_value: "80"                      # Threshold that triggered export
  metric_type: "cpu_usage"                   # Type of metric being exported
```

## 3. Data Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │───▶│     vmalert     │───▶│  Export Agent   │───▶│  External DB    │
│   (Data Source) │    │  (Rule Engine)  │    │  (Webhook/API)  │    │  (InfluxDB/etc) │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Step-by-Step Process:

1. **Metric Evaluation**: vmalert queries Prometheus/VictoriaMetrics every `interval`
2. **Condition Check**: Evaluates rule expressions against current metric values
3. **Export Decision**: Checks if `export_to_datastore: "true"` label is present
4. **Data Preparation**: Formats data according to annotation specifications
5. **Export Execution**: Sends data to configured external datastore

## 4. Implementation Methods

### Method 1: Remote Write (Built-in)
```bash
vmalert -rule.file=vmalert-rules.yaml \
        -datasource.url=http://victoriametrics:8428 \
        -remoteWrite.url=http://influxdb:8086/api/v1/prom/write?db=alerts_db
```

**Pros:**
- Native vmalert feature
- Automatic handling of export logic
- Built-in retry mechanisms

**Cons:**
- Limited to Prometheus remote write protocol
- Less flexibility in data formatting

### Method 2: Webhook Notifications
```bash
vmalert -rule.file=vmalert-rules.yaml \
        -datasource.url=http://victoriametrics:8428 \
        -notifier.url=http://alertmanager:9093
```

**Pros:**
- Maximum flexibility in data processing
- Can transform data format before export
- Supports any target system with API

**Cons:**
- Requires additional webhook service
- More complex setup

### Method 3: External Export Service
```yaml
# Custom export service configuration
annotations:
  webhook_url: "http://export-service:8080/webhook"
  export_format: "json"
  batch_size: "100"
```

## 5. Export Data Format Examples

### Alert Export (JSON format)
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "alert_name": "HighCPUUsage",
  "instance": "server-01",
  "value": 85.4,
  "threshold": 80,
  "severity": "warning",
  "labels": {
    "service": "node_exporter",
    "export_to_datastore": "true"
  },
  "annotations": {
    "summary": "High CPU usage detected on server-01",
    "export_database": "alerts_db",
    "export_measurement": "cpu_alerts"
  }
}
```

### Recording Rule Export (InfluxDB Line Protocol)
```
cpu_usage,instance=server-01,export_to_datastore=true value=85.4 1705317000000000000
memory_usage,instance=server-01,export_to_datastore=true value=78.2 1705317000000000000
```

## 6. Advanced Export Patterns

### Conditional Export with Multiple Thresholds
```yaml
- record: multi_threshold_cpu_data
  expr: |
    (
      (100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90) * 3 +
      (100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80) * 2 +
      (100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 70) * 1
    ) * on(instance) group_left() (100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100))
```

This exports different severity levels (1=warning, 2=high, 3=critical) based on multiple thresholds.

### Batch Export with Aggregation
```yaml
- record: hourly_avg_cpu_export
  expr: avg_over_time(node_cpu_usage_percent[1h])
  labels:
    export_to_datastore: "true"
    export_type: "batch"
  annotations:
    export_interval: "1h"
    export_measurement: "hourly_cpu_avg"
```

## 7. Monitoring Export Success

### Export Metrics
vmalert exposes metrics to monitor export success:
```
vmalert_remotewrite_requests_total
vmalert_remotewrite_errors_total
vmalert_notification_requests_total
vmalert_notification_errors_total
```

### Health Checks
```yaml
- alert: ExportFailure
  expr: increase(vmalert_remotewrite_errors_total[5m]) > 0
  annotations:
    summary: "Data export to external datastore is failing"
```

## 8. Performance Considerations

### Optimization Strategies:
1. **Batch Processing**: Group multiple metrics in single export requests
2. **Selective Export**: Use precise threshold conditions to avoid unnecessary exports
3. **Compression**: Enable compression for network transfers
4. **Buffer Management**: Configure appropriate buffer sizes for high-volume scenarios

### Resource Usage:
- CPU: Proportional to rule complexity and evaluation frequency
- Memory: Depends on batch sizes and number of active exports
- Network: Bandwidth usage scales with export frequency and data volume

This export mechanism provides flexible, efficient data export capabilities that can be tailored to specific monitoring and compliance requirements.