"""
Factory for creating datasource instances
"""

from typing import Dict, Any
from .base import DataSource
from .sources.postgresql_source import PostgreSQLSource
from .sources.csv_source import CSVSource
from .sources.rest_api_source import RestAPISource


class DataSourceFactory:
    """Factory for creating datasource instances"""
    
    _source_types = {
        'postgresql': PostgreSQLSource,
        'csv': CSVSource,
        'rest_api': RestAPISource,
    }
    
    @classmethod
    def create_datasource(cls, config: Dict[str, Any]) -> DataSource:
        """Create a datasource instance based on config type"""
        source_type = config.get('type')
        
        if not source_type:
            raise ValueError("Datasource config must specify 'type'")
        
        if source_type not in cls._source_types:
            raise ValueError(f"Unsupported datasource type: {source_type}. "
                           f"Supported types: {list(cls._source_types.keys())}")
        
        source_class = cls._source_types[source_type]
        return source_class(config)
    
    @classmethod
    def get_supported_types(cls):
        """Get list of supported datasource types"""
        return list(cls._source_types.keys())