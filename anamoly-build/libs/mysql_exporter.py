import mysql.connector
from datetime import datetime
import logging

def export_to_mysql(rule, value, exports):
    mysql_config = exports.get("mysql", {})
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
