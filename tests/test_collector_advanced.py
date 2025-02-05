import pytest
from datetime import datetime, UTC, timedelta
from fastapi.testclient import TestClient
import json

def test_ingest_unicode_data(client: TestClient):
    """Test ingesting log with unicode data"""
    test_event = {
        "source": "test-system",
        "event_type": "user-input",
        "data": {
            "user": "测试用户",  # Chinese characters
            "message": "Привет мир",  # Russian text
            "location": "München"  # German umlaut
        }
    }
    
    response = client.post("/ingest", json=test_event)
    assert response.status_code == 200

def test_ingest_nested_data(client: TestClient):
    """Test ingesting deeply nested data"""
    test_event = {
        "source": "test-system",
        "event_type": "complex-event",
        "data": {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "value": "deep-nested-value"
                        }
                    }
                }
            }
        }
    }
    
    response = client.post("/ingest", json=test_event)
    assert response.status_code == 200

def test_ingest_array_data(client: TestClient):
    """Test ingesting array data"""
    test_event = {
        "source": "test-system",
        "event_type": "batch-event",
        "data": {
            "items": [
                {"id": 1, "value": "first"},
                {"id": 2, "value": "second"},
                {"id": 3, "value": "third"}
            ],
            "tags": ["tag1", "tag2", "tag3"]
        }
    }
    
    response = client.post("/ingest", json=test_event)
    assert response.status_code == 200

def test_ingest_special_characters(client: TestClient):
    """Test ingesting data with special characters"""
    test_event = {
        "source": "test-system",
        "event_type": "special-chars",
        "data": {
            "path": "C:\\Windows\\System32",  # Windows path
            "query": "SELECT * FROM users;",  # SQL
            "regex": "^[a-zA-Z0-9]+$",  # Regex
            "html": "<script>alert('test')</script>"  # HTML/JS
        }
    }
    
    response = client.post("/ingest", json=test_event)
    assert response.status_code == 200

def test_ingest_future_timestamp(client: TestClient):
    """Test ingesting event with future timestamp"""
    future_time = datetime.now(UTC) + timedelta(days=1)
    test_event = {
        "source": "test-system",
        "event_type": "future-event",
        "timestamp": future_time.isoformat(),
        "data": {"message": "future event"}
    }
    
    response = client.post("/ingest", json=test_event)
    assert response.status_code == 200

def test_ingest_past_timestamp(client: TestClient):
    """Test ingesting event with past timestamp"""
    past_time = datetime.now(UTC) - timedelta(days=365)
    test_event = {
        "source": "test-system",
        "event_type": "past-event",
        "timestamp": past_time.isoformat(),
        "data": {"message": "past event"}
    }
    
    response = client.post("/ingest", json=test_event)
    assert response.status_code == 200

def test_concurrent_requests(client: TestClient):
    """Test multiple concurrent requests"""
    import concurrent.futures
    
    def make_request():
        test_event = {
            "source": "test-system",
            "event_type": "concurrent-test",
            "data": {"timestamp": datetime.now(UTC).isoformat()}
        }
        return client.post("/ingest", json=test_event)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        responses = [f.result() for f in futures]
    
    assert all(r.status_code == 200 for r in responses)
