# import requests
# from datetime import datetime

# def export_to_victoriametrics(rule, value, exports):
#     vm_config = exports["victoriametrics"]

#     try:
#         # Add dummy labels if none are defined
#         labels = rule.get("labels", {"source": "custom_export"})

#         # Build the Prometheus line format: metric{label="value"} value timestamp(ms)
#         label_str = ",".join([f'{k}="{v}"' for k, v in labels.items()])
#         timestamp_ms = int(datetime.utcnow().timestamp() * 1000)
#         data = f'{rule["name"]}{{{label_str}}} {value} {timestamp_ms}\n'

#         # Send to VictoriaMetrics
#         headers = {"Content-Type": "text/plain"}
#         response = requests.post(f'{vm_config["url"]}/api/v1/import/prometheus', data=data, headers=headers)

#         if response.status_code==200:
#             print(f"Exported to VictoriaMetrics: {rule['name']} - value: {value}")
#         else:
#             print(f"Failed to export data to VictoriaMetrics: {response.status_code} - {response.text}")
            
#     except Exception as e:
#         print(f" Error exporting to VictoriaMetrics: {e}")
import requests
from prometheus_client import CollectorRegistry, Gauge, generate_latest
from prometheus_client.exposition import basic_auth_handler
from datetime import datetime

def export_to_victoriametrics_remote_write(rule, value, exports):
    # Remote Write URL for VictoriaMetrics
    vm_url = exports["victoriametrics"]["url"]

    try:
        # Create a registry and a gauge metric
        registry = CollectorRegistry()
        gauge = Gauge(rule["name"], rule["description"], registry=registry)

        # Set the value
        gauge.set(value)

        # Serialize the metrics in Prometheus format
        metrics_data = generate_latest(registry)

        # Send to VictoriaMetrics using Remote Write (protobuf format)
        headers = {
            "Content-Type": "application/x-protobuf",  # Remote write requires protobuf format
        }

        # Send the data to VictoriaMetrics
        response = requests.post(f'{vm_url}/api/v1/write', data=metrics_data, headers=headers)

        if response.status_code == 200:
            print(f"Successfully exported {rule['name']} with value {value} to VictoriaMetrics")
        else:
            print(f"Failed to export: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error exporting to VictoriaMetrics: {e}")


# Example usage
exports = {
    "victoriametrics": {
        "url": "http://victoriametrics-instance:8428"  # Update with your VictoriaMetrics URL
    }
}

# Example rule
rule = {
    "name": "http_requests_total",
    "description": "Total number of HTTP requests"
}

# Example value to export
value = 100  # Replace this with the actual value

# Export to VictoriaMetrics via Remote Write
export_to_victoriametrics_remote_write(rule, value, exports)
