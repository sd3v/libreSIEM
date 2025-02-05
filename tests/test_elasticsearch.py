"""Test Elasticsearch integration."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from libreSIEM.processor.elasticsearch import ElasticsearchManager
from libreSIEM.config import Settings

@pytest.fixture
def es_settings():
    """Mock Elasticsearch settings."""
    settings = MagicMock()
    elasticsearch = MagicMock()
    elasticsearch.ES_HOSTS = "http://localhost:9200"
    elasticsearch.ES_USERNAME = "elastic"
    elasticsearch.ES_PASSWORD = "changeme"
    elasticsearch.ES_SSL_VERIFY = True
    settings.elasticsearch = elasticsearch
    return settings

@pytest.fixture
def mock_es():
    """Mock Elasticsearch client."""
    with patch('libreSIEM.processor.elasticsearch.Elasticsearch') as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client

def test_elasticsearch_initialization(mock_es, es_settings):
    """Test ElasticsearchManager initialization."""
    manager = ElasticsearchManager(es_settings)
    assert manager.es == mock_es
    
    # Verify template creation
    mock_es.indices.put_index_template.assert_called_once()
    template_call = mock_es.indices.put_index_template.call_args
    template_body = template_call.kwargs['body']
    
    # Verify template settings
    assert template_body['index_patterns'] == ['logs-*']
    assert template_body['template']['settings']['index.lifecycle.name'] == 'libresiem-logs'
    
    # Verify ILM policy creation
    mock_es.ilm.put_lifecycle.assert_called_once()
    policy_call = mock_es.ilm.put_lifecycle.call_args
    policy_body = policy_call.kwargs['policy']['policy']
    
    # Verify policy phases
    assert 'hot' in policy_body['phases']
    assert 'warm' in policy_body['phases']
    assert 'cold' in policy_body['phases']
    assert 'delete' in policy_body['phases']

def test_store_document(mock_es, es_settings):
    """Test document storage."""
    manager = ElasticsearchManager(es_settings)
    
    # Test storing a document
    doc = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'source': 'test',
        'event_type': 'test.event',
        'data': {'message': 'test message'}
    }
    
    manager.store_document(doc)
    mock_es.index.assert_called_once_with(
        index='logs-write',
        document=doc,
        pipeline='logs_enrichment'
    )

def test_search_logs(mock_es, es_settings):
    """Test log searching."""
    manager = ElasticsearchManager(es_settings)
    
    # Test search with time range
    start_time = datetime(2025, 1, 1, tzinfo=timezone.utc)
    end_time = datetime(2025, 2, 1, tzinfo=timezone.utc)
    query = {'match': {'source': 'test'}}
    
    manager.search_logs(query, start_time, end_time)
    mock_es.search.assert_called_once()
    
    search_call = mock_es.search.call_args
    search_body = search_call.kwargs['body']
    
    # Verify search parameters
    assert search_body['query']['bool']['must'] == [query]
    assert search_body['query']['bool']['filter'][0]['range']['timestamp']['gte'] == start_time.isoformat()
    assert search_body['query']['bool']['filter'][0]['range']['timestamp']['lte'] == end_time.isoformat()

@pytest.mark.asyncio
async def test_index_rollover(mock_es, es_settings):
    """Test index rollover."""
    manager = ElasticsearchManager(es_settings)
    
    # Mock that write alias doesn't exist
    mock_es.indices.exists_alias.return_value = False
    
    # Initialize indices
    manager._ensure_current_index()
    
    # Verify initial index creation
    mock_es.indices.create.assert_called_once()
    create_call = mock_es.indices.create.call_args
    assert 'logs-write' in create_call.kwargs['body']['aliases']
    
    # Mock that write alias exists but current index doesn't
    mock_es.indices.exists_alias.return_value = True
    mock_es.indices.exists.return_value = False
    
    # Test rollover
    manager._ensure_current_index()
    mock_es.indices.rollover.assert_called_once_with(alias='logs-write')
