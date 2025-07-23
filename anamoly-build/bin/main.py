import sys
import os

# Add the libs folder to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'libs'))
from libs.config_loader import load_config
from libs.prometheus_query import query_prometheus
from libs.mysql_exporter import export_to_mysql
from libs.file_exporter import export_to_file
from libs.victoria_export import export_to_victoriametrics
import logging

logging.basicConfig(level=logging.INFO)

def main():
    # Load config
    config = load_config("config/rules.yaml")
    datasources = config.get("datasources", {})
    exports = config.get("exports", {})
    
    # Process each rule
    for rule in config.get("rules", []):
        value = query_prometheus(rule, datasources)
        if value is None:
            continue

        threshold = rule["threshold"]
        condition = rule["condition"]
        
        if (condition == ">" and value > threshold) or (condition == "<" and value < threshold):
            logging.info(f"Rule triggered: {rule['name']} with value {value}")
            export_type = rule["export"]["datastore"]
            if export_type == "mysql":
                export_to_mysql(rule, value, exports)
            elif export_type == "file":
                export_to_file(rule, value)
            else:
                export_to_victoriametrics(rule, value, exports)
        else:
            logging.info(f"Rule not triggered: {rule['name']} with value {value}")

if __name__ == "__main__":
    main()
