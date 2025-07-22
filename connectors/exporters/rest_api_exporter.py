"""
REST API data exporter implementation
"""

import pandas as pd
import requests
import logging
import asyncio
import aiohttp
import json
from typing import Dict, Any, List
from ..base import DataExporter


class RestAPIExporter(DataExporter):
    """REST API data exporter"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
    async def export_data(self, data: pd.DataFrame) -> int:
        """Export data to REST API"""
        if data.empty:
            return 0
            
        try:
            url = self.config['url']
            method = self.config.get('method', 'POST').upper()
            headers = self.config.get('headers', {})
            batch_size = self.config.get('batch_size', 100)
            timeout = self.config.get('timeout', 30)
            
            exported_count = 0
            
            # Process data in batches
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                for i in range(0, len(data), batch_size):
                    batch = data.iloc[i:i + batch_size]
                    
                    # Convert batch to JSON
                    records = batch.to_dict('records')
                    
                    try:
                        async with session.request(
                            method=method,
                            url=url,
                            headers=headers,
                            json=records
                        ) as response:
                            response.raise_for_status()
                            exported_count += len(records)
                            
                            self.logger.debug(f"Exported batch {i//batch_size + 1}: {len(records)} records")
                            
                    except aiohttp.ClientError as e:
                        self.logger.error(f"Error exporting batch {i//batch_size + 1}: {e}")
                        raise
            
            self.logger.info(f"Successfully exported {exported_count} records to API: {url}")
            return exported_count
            
        except Exception as e:
            self.logger.error(f"Error exporting to REST API: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test REST API connection"""
        try:
            url = self.config['url']
            headers = self.config.get('headers', {})
            timeout = self.config.get('timeout', 10)
            
            # Make a simple HEAD request to test connectivity
            response = requests.head(url, headers=headers, timeout=timeout)
            
            # Accept any 2xx status or 405 (method not allowed)
            if response.status_code < 400 or response.status_code == 405:
                return True
            else:
                self.logger.error(f"API test failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"REST API connection test failed: {e}")
            return False