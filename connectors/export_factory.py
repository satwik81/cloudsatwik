"""
Factory for creating data exporter instances
"""

from typing import Dict, Any
from .base import DataExporter
from .exporters.postgresql_exporter import PostgreSQLExporter
from .exporters.rest_api_exporter import RestAPIExporter
from .exporters.s3_exporter import S3Exporter
from .exporters.redis_exporter import RedisExporter


class ExportFactory:
    """Factory for creating data exporter instances"""
    
    _exporter_types = {
        'postgresql': PostgreSQLExporter,
        'rest_api': RestAPIExporter,
        's3': S3Exporter,
        'redis': RedisExporter,
    }
    
    @classmethod
    def create_exporter(cls, config: Dict[str, Any]) -> DataExporter:
        """Create an exporter instance based on config type"""
        exporter_type = config.get('type')
        
        if not exporter_type:
            raise ValueError("Export config must specify 'type'")
        
        if exporter_type not in cls._exporter_types:
            raise ValueError(f"Unsupported exporter type: {exporter_type}. "
                           f"Supported types: {list(cls._exporter_types.keys())}")
        
        exporter_class = cls._exporter_types[exporter_type]
        return exporter_class(config)
    
    @classmethod
    def get_supported_types(cls):
        """Get list of supported exporter types"""
        return list(cls._exporter_types.keys())