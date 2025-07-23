import yaml
import requests
import pymysql
import json

# Load the YAML configuration file
def load_config(config_file="config.yaml"):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

# Function to query the datasource and fetch the metric value
def query_datasource(url, query):
    try:
        response = requests.get(url, params={"query": query})
        response.raise_for_status()
        data = response.json()
        return data['data']
    except Exception as e:
        print(f"Error querying VictoriaMetrics: {e}")
        return None

# Function to export data to MySQL
def export_to_mysql(mysql_config, data):
    try:
        connection = pymysql.connect(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database']
        )
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                metric_name VARCHAR(255),
                value FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        for metric in data:
            cursor.execute("""
                INSERT INTO metrics (metric_name, value) VALUES (%s, %s)
            """, (metric['metric'], metric['value']))
        connection.commit()
        connection.close()
        print(f"Data exported to MySQL: {len(data)} records")
    except Exception as e:
        print(f"Error exporting to MySQL: {e}")

# Function to export data to a file
def export_to_file(file_path, data):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data exported to file: {file_path}")
    except Exception as e:
        print(f"Error exporting to file: {e}")

# Process each rule from the configuration
def process_rules(config):
    for rule in config['rules']:
        print(f"Processing rule: {rule['name']}")

        # Get the datasource URL and query the data
        datasource_url = rule['datasource']['url']
        query = rule['query']
        result = query_datasource(datasource_url, query)
        
        if result is None:
            print(f"No data returned for rule: {rule['name']}")
            continue
        
        # Check if the value exceeds the threshold
        metric_value = result[0].get('value')  # Assuming the first result contains the value
        print(f"Queried Value: {metric_value} | Threshold: {rule['threshold']}")
        
        if rule['condition'] == ">" and metric_value > rule['threshold']:
            print(f"Threshold exceeded for rule: {rule['name']}. Value: {metric_value} > {rule['threshold']}")
            # Export data based on the export section
            if rule['export']['datastore'] == 'mysql':
                export_to_mysql(rule['export']['mysql'], result)
            elif rule['export']['datastore'] == 'file':
                export_to_file(rule['export']['file']['path'], result)
        else:
            print(f"Threshold not met for rule: {rule['name']}. Skipping export.")

# Main function to run the script
if __name__ == "__main__":
    config = load_config()  # Load the configuration from config.yaml
    process_rules(config)  # Process each rule in the config
