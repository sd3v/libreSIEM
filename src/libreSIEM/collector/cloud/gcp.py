"""Google Cloud Platform integration for LibreSIEM."""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, UTC
from pydantic import BaseModel
from google.cloud import logging_v2
from google.cloud import storage
from google.cloud import monitoring_v3
from google.cloud.logging_v2.resource import Resource
from ..models import LogEvent

logger = logging.getLogger(__name__)

class GCPService(BaseModel):
    """GCP service configuration."""
    name: str
    enabled: bool = True
    project_id: str
    log_filter: Optional[str] = None
    bucket_names: Optional[List[str]] = None

class GCPCredentials(BaseModel):
    """GCP credentials configuration."""
    service_account_info: Dict[str, Any]

class GCPIntegration:
    """GCP service integration for collecting logs and events."""
    
    def __init__(self, credentials: GCPCredentials):
        self.credentials = credentials
        self.logging_client = logging_v2.Client.from_service_account_info(
            credentials.service_account_info
        )
        self.storage_client = storage.Client.from_service_account_info(
            credentials.service_account_info
        )
        
    def _convert_to_log_event(
        self,
        entry: logging_v2.entries.StructEntry,
        service: GCPService
    ) -> LogEvent:
        """Convert a GCP log entry to a LibreSIEM LogEvent."""
        return LogEvent(
            source=f"gcp.{service.name}.{entry.resource.type}",
            event_type="gcp.logs",
            timestamp=entry.timestamp,
            data={
                "severity": entry.severity,
                "resource": {
                    "type": entry.resource.type,
                    "labels": dict(entry.resource.labels)
                },
                "labels": dict(entry.labels) if entry.labels else {},
                "message": entry.payload,
                "insert_id": entry.insert_id,
                "http_request": entry.http_request,
                "operation": entry.operation,
                "trace": entry.trace,
                "span_id": entry.span_id,
                "source_location": entry.source_location
            }
        )
        
    async def collect_stackdriver_logs(
        self,
        service: GCPService,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect logs from Stackdriver Logging."""
        logs = []
        
        start_time = start_time or (datetime.now(UTC) - timedelta(minutes=5))
        
        # Build the filter string
        filter_str = [
            f'timestamp >= "{start_time.isoformat()}Z"'
        ]
        
        if end_time:
            filter_str.append(f'timestamp <= "{end_time.isoformat()}Z"')
            
        if service.log_filter:
            filter_str.append(service.log_filter)
            
        filter_str = " AND ".join(filter_str)
        
        try:
            entries = self.logging_client.list_entries(
                project_ids=[service.project_id],
                filter_=filter_str,
                order_by="timestamp desc",
                page_size=1000  # Adjust as needed
            )
            
            for entry in entries:
                logs.append(self._convert_to_log_event(entry, service))
                
        except Exception as e:
            logger.error(f"Error collecting Stackdriver logs: {str(e)}")
            
        return logs
        
    async def collect_bucket_logs(
        self,
        service: GCPService,
        prefix: Optional[str] = None
    ) -> List[LogEvent]:
        """Collect logs from Cloud Storage buckets."""
        logs = []
        
        if not service.bucket_names:
            return logs
            
        for bucket_name in service.bucket_names:
            try:
                bucket = self.storage_client.bucket(bucket_name)
                blobs = bucket.list_blobs(prefix=prefix)
                
                for blob in blobs:
                    if not blob.name.endswith('.log'):
                        continue
                        
                    log_content = blob.download_as_string().decode('utf-8')
                    
                    for line in log_content.splitlines():
                        logs.append(LogEvent(
                            source=f"gcp.{service.name}.storage",
                            event_type="gcp.storage",
                            timestamp=datetime.now(UTC),  # Use actual timestamp if available
                            data={
                                "bucket": bucket_name,
                                "object": blob.name,
                                "message": line,
                                "metadata": dict(blob.metadata) if blob.metadata else {}
                            }
                        ))
                        
            except Exception as e:
                logger.error(f"Error collecting GCP Storage logs from {bucket_name}: {str(e)}")
                
        return logs
        
    async def collect_audit_logs(
        self,
        service: GCPService,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect Cloud Audit logs."""
        logs = []
        
        start_time = start_time or (datetime.now(UTC) - timedelta(minutes=5))
        
        # Build the filter string for audit logs
        filter_str = [
            f'timestamp >= "{start_time.isoformat()}Z"',
            'resource.type="audited_resource"'
        ]
        
        if end_time:
            filter_str.append(f'timestamp <= "{end_time.isoformat()}Z"')
            
        filter_str = " AND ".join(filter_str)
        
        try:
            entries = self.logging_client.list_entries(
                project_ids=[service.project_id],
                filter_=filter_str,
                order_by="timestamp desc",
                page_size=1000
            )
            
            for entry in entries:
                logs.append(LogEvent(
                    source=f"gcp.{service.name}.audit",
                    event_type="gcp.audit",
                    timestamp=entry.timestamp,
                    data={
                        "principal_email": entry.principal_email,
                        "method_name": entry.method_name,
                        "resource_name": entry.resource_name,
                        "severity": entry.severity,
                        "message": entry.payload,
                        "operation": entry.operation,
                        "labels": dict(entry.labels) if entry.labels else {}
                    }
                ))
                
        except Exception as e:
            logger.error(f"Error collecting Cloud Audit logs: {str(e)}")
            
        return logs
        
    async def collect_all_logs(
        self,
        service: GCPService,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect all available logs from configured GCP services."""
        all_logs = []
        
        # Collect Stackdriver logs
        logs = await self.collect_stackdriver_logs(service, start_time, end_time)
        all_logs.extend(logs)
        
        # Collect Storage logs
        if service.bucket_names:
            logs = await self.collect_bucket_logs(service)
            all_logs.extend(logs)
            
        # Collect Audit logs
        logs = await self.collect_audit_logs(service, start_time, end_time)
        all_logs.extend(logs)
        
        return all_logs
