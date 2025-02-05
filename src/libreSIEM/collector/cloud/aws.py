"""AWS integration for LibreSIEM."""

import boto3
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, UTC
from pydantic import BaseModel
from botocore.exceptions import ClientError
from ..models import LogEvent

logger = logging.getLogger(__name__)

class AWSService(BaseModel):
    """AWS service configuration."""
    name: str
    enabled: bool = True
    regions: List[str]
    log_groups: Optional[List[str]] = None
    bucket_names: Optional[List[str]] = None

class AWSCredentials(BaseModel):
    """AWS credentials configuration."""
    access_key_id: str
    secret_access_key: str
    region: str = "us-east-1"
    role_arn: Optional[str] = None

class AWSIntegration:
    """AWS service integration for collecting logs and events."""
    
    def __init__(self, credentials: AWSCredentials):
        self.credentials = credentials
        self.session = self._create_session()
        
    def _create_session(self) -> boto3.Session:
        """Create an AWS session with the provided credentials."""
        session_kwargs = {
            "aws_access_key_id": self.credentials.access_key_id,
            "aws_secret_access_key": self.credentials.secret_access_key,
            "region_name": self.credentials.region
        }
        
        if self.credentials.role_arn:
            sts = boto3.client('sts', **session_kwargs)
            assumed_role = sts.assume_role(
                RoleArn=self.credentials.role_arn,
                RoleSessionName="LibreSIEM"
            )
            credentials = assumed_role['Credentials']
            session_kwargs.update({
                "aws_access_key_id": credentials['AccessKeyId'],
                "aws_secret_access_key": credentials['SecretAccessKey'],
                "aws_session_token": credentials['SessionToken']
            })
            
        return boto3.Session(**session_kwargs)
        
    async def collect_cloudwatch_logs(
        self,
        service: AWSService,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect logs from CloudWatch Logs."""
        if not service.log_groups:
            return []
            
        logs = []
        logs_client = self.session.client('logs')
        
        start_time = start_time or (datetime.now(UTC) - timedelta(minutes=5))
        end_time = end_time or datetime.now(UTC)
        
        for log_group in service.log_groups:
            try:
                response = logs_client.filter_log_events(
                    logGroupName=log_group,
                    startTime=int(start_time.timestamp() * 1000),
                    endTime=int(end_time.timestamp() * 1000)
                )
                
                for event in response.get('events', []):
                    logs.append(LogEvent(
                        source=f"aws.{service.name}.cloudwatch",
                        event_type="cloudwatch.logs",
                        timestamp=datetime.fromtimestamp(event['timestamp'] / 1000, UTC),
                        data={
                            "message": event['message'],
                            "log_group": log_group,
                            "log_stream": event.get('logStreamName'),
                            "event_id": event['eventId']
                        }
                    ))
                    
            except ClientError as e:
                logger.error(f"Error collecting CloudWatch logs from {log_group}: {str(e)}")
                
        return logs
        
    async def collect_s3_logs(
        self,
        service: AWSService,
        prefix: Optional[str] = None
    ) -> List[LogEvent]:
        """Collect logs from S3 buckets."""
        if not service.bucket_names:
            return []
            
        logs = []
        s3_client = self.session.client('s3')
        
        for bucket in service.bucket_names:
            try:
                list_kwargs = {"Bucket": bucket}
                if prefix:
                    list_kwargs["Prefix"] = prefix
                    
                response = s3_client.list_objects_v2(**list_kwargs)
                
                for obj in response.get('Contents', []):
                    if not obj['Key'].endswith('.log'):
                        continue
                        
                    obj_response = s3_client.get_object(
                        Bucket=bucket,
                        Key=obj['Key']
                    )
                    
                    log_content = obj_response['Body'].read().decode('utf-8')
                    
                    for line in log_content.splitlines():
                        try:
                            log_data = json.loads(line)
                            logs.append(LogEvent(
                                source=f"aws.{service.name}.s3",
                                event_type="s3.logs",
                                timestamp=datetime.now(UTC),  # Use actual timestamp if available in log
                                data={
                                    "bucket": bucket,
                                    "key": obj['Key'],
                                    **log_data
                                }
                            ))
                        except json.JSONDecodeError:
                            # Handle non-JSON logs
                            logs.append(LogEvent(
                                source=f"aws.{service.name}.s3",
                                event_type="s3.logs",
                                timestamp=datetime.now(UTC),
                                data={
                                    "bucket": bucket,
                                    "key": obj['Key'],
                                    "message": line
                                }
                            ))
                            
            except ClientError as e:
                logger.error(f"Error collecting S3 logs from {bucket}: {str(e)}")
                
        return logs
        
    async def collect_cloudtrail_logs(
        self,
        service: AWSService,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect logs from CloudTrail."""
        logs = []
        cloudtrail = self.session.client('cloudtrail')
        
        start_time = start_time or (datetime.now(UTC) - timedelta(minutes=5))
        end_time = end_time or datetime.now(UTC)
        
        try:
            for region in service.regions:
                response = cloudtrail.lookup_events(
                    StartTime=start_time,
                    EndTime=end_time,
                    MaxResults=50  # Adjust as needed
                )
                
                for event in response.get('Events', []):
                    logs.append(LogEvent(
                        source=f"aws.{service.name}.cloudtrail",
                        event_type="cloudtrail.event",
                        timestamp=event['EventTime'],
                        data={
                            "event_name": event['EventName'],
                            "event_id": event['EventId'],
                            "event_source": event['EventSource'],
                            "username": event.get('Username'),
                            "resources": event.get('Resources', []),
                            "region": region,
                            "raw_event": json.loads(event['CloudTrailEvent'])
                        }
                    ))
                    
        except ClientError as e:
            logger.error(f"Error collecting CloudTrail logs: {str(e)}")
            
        return logs
        
    async def collect_all_logs(
        self,
        service: AWSService,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect all available logs from configured AWS services."""
        all_logs = []
        
        # Collect CloudWatch logs
        if service.log_groups:
            logs = await self.collect_cloudwatch_logs(service, start_time, end_time)
            all_logs.extend(logs)
            
        # Collect S3 logs
        if service.bucket_names:
            logs = await self.collect_s3_logs(service)
            all_logs.extend(logs)
            
        # Collect CloudTrail logs
        logs = await self.collect_cloudtrail_logs(service, start_time, end_time)
        all_logs.extend(logs)
        
        return all_logs
