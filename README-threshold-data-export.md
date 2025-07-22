# Threshold-Based Data Export System

This system implements a threshold-based data export mechanism similar to vmalert's alarm triggering, but instead of sending alerts, it exports data to separate datasources when thresholds are met.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Data Source   │    │   vmalert with   │    │   vmagent Router    │
│ (VictoriaMetrics│────│ Recording Rules  │────│                     │
│  or Prometheus) │    │                  │    │                     │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                                         │
                                                         ▼
               ┌─────────────────────────────────────────────────────────┐
               │                 Route Based on Labels                  │
               └─────────────────────────────────────────────────────────┘
                          │              │              │
                          ▼              ▼              ▼
                ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
                │ Incident Storage│ │ Debug Storage│ │Security SIEM    │
                │ (Critical Data) │ │ (Dev Team)   │ │ (Security Team) │
                └─────────────────┘ └─────────────┘ └─────────────────┘
```

## How It Works

### 1. Threshold Detection via Recording Rules

Instead of using alerting rules that trigger notifications, we use **recording rules** that:
- Evaluate expressions against the primary datasource
- Only create new time series when thresholds are exceeded
- Add metadata labels to identify the export target and reason

### 2. Smart Routing via vmagent

vmagent acts as an intelligent router that:
- Scrapes the threshold-triggered metrics from vmalert
- Uses label-based routing to send data to different datasources
- Enriches data with additional metadata during routing

### 3. Multiple Export Destinations

Different types of threshold breaches route to appropriate systems:
- **Critical incidents** → Incident management storage
- **Performance issues** → Debug storage for development teams
- **Security events** → SIEM systems
- **Long-term trends** → Long-term storage with high retention

## Configuration Examples

### Basic CPU Threshold Export

```yaml
- record: high_cpu_usage_export
  expr: 'cpu_usage_percent > 80'
  labels:
    export_reason: "cpu_threshold_exceeded"
    severity: "warning"
    export_target: "separate_ds"
```

### Advanced Predictive Memory Export

```yaml
- record: memory_exhaustion_predicted
  expr: 'predict_linear(memory_used[30m], 3600) / memory_total > 0.95'
  labels:
    export_reason: "memory_exhaustion_predicted"
    severity: "critical"
    export_target: "incident_storage"
    prediction_horizon: "1hour"
```

### VictoriaLogs Integration for Log Thresholds

```yaml
- record: error_spike_with_context
  expr: |
    _time:5m | filter level="error" 
    | stats by (service, container) count() as error_count 
    | filter error_count > 50
  labels:
    export_reason: "error_spike_detected"
    severity: "warning"
    export_target: "log_analysis_ds"
```

## Key Features

### 1. Multi-Datasource Support
- **VictoriaMetrics/Prometheus**: Metrics-based thresholds
- **VictoriaLogs**: Log-based thresholds using LogsQL
- **Mixed environments**: Support for both simultaneously

### 2. Intelligent Routing
- **Label-based routing**: Route based on `export_target`, `severity`, etc.
- **Multiple destinations**: Send same data to multiple endpoints
- **Metadata enrichment**: Add routing information, timestamps, etc.

### 3. Flexible Threshold Types
- **Static thresholds**: Simple value comparisons
- **Predictive thresholds**: Using `predict_linear()` for forecasting
- **Comparative thresholds**: Compare against historical data
- **Rate-based thresholds**: Detect spikes and anomalies

### 4. Export Targets

#### Incident Storage
```yaml
export_target: "incident_storage"
severity: "critical"
```
For critical issues requiring immediate attention.

#### Debug Storage
```yaml
export_target: "debug_storage"
export_reason: "error_rate_spike"
```
For development teams to investigate performance issues.

#### Security SIEM
```yaml
export_target: "security_siem"
anomaly_type: "authentication"
```
For security events and anomaly detection.

#### Long-term Storage
```yaml
export_target: "long_term_storage"
retention_policy: "1year"
```
For trend analysis and capacity planning.

## Deployment

### 1. Deploy the Basic System

```bash
kubectl apply -f threshold-data-exporter.yaml
```

### 2. Deploy the Advanced Router

```bash
kubectl apply -f vmagent-threshold-router.yaml
```

### 3. Verify Operation

```bash
# Check vmalert is running and evaluating rules
kubectl logs -l app=threshold-data-exporter -n monitoring

