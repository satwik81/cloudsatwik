import requests
import yaml
import json
import time
import os
import logging
import mysql.connector
from datetime import datetime
from urllib.parse import urlencode

logging.basicConfig(level=logging.INFO)

# Load configuration from the updated YAML
def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

# Query Prometheus using the specified rule
def query_prometheus(rule, datasources):
    query_params = {
        "query": rule["query"]
    }
    datasource = datasources[rule["datasource"]["name"]]
    url = f'{datasource["url"]}?{urlencode(query_params)}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        results = data.get("data", {}).get("result", [])
        if not results:
            raise ValueError("no results")
        value = float(results[0]["value"][1])
        return value
    except Exception as e:
        logging.error(f"Error querying datasource for rule {rule['name']}: {e}")
        return None

# Export data to a file
def export_to_file(rule, value):
    alert = {
        "name": rule["name"],
        "description": rule["description"],
        "value": value,
        "timestamp": datetime.utcnow().isoformat()
    }
    path = rule["export"]["file"]["path"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a') as f:
        f.write(json.dumps(alert) + "\n")
    logging.info(f"Exported to file: {path}")

# Export data to MySQL
def export_to_mysql(rule, value, exports):
    mysql_config = exports["mysql"]
    try:
        conn = mysql.connector.connect(
            host=mysql_config["host"],
            user=mysql_config["user"],
            password=mysql_config["password"],
            database=mysql_config["database"]
        )
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                description TEXT,
                value DOUBLE,
                timestamp DATETIME
            )
        """)
        cursor.execute("""
            INSERT INTO alerts (name, description, value, timestamp)
            VALUES (%s, %s, %s, %s)
        """, (rule["name"], rule["description"], value, datetime.utcnow()))
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Exported to MySQL")
    except Exception as e:
        logging.error(f"MySQL export error: {e}")

# Evaluate a given rule against the query results
def evaluate_rule(rule, datasources, exports):
    value = query_prometheus(rule, datasources)
    if value is None:
        return

    condition = rule["condition"]
    threshold = rule["threshold"]
    triggered = False

    if condition == ">":
        triggered = value > threshold
    elif condition == "<":
        triggered = value < threshold
    else:
        logging.warning(f"Unknown condition {condition} in rule {rule['name']}")
        return

    if triggered:
        logging.info(f"Rule triggered: {rule['name']} - value: {value}")
        export_type = rule["export"]["datastore"]
        if export_type == "file":
            export_to_file(rule, value)
        elif export_type == "mysql":
            export_to_mysql(rule, value, exports)
    else:
        logging.info(f"Rule not triggered: {rule['name']} - value: {value}")

# Main execution
def main():
    config = load_config("rules.yaml")
    datasources = config.get("datasources", {})
    exports = config.get("exports", {})
    
    for rule in config.get("rules", []):
        evaluate_rule(rule, datasources, exports)

if __name__ == "__main__":
    main()
