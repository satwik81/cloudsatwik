"""
PostgreSQL data exporter implementation
"""

import pandas as pd
import psycopg2
import psycopg2.extras
import logging
import asyncio
from typing import Dict, Any
from ..base import DataExporter


class PostgreSQLExporter(DataExporter):
    """PostgreSQL data exporter"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
    async def export_data(self, data: pd.DataFrame) -> int:
        """Export data to PostgreSQL database"""
        if data.empty:
            return 0
            
        try:
            # Create connection parameters
            conn_params = {
                'host': self.config['host'],
                'port': self.config['port'],
                'database': self.config['database'],
                'user': self.config['username'],
                'password': self.config['password']
            }
            
            table_name = self.config['table']
            batch_size = self.config.get('batch_size', 1000)
            
            exported_count = 0
            
            # Process data in batches
            for i in range(0, len(data), batch_size):
                batch = data.iloc[i:i + batch_size]
                
                # Run batch insert in thread pool to avoid blocking
                count = await asyncio.get_event_loop().run_in_executor(
                    None, self._insert_batch, conn_params, table_name, batch
                )
                exported_count += count
                
                self.logger.debug(f"Exported batch {i//batch_size + 1}: {count} records")
            
            self.logger.info(f"Successfully exported {exported_count} records to PostgreSQL table: {table_name}")
            return exported_count
            
        except Exception as e:
            self.logger.error(f"Error exporting to PostgreSQL: {e}")
            raise
    
    def _insert_batch(self, conn_params: Dict[str, Any], table_name: str, batch: pd.DataFrame) -> int:
        """Insert a batch of data to PostgreSQL"""
        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor() as cursor:
                # Convert DataFrame to list of tuples
                records = [tuple(row) for row in batch.values]
                columns = list(batch.columns)
                
                # Create INSERT statement
                columns_str = ', '.join(columns)
                placeholders = ', '.join(['%s'] * len(columns))
                query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                
                # Execute batch insert
                psycopg2.extras.execute_batch(cursor, query, records)
                conn.commit()
                
                return len(records)
    
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
                    # Test basic connection
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    
                    # Test if table exists (optional)
                    table_name = self.config.get('table')
                    if table_name:
                        cursor.execute(
                            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
                            (table_name,)
                        )
                        table_exists = cursor.fetchone()[0]
                        if not table_exists:
                            self.logger.warning(f"Table '{table_name}' does not exist")
            
            return True
            
        except Exception as e:
            self.logger.error(f"PostgreSQL connection test failed: {e}")
            return False