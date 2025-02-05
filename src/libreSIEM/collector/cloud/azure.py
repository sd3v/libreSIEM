"""Azure integration for LibreSIEM."""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, UTC
from pydantic import BaseModel
from azure.identity import ClientSecretCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.storage.blob import BlobServiceClient
from ..models import LogEvent

logger = logging.getLogger(__name__)

class AzureService(BaseModel):
    """Azure service configuration."""
    name: str
    enabled: bool = True
    subscription_id: str
    resource_groups: List[str]
    workspace_id: Optional[str] = None
    storage_accounts: Optional[List[str]] = None

class AzureCredentials(BaseModel):
    """Azure credentials configuration."""
    tenant_id: str
    client_id: str
    client_secret: str

class AzureIntegration:
    """Azure service integration for collecting logs and events."""
    
    def __init__(self, credentials: AzureCredentials):
        self.credentials = credentials
        self.credential = ClientSecretCredential(
            tenant_id=credentials.tenant_id,
            client_id=credentials.client_id,
            client_secret=credentials.client_secret
        )
        self.logs_client = LogsQueryClient(credential=self.credential)
        
    async def collect_activity_logs(
        self,
        service: AzureService,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect Azure Activity logs."""
        logs = []
        
        start_time = start_time or (datetime.now(UTC) - timedelta(minutes=5))
        end_time = end_time or datetime.now(UTC)
        
        query = """
        AzureActivity
        | where TimeGenerated between(datetime({start_time}) .. datetime({end_time}))
        | where SubscriptionId == '{subscription_id}'
        | project TimeGenerated, OperationName, ResourceGroup, Caller, CallerIpAddress,
                  Level, ResultType, ResourceProvider, ResourceId
        """.format(
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            subscription_id=service.subscription_id
        )
        
        try:
            async with self.logs_client.query_workspace(
                workspace_id=service.workspace_id,
                query=query,
                timespan=timedelta(minutes=5)
            ) as response:
                if response.status == LogsQueryStatus.SUCCESS:
                    for row in response.tables[0].rows:
                        logs.append(LogEvent(
                            source=f"azure.{service.name}.activity",
                            event_type="azure.activity",
                            timestamp=row[0],  # TimeGenerated
                            data={
                                "operation": row[1],
                                "resource_group": row[2],
                                "caller": row[3],
                                "caller_ip": row[4],
                                "level": row[5],
                                "result": row[6],
                                "resource_provider": row[7],
                                "resource_id": row[8]
                            }
                        ))
                    
        except Exception as e:
            logger.error(f"Error collecting Azure Activity logs: {str(e)}")
            
        return logs
        
    async def collect_diagnostic_logs(
        self,
        service: AzureService,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect Azure Diagnostic logs."""
        logs = []
        
        start_time = start_time or (datetime.now(UTC) - timedelta(minutes=5))
        end_time = end_time or datetime.now(UTC)
        
        query = """
        AzureDiagnostics
        | where TimeGenerated between(datetime({start_time}) .. datetime({end_time}))
        | where SubscriptionId == '{subscription_id}'
        | project TimeGenerated, ResourceGroup, ResourceProvider, ResourceId,
                  Category, OperationName, Level, ResultType, Properties
        """.format(
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            subscription_id=service.subscription_id
        )
        
        try:
            async with self.logs_client.query_workspace(
                workspace_id=service.workspace_id,
                query=query,
                timespan=timedelta(minutes=5)
            ) as response:
                if response.status == LogsQueryStatus.SUCCESS:
                    for row in response.tables[0].rows:
                        logs.append(LogEvent(
                            source=f"azure.{service.name}.diagnostic",
                            event_type="azure.diagnostic",
                            timestamp=row[0],  # TimeGenerated
                            data={
                                "resource_group": row[1],
                                "resource_provider": row[2],
                                "resource_id": row[3],
                                "category": row[4],
                                "operation": row[5],
                                "level": row[6],
                                "result": row[7],
                                "properties": row[8]
                            }
                        ))
                    
        except Exception as e:
            logger.error(f"Error collecting Azure Diagnostic logs: {str(e)}")
            
        return logs
        
    async def collect_storage_logs(
        self,
        service: AzureService,
        container_name: str = "$logs"
    ) -> List[LogEvent]:
        """Collect Azure Storage Account logs."""
        logs = []
        
        if not service.storage_accounts:
            return logs
            
        for account_name in service.storage_accounts:
            try:
                blob_service = BlobServiceClient(
                    account_url=f"https://{account_name}.blob.core.windows.net",
                    credential=self.credential
                )
                
                container_client = blob_service.get_container_client(container_name)
                
                for blob in container_client.list_blobs():
                    if not blob.name.endswith('.log'):
                        continue
                        
                    blob_client = container_client.get_blob_client(blob.name)
                    log_content = blob_client.download_blob().readall().decode('utf-8')
                    
                    for line in log_content.splitlines():
                        logs.append(LogEvent(
                            source=f"azure.{service.name}.storage",
                            event_type="azure.storage",
                            timestamp=datetime.now(UTC),  # Use actual timestamp if available
                            data={
                                "storage_account": account_name,
                                "container": container_name,
                                "blob": blob.name,
                                "message": line
                            }
                        ))
                        
            except Exception as e:
                logger.error(f"Error collecting Azure Storage logs from {account_name}: {str(e)}")
                
        return logs
        
    async def collect_all_logs(
        self,
        service: AzureService,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect all available logs from configured Azure services."""
        all_logs = []
        
        # Collect Activity logs
        if service.workspace_id:
            logs = await self.collect_activity_logs(service, start_time, end_time)
            all_logs.extend(logs)
            
            # Collect Diagnostic logs
            logs = await self.collect_diagnostic_logs(service, start_time, end_time)
            all_logs.extend(logs)
            
        # Collect Storage logs
        if service.storage_accounts:
            logs = await self.collect_storage_logs(service)
            all_logs.extend(logs)
            
        return all_logs
