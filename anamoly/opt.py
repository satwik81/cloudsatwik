import requests
import yaml
import json
import time
import pymysql
from pymysql import MySQLError

# Load configuration from YAML
def load_config(config_file='config.yaml'):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

# Fetch metrics from vmselect API
def fetch_metrics_from_vmselect(vmselect_url, query):
    try:
        response = requests.get(vmselect_url, params={'query': query})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching metrics from {vmselect_url}: {e}")
        return None

# Process and check if a metric breaches its threshold
def process_and_check_threshold(metrics_data, metric_config):
    results = []
    for metric in metric_config:
        metric_name = metric['name']
        threshold = metric['threshold']
        condition = metric['condition']
        action = metric['action']
        
        # Find the corresponding metric in the fetched data
        metric_value = next(
            (item['value'] for item in metrics_data['data'] if item['name'] == metric_name), 
            None
        )
        
        if metric_value is not None:
            metric_value = float(metric_value)
            if condition == ">" and metric_value > threshold:
                if action == "export":
                    results.append({
                        'metric': metric_name,
                        'value': metric_value,
                        'threshold': threshold
                    })
                elif action == "export":
                    results.append({
                        'metric': metric_name,
                        'value': metric_value,
                        'threshold': threshold
                    })
    return results

# Export data to MySQL database using PyMySQL
def export_data_to_mysql(records, mysql_config):
    try:
        # Connect to MySQL
        connection = pymysql.connect(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database']
        )
        cursor = connection.cursor()

        # Prepare SQL query to insert the records
        for record in records:
            timestamp = record.get('timestamp', time.time())  # Use current timestamp if not provided
            value = record['value']
            metric_name = record['metric']

            insert_query = """
            INSERT INTO metrics (metric_name, timestamp, value)
            VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (metric_name, timestamp, value))
        
        connection.commit()
        print(f"{len(records)} records exported to MySQL.")
    except MySQLError as e:
        print(f"Error exporting data to MySQL: {e}")
    finally:
        if connection.open:
            cursor.close()
            connection.close()

# Export data to a JSON file
def export_data_to_file(records, file_path):
    try:
        with open(file_path, 'w') as file:
            json.dump(records, file, indent=4)
        print(f"Data exported to {file_path}.")
    except Exception as e:
        print(f"Error exporting data to file: {e}")

# Main function to run the process
def main():
    config = load_config()

    vmselects = config['vmselects']
    metric_config = config['metrics']
    export_config = config['export']

    while True:
        all_records_to_export = []

        # Loop over each vmselect instance
        for vmselect in vmselects:
            vmselect_url = vmselect['url']
            query = vmselect['query']
            
            # Fetch metrics from vmselect
            metrics_data = fetch_metrics_from_vmselect(vmselect_url, query)
            if metrics_data:
                # Process and check thresholds for each metric
                records_to_export = process_and_check_threshold(metrics_data, metric_config)
                all_records_to_export.extend(records_to_export)

        # Export the collected records if any threshold was breached
        if all_records_to_export:
            if export_config['datastore'] == 'mysql':
                export_data_to_mysql(all_records_to_export, export_config['mysql'])
            elif export_config['datastore'] == 'file':
                export_data_to_file(all_records_to_export, export_config['file']['path'])

        # Wait for the next poll (e.g., 60 seconds)
        time.sleep(60)

if __name__ == "__main__":
    main()
