"""
CSV data source implementation
"""

import pandas as pd
import os
import logging
from typing import Dict, Any
from ..base import DataSource


class CSVSource(DataSource):
    """CSV file data source"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
    def get_data(self) -> pd.DataFrame:
        """Get data from CSV file"""
        try:
            file_path = self.config['path']
            delimiter = self.config.get('delimiter', ',')
            encoding = self.config.get('encoding', 'utf-8')
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"CSV file not found: {file_path}")
            
            df = pd.read_csv(
                file_path,
                delimiter=delimiter,
                encoding=encoding
            )
            
            self.logger.info(f"Retrieved {len(df)} records from CSV file: {file_path}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test if CSV file exists and is readable"""
        try:
            file_path = self.config['path']
            
            if not os.path.exists(file_path):
                self.logger.error(f"CSV file not found: {file_path}")
                return False
            
            if not os.access(file_path, os.R_OK):
                self.logger.error(f"CSV file is not readable: {file_path}")
                return False
            
            # Try to read first few rows to validate format
            pd.read_csv(file_path, nrows=5)
            return True
            
        except Exception as e:
            self.logger.error(f"CSV connection test failed: {e}")
            return False