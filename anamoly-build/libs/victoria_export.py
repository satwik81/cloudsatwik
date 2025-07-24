import requests
from datetime import datetime

def export_to_victoriametrics(rule, value, exports):
    vm_config = exports["victoriametrics"]

    try:
        # Add dummy labels if none are defined
        labels = rule.get("labels", {"source": "custom_export"})

        # Build the Prometheus line format: metric{label="value"} value timestamp(ms)
        label_str = ",".join([f'{k}="{v}"' for k, v in labels.items()])
        timestamp_ms = int(datetime.utcnow().timestamp() * 1000)
        data = f'{rule["name"]}{{{label_str}}} {value} {timestamp_ms}\n'

        # Send to VictoriaMetrics
        headers = {"Content-Type": "text/plain"}
        response = requests.post(f'{vm_config["url"]}', data=data, headers=headers)

        if response.status_code==200:
            print(f"Exported to VictoriaMetrics: {rule['name']} - value: {value}")
        else:
            print(f"Failed to export data to VictoriaMetrics: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f" Error exporting to VictoriaMetrics: {e}")
