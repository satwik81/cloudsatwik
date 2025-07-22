# Where and How to Configure Datastore Settings for vmalert Export

## 1. Command Line Configuration (Primary Method)

### Remote Write Configuration
```bash
vmalert \
  -rule.file=vmalert-rules.yaml \
  -datasource.url=http://victoriametrics:8428 \
  -remoteWrite.url=http://influxdb:8086/api/v1/prom/write?db=alerts_db \
  -remoteWrite.basicAuth.username=admin \
  -remoteWrite.basicAuth.password=password123 \
  -remoteWrite.timeout=30s \
  -remoteWrite.maxBatchSize=1000
```

### Multiple Datastore Targets
```bash
vmalert \
  -rule.file=vmalert-rules.yaml \
  -datasource.url=http://victoriametrics:8428 \
  -remoteWrite.url=http://influxdb:8086/api/v1/prom/write?db=alerts_db \
  -remoteWrite.url=http://prometheus:9090/api/v1/write \
  -remoteWrite.url=http://elasticsearch:9200/_bulk
```

### Webhook/Alertmanager Configuration
```bash
vmalert \
  -rule.file=vmalert-rules.yaml \
  -datasource.url=http://victoriametrics:8428 \
  -notifier.url=http://alertmanager:9093 \
  -notifier.basicAuth.username=admin \
  -notifier.basicAuth.password=password123
```

## 2. Configuration File Method

### vmalert.yml Configuration
```yaml
# vmalert.yml
datasource:
  url: "http://victoriametrics:8428"
  basicAuth:
    username: "reader"
    password: "secret"

remoteWrite:
  - url: "http://influxdb:8086/api/v1/prom/write?db=alerts_db"
    basicAuth:
      username: "influx_user"
      password: "influx_pass"
    timeout: "30s"
    maxBatchSize: 1000
    headers:
      X-Custom-Header: "custom-value"
  
  - url: "http://prometheus:9090/api/v1/write"
    bearerToken: "your-bearer-token"
    
  - url: "http://elasticsearch:9200/_bulk"
    headers:
      Content-Type: "application/x-ndjson"

notifier:
  url: "http://alertmanager:9093"
  timeout: "10s"

ruleFiles:
  - "vmalert-rules.yaml"
  - "additional-rules.yaml"
```

### Usage with Config File
```bash
vmalert -config.file=vmalert.yml
```

## 3. Rule-Level Configuration (Metadata Only)

### In vmalert-rules.yaml (Annotations for Routing)
```yaml
groups:
  - name: cpu_rules
    rules:
      - alert: HighCPUUsage
        expr: cpu_usage > 80
        labels:
          export_to_datastore: "true"
          datastore_target: "influxdb"  # Routing hint
        annotations:
          # These are METADATA only - actual connection configured elsewhere
          export_datastore: "influxdb"
          export_database: "alerts_db"
          export_measurement: "cpu_alerts"
          export_retention_policy: "autogen"
          
      - alert: CriticalMemoryUsage
        expr: memory_usage > 95
        labels:
          export_to_datastore: "true"
          datastore_target: "elasticsearch"  # Different target
        annotations:
          export_datastore: "elasticsearch"
          export_index: "memory-alerts-2024"
          export_type: "alert"
```

## 4. Environment Variables Method

```bash
# Environment variables for vmalert
export VMALERT_DATASOURCE_URL="http://victoriametrics:8428"
export VMALERT_REMOTEWRITE_URL="http://influxdb:8086/api/v1/prom/write?db=alerts_db"
export VMALERT_REMOTEWRITE_BASICAUTH_USERNAME="admin"
export VMALERT_REMOTEWRITE_BASICAUTH_PASSWORD="password123"
export VMALERT_NOTIFIER_URL="http://alertmanager:9093"

# Then run vmalert
vmalert -rule.file=vmalert-rules.yaml
```

## 5. Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'
services:
  vmalert:
    image: victoriametrics/vmalert:latest
    command:
      - '-rule.file=/etc/vmalert/rules.yaml'
      - '-datasource.url=http://victoriametrics:8428'
      - '-remoteWrite.url=http://influxdb:8086/api/v1/prom/write?db=alerts_db'
      - '-remoteWrite.basicAuth.username=admin'
      - '-remoteWrite.basicAuth.password=password123'
      - '-notifier.url=http://alertmanager:9093'
    volumes:
      - ./vmalert-rules.yaml:/etc/vmalert/rules.yaml
    environment:
      - VMALERT_EXTERNAL_URL=http://vmalert:8880
    depends_on:
      - victoriametrics
      - influxdb
      - alertmanager

  influxdb:
    image: influxdb:1.8
    environment:
      - INFLUXDB_DB=alerts_db
      - INFLUXDB_USER=admin
      - INFLUXDB_USER_PASSWORD=password123
    volumes:
      - influxdb_data:/var/lib/influxdb

  alertmanager:
    image: prom/alertmanager:latest
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml

volumes:
  influxdb_data:
```

## 6. Kubernetes Configuration

### ConfigMap for Rules
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: vmalert-rules
data:
  rules.yaml: |
    groups:
      - name: cpu_rules
        rules:
          - alert: HighCPUUsage
            expr: cpu_usage > 80
            labels:
              export_to_datastore: "true"
            annotations:
              export_datastore: "influxdb"
              export_database: "alerts_db"
```

