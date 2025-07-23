import json
import os
from datetime import datetime
import logging

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
