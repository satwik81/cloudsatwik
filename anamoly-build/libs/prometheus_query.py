import requests
from urllib.parse import urlencode
import logging

def query_prometheus(rule, datasources):
    query_params = {
        "query": rule["query"]
    }
    datasource = datasources.get(rule["datasource"]["name"])
    if not datasource:
        logging.error(f"Datasource {rule['datasource']['name']} not found.")
        return None
    
    url = f'{datasource["url"]}?{urlencode(query_params)}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        results = data.get("data", {}).get("result", [])
        if not results:
            raise ValueError("No results")
        return float(results[0]["value"][1])
    except Exception as e:
        logging.error(f"Error querying datasource for rule {rule['name']}: {e}")
        return None
