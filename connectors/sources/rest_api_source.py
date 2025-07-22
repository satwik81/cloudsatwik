"""
REST API data source implementation
"""

import pandas as pd
import requests
import logging
import json
from typing import Dict, Any
from ..base import DataSource


class RestAPISource(DataSource):
    """REST API data source"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
    def get_data(self) -> pd.DataFrame:
        """Get data from REST API"""
        try:
            url = self.config['url']
            method = self.config.get('method', 'GET').upper()
            headers = self.config.get('headers', {})
            params = self.config.get('params', {})
            timeout = self.config.get('timeout', 30)
            
            # Make API request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                timeout=timeout
            )
            
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # If response has a data key, use that
                if 'data' in data:
                    df = pd.DataFrame(data['data'])
                elif 'results' in data:
                    df = pd.DataFrame(data['results'])
                else:
                    # Try to convert the dict directly
                    df = pd.DataFrame([data])
            else:
                raise ValueError(f"Unsupported response format: {type(data)}")
            
            self.logger.info(f"Retrieved {len(df)} records from API: {url}")
            return df
            
        except requests.RequestException as e:
            self.logger.error(f"API request error: {e}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting data from API: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            url = self.config['url']
            headers = self.config.get('headers', {})
            timeout = self.config.get('timeout', 10)
            
            # Make a simple HEAD request to test connectivity
            response = requests.head(url, headers=headers, timeout=timeout)
            
            # Accept any 2xx or 405 (method not allowed) status
            if response.status_code < 400 or response.status_code == 405:
                return True
            else:
                self.logger.error(f"API test failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"API connection test failed: {e}")
            return False