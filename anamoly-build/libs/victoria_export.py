import requests
from datetime import datetime

def export_to_victoriametrics(rule, value, exports):
    vm_config = exports["victoriametrics"]

    try:
        # Prepare the time-series data in the Prometheus format
        data = f'{rule["name"]} {value} {int(datetime.utcnow().timestamp())}\n'
        headers = {'Content-Type': 'text/plain'}
        # Send data to the /api/v1/import endpoint
        response = requests.post(f'{vm_config["url"]}/insert/0/prometheus/api/v1/import', data=data, headers=headers)
        
        if response.status_code == 200:
            print(f"Exported to VictoriaMetrics: {rule['name']} - value: {value}")
        else:
            print(f"Failed to export data to VictoriaMetrics: {response.status_code}")
            
    except Exception as e:
        print(f"Error exporting to VictoriaMetrics: {e}")
