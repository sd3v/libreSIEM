import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from libreSIEM.collector.collector import app
from libreSIEM.config import Settings, get_settings
from tests.test_settings import get_test_settings



@pytest.fixture
def test_app():
    """Test app fixture with mocked settings"""
    app.dependency_overrides[get_settings] = get_test_settings
    return app

@pytest.fixture
def client(test_app):
    """Test client fixture"""
    return TestClient(test_app)
