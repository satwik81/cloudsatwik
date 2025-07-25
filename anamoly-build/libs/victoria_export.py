import requests
from datetime import datetime

def export_to_victoriametrics(rule, value, exports):
    vm_config = exports["victoriametrics"]
    
    try:
        # Add dummy labels if none are defined
        labels = rule.get("labels", {"source": "custom_export"})
        
        # Build the Prometheus line format: metric{label="value"} value timestamp(ms)
        label_str = ",".join([f'{k}="{v}"' for k, v in labels.items()])
        timestamp_ms = int(datetime.utcnow().timestamp() * 1000)  # Timestamp in milliseconds
        data = f"{rule['name']}{{{label_str}}} {value} {timestamp_ms}\n"  # Metric format
        
        # Send to VictoriaMetrics (vminsert endpoint)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}  # Raw data format
        response = requests.post(f"{vm_config['url']}", headers=headers, data=data)
        
        # Check the response from VictoriaMetrics
        if response.status_code == 200:
            print(f"Exported to VictoriaMetrics: {rule['name']} - value: {value}")
        else:
            print(f"Failed to export data to VictoriaMetrics: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error exporting to VictoriaMetrics: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Example Usage
# if __name__ == "__main__":
#     # Example rule with name and labels
#     rule = {
#         "name": "my_custom_metric",
#         "labels": {"source": "custom_export", "host": "my_host", "region": "us-west-1"}
#     }

#     value = 123.45  # Metric value
#     exports = {
#         "victoriametrics": {
#             "url": "http://your-vminsert-instance:8480"  # Change to your vminsert endpoint
#         }
#     }
    
#     export_to_victoriametrics(rule, value, exports)
