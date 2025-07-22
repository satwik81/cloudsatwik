"""
Redis data exporter implementation
"""

import pandas as pd
import redis
import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, Any
from ..base import DataExporter


class RedisExporter(DataExporter):
    """Redis data exporter"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
    async def export_data(self, data: pd.DataFrame) -> int:
        """Export data to Redis"""
        if data.empty:
            return 0
            
        try:
            # Create Redis client
            redis_client = redis.Redis(
                host=self.config['host'],
                port=self.config['port'],
                db=self.config.get('database', 0),
                password=self.config.get('password'),
                decode_responses=True
            )
            
            key_prefix = self.config.get('key_prefix', 'data:')
            storage_type = self.config.get('storage_type', 'hash')  # hash, list, set, string
            expiry_seconds = self.config.get('expiry_seconds')
            
            exported_count = 0
            
            # Export data based on storage type
            if storage_type == 'hash':
                exported_count = await self._export_as_hash(redis_client, data, key_prefix, expiry_seconds)
            elif storage_type == 'list':
                exported_count = await self._export_as_list(redis_client, data, key_prefix, expiry_seconds)
            elif storage_type == 'string':
                exported_count = await self._export_as_string(redis_client, data, key_prefix, expiry_seconds)
            else:
                raise ValueError(f"Unsupported Redis storage type: {storage_type}")
            
            self.logger.info(f"Successfully exported {exported_count} records to Redis")
            return exported_count
            
        except Exception as e:
            self.logger.error(f"Error exporting to Redis: {e}")
            raise
    
    async def _export_as_hash(self, redis_client, data: pd.DataFrame, key_prefix: str, expiry_seconds: int) -> int:
        """Export data as Redis hashes (one hash per record)"""
        exported_count = 0
        
        for index, row in data.iterrows():
            key = f"{key_prefix}{index}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Convert row to dict and handle NaN values
            record = row.to_dict()
            record = {k: (str(v) if pd.notna(v) else '') for k, v in record.items()}
            
            # Store in Redis hash
            await asyncio.get_event_loop().run_in_executor(
                None, redis_client.hset, key, None, record
            )
            
            # Set expiry if specified
            if expiry_seconds:
                await asyncio.get_event_loop().run_in_executor(
                    None, redis_client.expire, key, expiry_seconds
                )
            
            exported_count += 1
        
        return exported_count
    
    async def _export_as_list(self, redis_client, data: pd.DataFrame, key_prefix: str, expiry_seconds: int) -> int:
        """Export data as Redis list (all records in one list)"""
        key = f"{key_prefix}list_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Convert DataFrame to list of JSON strings
        records = []
        for _, row in data.iterrows():
            record = row.to_dict()
            # Handle NaN values
            record = {k: (v if pd.notna(v) else None) for k, v in record.items()}
            records.append(json.dumps(record))
        
        # Push all records to Redis list
        await asyncio.get_event_loop().run_in_executor(
            None, redis_client.lpush, key, *records
        )
        
        # Set expiry if specified
        if expiry_seconds:
            await asyncio.get_event_loop().run_in_executor(
                None, redis_client.expire, key, expiry_seconds
            )
        
        return len(records)
    
    async def _export_as_string(self, redis_client, data: pd.DataFrame, key_prefix: str, expiry_seconds: int) -> int:
        """Export data as Redis string (entire DataFrame as JSON)"""
        key = f"{key_prefix}data_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Convert DataFrame to JSON
        json_data = data.to_json(orient='records')
        
        # Store in Redis string
        await asyncio.get_event_loop().run_in_executor(
            None, redis_client.set, key, json_data
        )
        
        # Set expiry if specified
        if expiry_seconds:
            await asyncio.get_event_loop().run_in_executor(
                None, redis_client.expire, key, expiry_seconds
            )
        
        return len(data)
    
    def test_connection(self) -> bool:
        """Test Redis connection"""
        try:
            redis_client = redis.Redis(
                host=self.config['host'],
                port=self.config['port'],
                db=self.config.get('database', 0),
                password=self.config.get('password'),
                decode_responses=True
            )
            
            # Test connection with ping
            redis_client.ping()
            return True
            
        except Exception as e:
            self.logger.error(f"Redis connection test failed: {e}")
            return False