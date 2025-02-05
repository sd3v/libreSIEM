"""Test enrichment processors."""

import pytest
from unittest.mock import MagicMock, patch
import json
from datetime import datetime, timezone
from libreSIEM.processor.enrichment import EnrichmentProcessor

@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = MagicMock()
    settings.storage.STORAGE_TYPE = 'aws'
    settings.storage.AWS_ACCESS_KEY = 'test_key'
    settings.storage.AWS_SECRET_KEY = 'test_secret'
    settings.storage.AWS_REGION = 'us-east-1'
    settings.storage.ARCHIVE_BUCKET = 'test-bucket'
    settings.threat_intel.API_KEY = 'test_api_key'
    return settings

@pytest.fixture
def sample_log_event():
    """Sample log event for testing."""
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'source': 'test_source',
        'event_type': 'security.alert',
        'data': {
            'severity': 'high',
            'message': 'Suspicious activity detected from 192.168.1.1',
            'hostname': 'suspicious.example.com',
            'file_hash': 'a1b2c3d4e5f6'
        }
    }

@pytest.mark.asyncio
async def test_geoip_enrichment():
    """Test GeoIP enrichment."""
    with patch('geoip2.database.Reader') as mock_reader:
        mock_response = MagicMock()
        mock_response.country.iso_code = 'US'
        mock_response.city.name = 'New York'
        mock_response.location.latitude = 40.7128
        mock_response.location.longitude = -74.0060
        mock_response.traits.autonomous_system_number = 12345
        mock_reader.return_value.city.return_value = mock_response
        
        processor = EnrichmentProcessor()
        enriched = await processor._enrich_geoip({'data': {'ip': '192.168.1.1'}})
        
        assert enriched is not None
        assert 'ip_info' in enriched.get('enriched', {})
        ip_info = enriched['enriched']['ip_info'].get('192.168.1.1', {})
        assert ip_info.get('country') == 'US'
        assert ip_info.get('city') == 'New York'
        assert ip_info.get('location', {}).get('lat') == 40.7128
        assert ip_info.get('location', {}).get('lon') == -74.0060
        assert ip_info.get('asn') == 12345

@pytest.mark.asyncio
async def test_dns_enrichment():
    """Test DNS enrichment."""
    with patch('aiodns.DNSResolver') as mock_resolver:
        mock_response = [MagicMock()]
        mock_response[0].host = '192.168.1.1'
        mock_resolver.return_value.query.return_value = mock_response
        
        processor = EnrichmentProcessor()
        processor.dns_resolver = mock_resolver.return_value
        
        enriched = await processor._enrich_dns({'data': {'hostname': 'example.com'}})
        
        assert enriched is not None
        assert 'dns_info' in enriched.get('enriched', {})
        dns_info = enriched['enriched']['dns_info'].get('example.com', {})
        assert '192.168.1.1' in dns_info.get('ip_addresses', [])

@pytest.mark.asyncio
async def test_threat_intel_enrichment():
    """Test threat intelligence enrichment."""
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            'data': {
                'abuseConfidenceScore': 90,
                'categories': ['malware'],
                'lastReportedAt': '2025-02-05T14:00:00Z'
            }
        }
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_response
        
        processor = EnrichmentProcessor()
        processor.threat_session = mock_session.return_value
        
        enriched = await processor._enrich_threat_intel({'data': {'ip': '192.168.1.1'}})
        
        assert enriched is not None
        assert 'threat_intel' in enriched.get('enriched', {})
        threat_info = enriched['enriched']['threat_intel'].get('192.168.1.1', {})
        assert threat_info.get('score') == 90
        assert 'malware' in threat_info.get('categories', [])

@pytest.mark.asyncio
async def test_deduplication():
    """Test log deduplication."""
    processor = EnrichmentProcessor()
    
    # Create two identical events
    event1 = {
        'source': 'test',
        'event_type': 'alert',
        'data': {'message': 'test message'}
    }
    event2 = event1.copy()
    
    # First event should be processed
    result1 = processor._is_duplicate(event1)
    assert result1 is False
    
    # Second identical event should be marked as duplicate
    result2 = processor._is_duplicate(event2)
    assert result2 is True
    
    # Different event should not be marked as duplicate
    event3 = {
        'source': 'test',
        'event_type': 'alert',
        'data': {'message': 'different message'}
    }
    result3 = processor._is_duplicate(event3)
    assert result3 is False

@pytest.mark.asyncio
async def test_cold_storage_archival(mock_settings):
    """Test archival to cold storage."""
    with patch('boto3.client') as mock_boto:
        processor = EnrichmentProcessor(mock_settings)
        
        # Test archival of high severity event
        high_severity_event = {
            'timestamp': '2025-02-05T14:00:00Z',
            'source': 'test',
            'id': '123',
            'data': {'severity': 'high'}
        }
        
        await processor._archive_to_cold_storage(high_severity_event)
        
        mock_boto.return_value.put_object.assert_called_once()
        call_args = mock_boto.return_value.put_object.call_args
        assert call_args.kwargs['Bucket'] == 'test-bucket'
        assert '2025/02/05' in call_args.kwargs['Key']
        assert json.loads(call_args.kwargs['Body']) == high_severity_event
        
        # Test that low severity event is not archived
        low_severity_event = {
            'timestamp': '2025-02-05T14:00:00Z',
            'source': 'test',
            'id': '124',
            'data': {'severity': 'low'}
        }
        
        mock_boto.return_value.put_object.reset_mock()
        await processor._archive_to_cold_storage(low_severity_event)
        mock_boto.return_value.put_object.assert_not_called()
