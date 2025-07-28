import requests
import yaml
import logging
import time
import sys
import os
print("PYTHONPATH:", sys.path)
# Add the libs folder to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the full path to the libs directory
sys.path.append(os.path.join(project_root))
logging.basicConfig(level=logging.INFO)

def load_config(file_path):
    with open(file_path) as f:
        return yaml.safe_load(f)

def query_prometheus(query, datasource_url):
    try:
        resp = requests.get(datasource_url, params={"query": query})
        resp.raise_for_status()
        results = resp.json().get("data", {}).get("result", [])
        return results
    except Exception as e:
        logging.error(f"Query failed: {e}")
        return []

def export_to_victoriametrics(alert_name, expr, results, push_url):
    if not results:
        logging.warning(f"No results to export for {alert_name}")
        return

    ts = int(time.time() * 1000)
    lines = []

    for res in results:
        value = res["value"][1]
        labels = res.get("metric", {})
        label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
        metric_name = f"custom_{alert_name.lower()}"
        line = f'{metric_name}{{{label_str},alert="{alert_name}"}} {value} {ts}'
        lines.append(line)

    payload = "\n".join(lines)

    try:
        resp = requests.post(push_url, data=payload)
        resp.raise_for_status()
        logging.info(f"Exported alert: {alert_name}")
    except Exception as e:
        logging.error(f"Export failed for {alert_name}: {e}")

def main():
    config = load_config("config.yaml")
    datasource_url = config["datasource"]["url"]
    push_url = config["export"]["push_url"]
    groups = config.get("groups", [])

    for group in groups:
        for rule in group.get("rules", []):
            alert_name = rule["alert"]
            expr = rule["expr"]
            results = query_prometheus(expr, datasource_url)
            export_to_victoriametrics(alert_name, expr, results, push_url)
            time.sleep(1)

if __name__ == "__main__":
    main()

