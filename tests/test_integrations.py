"""Test script for cloud and security integrations."""

import asyncio
import logging
from datetime import datetime, timedelta, UTC
from libreSIEM.collector.cloud import AWSIntegration, AzureIntegration, GCPIntegration
from libreSIEM.collector.cloud.aws import AWSCredentials, AWSService
from libreSIEM.collector.cloud.azure import AzureCredentials, AzureService
from libreSIEM.collector.cloud.gcp import GCPCredentials, GCPService
from libreSIEM.collector.security import FirewallIntegration, IDSIntegration, EndpointIntegration
from libreSIEM.collector.security.firewall import FirewallConfig, FirewallVendor
from libreSIEM.collector.security.ids import IDSConfig, IDSVendor
from libreSIEM.collector.security.endpoint import EndpointConfig, EndpointVendor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_aws_integration():
    """Test AWS integration."""
    logger.info("Testing AWS integration...")
    
    # Configure AWS credentials (replace with your test credentials)
    credentials = AWSCredentials(
        access_key_id="YOUR_ACCESS_KEY",
        secret_access_key="YOUR_SECRET_KEY",
        region="us-east-1"
    )
    
    # Configure AWS service
    service = AWSService(
        name="test-aws",
        regions=["us-east-1"],
        log_groups=["/aws/lambda/test"],
        bucket_names=["test-bucket"]
    )
    
    # Initialize integration
    aws = AWSIntegration(credentials)
    
    # Test log collection
    try:
        start_time = datetime.now(UTC) - timedelta(minutes=30)
        logs = await aws.collect_all_logs(service, start_time)
        logger.info(f"Collected {len(logs)} AWS logs")
        for log in logs[:5]:  # Show first 5 logs
            logger.info(f"AWS Log: {log}")
    except Exception as e:
        logger.error(f"AWS test failed: {str(e)}")

async def test_azure_integration():
    """Test Azure integration."""
    logger.info("Testing Azure integration...")
    
    # Configure Azure credentials (replace with your test credentials)
    credentials = AzureCredentials(
        tenant_id="YOUR_TENANT_ID",
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET"
    )
    
    # Configure Azure service
    service = AzureService(
        name="test-azure",
        subscription_id="YOUR_SUBSCRIPTION_ID",
        resource_groups=["test-rg"],
        workspace_id="YOUR_WORKSPACE_ID"
    )
    
    # Initialize integration
    azure = AzureIntegration(credentials)
    
    # Test log collection
    try:
        start_time = datetime.now(UTC) - timedelta(minutes=30)
        logs = await azure.collect_all_logs(service, start_time)
        logger.info(f"Collected {len(logs)} Azure logs")
        for log in logs[:5]:  # Show first 5 logs
            logger.info(f"Azure Log: {log}")
    except Exception as e:
        logger.error(f"Azure test failed: {str(e)}")

async def test_firewall_integration():
    """Test firewall integration."""
    logger.info("Testing firewall integration...")
    
    # Configure firewall (replace with your test device details)
    config = FirewallConfig(
        name="test-firewall",
        vendor=FirewallVendor.PALO_ALTO,
        host="192.168.1.1",
        username="admin",
        password="password",
        syslog_port=514
    )
    
    # Initialize integration
    firewall = FirewallIntegration()
    
    # Test log collection
    try:
        logs = await firewall.collect_logs(config)
        logger.info(f"Collected {len(logs)} firewall logs")
        for log in logs[:5]:  # Show first 5 logs
            logger.info(f"Firewall Log: {log}")
    except Exception as e:
        logger.error(f"Firewall test failed: {str(e)}")

async def test_ids_integration():
    """Test IDS integration."""
    logger.info("Testing IDS integration...")
    
    # Configure IDS (replace with your test device details)
    config = IDSConfig(
        name="test-ids",
        vendor=IDSVendor.SURICATA,
        log_path="/var/log/suricata",
        eve_json_path="/var/log/suricata/eve.json"
    )
    
    # Initialize integration
    ids = IDSIntegration()
    
    # Test log collection
    try:
        logs = await ids.collect_logs(config)
        logger.info(f"Collected {len(logs)} IDS logs")
        for log in logs[:5]:  # Show first 5 logs
            logger.info(f"IDS Log: {log}")
    except Exception as e:
        logger.error(f"IDS test failed: {str(e)}")

async def test_endpoint_integration():
    """Test endpoint security integration."""
    logger.info("Testing endpoint security integration...")
    
    # Configure endpoint security (replace with your test credentials)
    config = EndpointConfig(
        name="test-endpoint",
        vendor=EndpointVendor.CROWDSTRIKE,
        api_url="https://api.crowdstrike.com",
        api_key="YOUR_API_KEY"
    )
    
    # Initialize integration
    endpoint = EndpointIntegration()
    
    # Test log collection
    try:
        start_time = datetime.now(UTC) - timedelta(minutes=30)
        logs = await endpoint.collect_logs(config, start_time)
        logger.info(f"Collected {len(logs)} endpoint security logs")
        for log in logs[:5]:  # Show first 5 logs
            logger.info(f"Endpoint Log: {log}")
    except Exception as e:
        logger.error(f"Endpoint security test failed: {str(e)}")
    finally:
        await endpoint.close()

async def main():
    """Run all integration tests."""
    logger.info("Starting integration tests...")
    
    # Run tests
    await test_aws_integration()
    await test_azure_integration()
    await test_firewall_integration()
    await test_ids_integration()
    await test_endpoint_integration()
    
    logger.info("Integration tests completed")

if __name__ == "__main__":
    asyncio.run(main())
