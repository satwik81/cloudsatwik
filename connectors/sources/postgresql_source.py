"""
PostgreSQL data source implementation
"""

import pandas as pd
import psycopg2
import logging
from typing import Dict, Any
from ..base import DataSource


class PostgreSQLSource(DataSource):
    """PostgreSQL data source"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
    def get_data(self) -> pd.DataFrame:
        """Get data from PostgreSQL database"""
        try:
            # Create connection string
            conn_params = {
                'host': self.config['host'],
                'port': self.config['port'],
                'database': self.config['database'],
                'user': self.config['username'],
                'password': self.config['password']
            }
            
            # Connect and execute query
            with psycopg2.connect(**conn_params) as conn:
                query = self.config['query']
                df = pd.read_sql(query, conn)
                self.logger.info(f"Retrieved {len(df)} records from PostgreSQL")
                return df
                
        except psycopg2.Error as e:
            self.logger.error(f"PostgreSQL error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting data from PostgreSQL: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test PostgreSQL connection"""
        try:
            conn_params = {
                'host': self.config['host'],
                'port': self.config['port'],
                'database': self.config['database'],
                'user': self.config['username'],
                'password': self.config['password']
            }
            
            with psycopg2.connect(**conn_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            
            return True
            
        except Exception as e:
            self.logger.error(f"PostgreSQL connection test failed: {e}")
            return False