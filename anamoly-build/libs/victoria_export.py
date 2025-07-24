import requests
import yaml
from prometheus_client import CollectorRegistry, Gauge, generate_latest
from datetime import datetime

def export_to_victoriametrics(rule, value, exports):
    vm_config = exports["victoriametrics"]

    try:
        # Create a registry and a gauge metric
        registry = CollectorRegistry()
        gauge = Gauge(rule["name"], rule["description"], labelnames=["source"], registry=registry)

        # Set the value with the label (ensure it is 'source' or custom label as needed)
        gauge.labels(source=rule["labels"].get("source", "custom_export")).set(value)

        # Serialize the metrics in Prometheus format
        metrics_data = generate_latest(registry)

        # Send the data to VictoriaMetrics using Remote Write (protobuf format)
        headers = {
            "Content-Type": "application/x-protobuf",  # Remote write requires protobuf format
        }

        # Send the data to VictoriaMetrics via POST to /api/v1/write
        response = requests.post(f'{vm_config}/api/v1/write', data=metrics_data, headers=headers)

        if response.status_code == 200:
            print(f"Successfully exported {rule['name']} with value {value} to VictoriaMetrics")
        else:
            print(f"Failed to export: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error exporting to VictoriaMetrics: {e}")