# Check vmagent is routing data
kubectl logs -l app=vmagent-threshold-router -n monitoring

# View the web UI
kubectl port-forward svc/threshold-data-exporter 8880:8880 -n monitoring
# Open http://localhost:8880
```

## Monitoring the Export System

### Key Metrics to Monitor

1. **Rule Evaluation Success**:
   ```promql
   vmalert_recording_rules_last_evaluation_samples > 0
   ```

2. **Export Queue Length**:
   ```promql
   vmagent_remotewrite_pending_data_bytes
   ```

3. **Successful Exports**:
   ```promql
   rate(vmagent_remotewrite_requests_total{status_code="2xx"}[5m])
   ```

4. **Failed Exports**:
   ```promql
   rate(vmagent_remotewrite_requests_total{status_code!="2xx"}[5m])
   ```

### Alerting on Export System Health

```yaml
groups:
  - name: threshold_export_health
    rules:
      - alert: ThresholdExportDown
        expr: up{job="threshold-data-exporter"} == 0
        for: 2m
        annotations:
          summary: "Threshold export system is down"
      
      - alert: HighExportQueueLength
        expr: vmagent_remotewrite_pending_data_bytes > 100000000  # 100MB
        for: 5m
        annotations:
          summary: "Export queue is backing up"
```

## Customization

### Adding New Threshold Types

1. **Create a new recording rule group**:
```yaml
- name: custom_threshold_export
  interval: 1m
  rules:
    - record: custom_metric_threshold
      expr: 'your_custom_metric > threshold_value'
      labels:
        export_reason: "custom_threshold"
        export_target: "your_target_storage"
```

2. **Configure routing in vmagent**:
```yaml
- url: "http://your-target-storage:8428/api/v1/write"
  write_relabel_configs:
    - source_labels: [export_target]
      regex: "your_target_storage"
      action: keep
```

### Advanced Filtering

Use relabeling to implement complex routing logic:

```yaml
write_relabel_configs:
  # Only export during business hours
  - source_labels: [__tmp_timestamp]
    regex: ".*T(09|10|11|12|13|14|15|16|17):.*"
    action: keep
  
  # Route based on multiple conditions
  - source_labels: [severity, team]
    regex: "critical;infrastructure"
    target_label: priority
    replacement: "p0"
```

## Troubleshooting

### Common Issues

1. **Rules not evaluating**:
   - Check vmalert logs for syntax errors
   - Verify datasource connectivity
   - Ensure metrics exist in the datasource

2. **Data not reaching target**:
   - Check vmagent logs for routing errors
   - Verify target datasource is reachable
   - Check relabeling configuration

3. **High memory usage**:
   - Tune `-remoteWrite.queues` parameter
   - Increase `-remoteWrite.flushInterval`
   - Monitor queue lengths

### Debug Commands

```bash
# Check rule evaluation
curl http://localhost:8880/api/v1/rules

# Check routing configuration
curl http://localhost:8429/config

# View metrics being exported
curl http://localhost:8880/metrics | grep "_export"
```

## Performance Considerations

### Resource Requirements

- **vmalert**: 
  - CPU: 100m-500m per 1000 rules
  - Memory: 64Mi-256Mi per 1000 rules
  
- **vmagent**:
  - CPU: 100m-500m depending on throughput
  - Memory: 128Mi-512Mi for buffering

### Optimization Tips

1. **Batch exports**: Use longer flush intervals for non-critical data
2. **Filter early**: Apply relabeling to reduce data volume
3. **Use appropriate intervals**: Don't evaluate rules too frequently
4. **Monitor queue depths**: Ensure targets can keep up with data volume

## Security Considerations

- **Network segmentation**: Isolate export targets appropriately
- **Authentication**: Configure proper auth for target datasources
- **Data sensitivity**: Be careful what data gets exported where
- **Access control**: Limit who can modify routing rules

This system provides a flexible, scalable way to export data based on thresholds, similar to how vmalert triggers alarms, but with the ability to route different types of threshold breaches to appropriate storage systems.