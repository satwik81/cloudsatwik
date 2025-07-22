"""
S3 data exporter implementation
"""

import pandas as pd
import boto3
import logging
import asyncio
import io
from datetime import datetime
from typing import Dict, Any
from ..base import DataExporter


class S3Exporter(DataExporter):
    """S3 data exporter"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
    async def export_data(self, data: pd.DataFrame) -> int:
        """Export data to S3"""
        if data.empty:
            return 0
            
        try:
            # Create S3 client
            s3_client = boto3.client(
                's3',
                region_name=self.config['region'],
                aws_access_key_id=self.config['access_key'],
                aws_secret_access_key=self.config['secret_key']
            )
            
            bucket = self.config['bucket']
            prefix = self.config.get('prefix', '')
            file_format = self.config.get('format', 'parquet')  # parquet, csv, json
            
            # Generate filename with timestamp
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{prefix}export_{timestamp}.{file_format}"
            
            # Convert DataFrame to bytes based on format
            if file_format == 'parquet':
                buffer = io.BytesIO()
                data.to_parquet(buffer, index=False)
                content = buffer.getvalue()
            elif file_format == 'csv':
                content = data.to_csv(index=False).encode('utf-8')
            elif file_format == 'json':
                content = data.to_json(orient='records').encode('utf-8')
            else:
                raise ValueError(f"Unsupported file format: {file_format}")
            
            # Upload to S3 in thread pool to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                None, self._upload_to_s3, s3_client, bucket, filename, content
            )
            
            exported_count = len(data)
            self.logger.info(f"Successfully exported {exported_count} records to S3: s3://{bucket}/{filename}")
            return exported_count
            
        except Exception as e:
            self.logger.error(f"Error exporting to S3: {e}")
            raise
    
    def _upload_to_s3(self, s3_client, bucket: str, key: str, content: bytes):
        """Upload content to S3"""
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=content
        )
    
    def test_connection(self) -> bool:
        """Test S3 connection"""
        try:
            s3_client = boto3.client(
                's3',
                region_name=self.config['region'],
                aws_access_key_id=self.config['access_key'],
                aws_secret_access_key=self.config['secret_key']
            )
            
            bucket = self.config['bucket']
            
            # Test bucket access
            s3_client.head_bucket(Bucket=bucket)
            return True
            
        except Exception as e:
            self.logger.error(f"S3 connection test failed: {e}")
            return False