"""
Base classes for datasources and exporters
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any


class DataSource(ABC):
    """Abstract base class for data sources"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    def get_data(self) -> pd.DataFrame:
        """Get data from the source and return as DataFrame"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if connection to the data source is working"""
        pass


class DataExporter(ABC):
    """Abstract base class for data exporters"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    async def export_data(self, data: pd.DataFrame) -> int:
        """Export data and return number of records exported"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if connection to the export target is working"""
        pass