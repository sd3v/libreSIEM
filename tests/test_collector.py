import pytest
from datetime import datetime, UTC
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_ingest_valid_log(client: TestClient):
    """Test ingesting a valid log event"""
    test_event = {
        "source": "test-system",
        "event_type": "login",
        "data": {
            "user": "testuser",
            "ip": "192.168.1.100",
            "status": "success"
        }
    }
    
    response = client.post("/ingest", json=test_event)
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Event ingested successfully"
    }

def test_ingest_invalid_log(client: TestClient):
    """Test ingesting an invalid log event"""
    invalid_event = {
        "source": "test-system",
        # Missing required field event_type
        "data": {}
    }
    
    response = client.post("/ingest", json=invalid_event)
    assert response.status_code == 422  # Validation error

def test_ingest_with_timestamp(client: TestClient):
    """Test ingesting a log event with timestamp"""
    test_event = {
        "source": "test-system",
        "event_type": "login",
        "timestamp": datetime.now(UTC).isoformat(),
        "data": {
            "user": "testuser",
            "ip": "192.168.1.100",
            "status": "success"
        }
    }
    
    response = client.post("/ingest", json=test_event)
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Event ingested successfully"
    }

def test_ingest_large_payload(client: TestClient):
    """Test ingesting a large log event"""
    large_data = {f"key_{i}": f"value_{i}" for i in range(1000)}
    test_event = {
        "source": "test-system",
        "event_type": "large-event",
        "data": large_data
    }
    
    response = client.post("/ingest", json=test_event)
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Event ingested successfully"
    }