### Deployment with Datastore Configuration
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vmalert
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vmalert
  template:
    metadata:
      labels:
        app: vmalert
    spec:
      containers:
      - name: vmalert
        image: victoriametrics/vmalert:latest
        args:
          - '-rule.file=/etc/vmalert/rules.yaml'
          - '-datasource.url=http://victoriametrics:8428'
          - '-remoteWrite.url=http://influxdb:8086/api/v1/prom/write?db=alerts_db'
          - '-remoteWrite.basicAuth.username=$(INFLUX_USER)'
          - '-remoteWrite.basicAuth.password=$(INFLUX_PASS)'
          - '-notifier.url=http://alertmanager:9093'
        env:
        - name: INFLUX_USER
          valueFrom:
            secretKeyRef:
              name: influxdb-secret
              key: username
        - name: INFLUX_PASS
          valueFrom:
            secretKeyRef:
              name: influxdb-secret
              key: password
        volumeMounts:
        - name: rules
          mountPath: /etc/vmalert
      volumes:
      - name: rules
        configMap:
          name: vmalert-rules
```

## 7. Advanced Datastore Configurations

### InfluxDB v2.x Configuration
```bash
vmalert \
  -remoteWrite.url="http://influxdb:8086/api/v2/write?org=myorg&bucket=alerts&precision=ns" \
  -remoteWrite.headers="Authorization: Token your-influxdb-token"
```

### Elasticsearch Configuration
```bash
vmalert \
  -remoteWrite.url="http://elasticsearch:9200/_bulk" \
  -remoteWrite.headers="Content-Type: application/x-ndjson"
```

### Custom Export Service Configuration
```bash
vmalert \
  -notifier.url="http://custom-export-service:8080/webhook" \
  -notifier.headers="X-API-Key: your-api-key"
```

## 8. Conditional Datastore Routing

### Using Custom Export Service with Rule Metadata
```yaml
# Custom export service that reads annotations
groups:
  - name: routing_rules
    rules:
      - alert: DatabaseAlert
        expr: db_connections > 100
        labels:
          export_to_datastore: "true"
        annotations:
          # Custom service routes based on these annotations
          primary_datastore: "influxdb"
          secondary_datastore: "elasticsearch"
          export_database: "db_alerts"
          export_index: "database-alerts"
          
      - alert: NetworkAlert
        expr: network_errors > 10
        labels:
          export_to_datastore: "true"
        annotations:
          primary_datastore: "prometheus"
          export_database: "network_monitoring"
```

### Custom Export Service (webhook receiver)
```python
# custom-export-service.py
from flask import Flask, request
import influxdb
import elasticsearch

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_export():
    alert_data = request.json
    
    # Route based on annotations
    datastore = alert_data['annotations'].get('primary_datastore')
    
    if datastore == 'influxdb':
        export_to_influxdb(alert_data)
    elif datastore == 'elasticsearch':
        export_to_elasticsearch(alert_data)
    elif datastore == 'prometheus':
        export_to_prometheus(alert_data)
    
    return 'OK'
```

## 9. Security Configurations

### TLS/SSL Configuration
```bash
vmalert \
  -remoteWrite.url="https://secure-influxdb:8086/api/v1/prom/write?db=alerts_db" \
  -remoteWrite.tlsInsecureSkipVerify=false \
  -remoteWrite.tlsCertFile="/path/to/client.crt" \
  -remoteWrite.tlsKeyFile="/path/to/client.key" \
  -remoteWrite.tlsCAFile="/path/to/ca.crt"
```

### OAuth2 Configuration
```bash
vmalert \
  -remoteWrite.url="https://api.example.com/metrics" \
  -remoteWrite.oauth2.clientID="your-client-id" \
  -remoteWrite.oauth2.clientSecret="your-client-secret" \
  -remoteWrite.oauth2.tokenURL="https://auth.example.com/token"
```

## 10. Complete Example Setup

```bash
#!/bin/bash
# complete-vmalert-setup.sh

# Start vmalert with multiple datastore configurations
vmalert \
  -rule.file=/etc/vmalert/rules.yaml \
  -datasource.url=http://victoriametrics:8428 \
  -datasource.basicAuth.username=vm_reader \
  -datasource.basicAuth.password=vm_secret \
  \
  -remoteWrite.url=http://influxdb:8086/api/v1/prom/write?db=alerts_db \
  -remoteWrite.basicAuth.username=influx_user \
  -remoteWrite.basicAuth.password=influx_pass \
  -remoteWrite.timeout=30s \
  -remoteWrite.maxBatchSize=1000 \
  \
  -notifier.url=http://alertmanager:9093 \
  -notifier.timeout=10s \
  \
  -external.url=http://vmalert:8880 \
  -external.alert.source=vmalert \
  -loggerLevel=INFO
```

## Summary

**Datastore settings are configured at the vmalert process level, NOT in the rules file.**

- **Rules file**: Contains only metadata/annotations for routing hints
- **Command line/config file**: Contains actual connection settings
- **Environment variables**: Alternative way to set connection parameters
- **Multiple targets**: Can export to multiple datastores simultaneously
- **Security**: Supports TLS, basic auth, OAuth2, bearer tokens
- **Routing**: Custom services can read rule annotations for intelligent routing