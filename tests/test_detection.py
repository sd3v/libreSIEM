"""Test detection engine and alert management."""

import pytest
from unittest.mock import MagicMock, patch
import json
import yaml
from datetime import datetime, timezone
from libreSIEM.detection.engine import DetectionEngine, Alert
from libreSIEM.detection.alerts import AlertManager

@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = MagicMock()
    settings.RULES_DIR = '/tmp/rules'
    settings.notifications.EMAIL_FROM = 'test@example.com'
    settings.notifications.EMAIL_TO = 'admin@example.com'
    settings.notifications.SMTP_HOST = 'localhost'
    settings.notifications.SMTP_PORT = 25
    settings.notifications.SLACK_WEBHOOK_URL = 'https://hooks.slack.com/test'
    return settings

@pytest.fixture
def sample_sigma_rule():
    """Sample Sigma rule for testing."""
    return {
        'id': 'test_rule_1',
        'title': 'Test Sigma Rule',
        'description': 'Rule for testing',
        'level': 'high',
        'detection': {
            'selection': {
                'event_type': 'authentication',
                'data.status': 'failure'
            },
            'condition': 'selection'
        }
    }

@pytest.fixture
def sample_custom_rule():
    """Sample custom rule for testing."""
    return {
        'id': 'custom_rule_1',
        'title': 'Test Custom Rule',
        'description': 'Custom rule for testing',
        'severity': 'medium',
        'conditions': [
            {
                'field': 'data.bytes_out',
                'op': 'greater_than',
                'value': 1000000
            }
        ],
        'operator': 'and'
    }

@pytest.fixture
def sample_event():
    """Sample event for testing."""
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'source': 'test_source',
        'event_type': 'authentication',
        'data': {
            'status': 'failure',
            'user': 'testuser',
            'source_ip': '192.168.1.1'
        }
    }

@pytest.mark.asyncio
async def test_sigma_rule_matching(mock_settings, sample_sigma_rule, sample_event):
    """Test Sigma rule matching."""
    with patch('os.path.exists') as mock_exists, \
         patch('builtins.open') as mock_open:
        # Setup mocks
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = \
            yaml.dump(sample_sigma_rule)
        
        engine = DetectionEngine(mock_settings)
        engine.sigma_rules = {'test_rule_1': sample_sigma_rule}
        
        # Test rule matching
        alerts = await engine._check_sigma_rules(sample_event)
        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.rule_id == 'test_rule_1'
        assert alert.severity == 'high'
        assert alert.source_event == sample_event

@pytest.mark.asyncio
async def test_custom_rule_matching(mock_settings, sample_custom_rule):
    """Test custom rule matching."""
    engine = DetectionEngine(mock_settings)
    engine.custom_rules = [sample_custom_rule]
    
    # Test matching event
    matching_event = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'source': 'test_source',
        'event_type': 'network',
        'data': {
            'bytes_out': 2000000
        }
    }
    
    alerts = await engine._check_custom_rules(matching_event)
    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.rule_id == 'custom_rule_1'
    assert alert.severity == 'medium'
    
    # Test non-matching event
    non_matching_event = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'source': 'test_source',
        'event_type': 'network',
        'data': {
            'bytes_out': 500000
        }
    }
    
    alerts = await engine._check_custom_rules(non_matching_event)
    assert len(alerts) == 0

@pytest.mark.asyncio
async def test_yara_rule_matching(mock_settings):
    """Test YARA rule matching."""
    with patch('yara.compile') as mock_compile:
        # Setup mock YARA rule
        mock_rule = MagicMock()
        mock_rule.rule = 'test_yara_rule'
        mock_compile.return_value.match.return_value = [mock_rule]
        
        engine = DetectionEngine(mock_settings)
        engine.yara_rules = mock_compile.return_value
        
        # Test file event
        file_event = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source': 'test_source',
            'event_type': 'file',
            'data': {
                'file': {
                    'path': '/tmp/test.exe',
                    'content': b'test content'
                }
            }
        }
        
        alerts = await engine._check_yara_rules(file_event)
        assert len(alerts) == 1
        alert = alerts[0]
        assert 'YARA Detection' in alert.title
        assert alert.severity == 'high'

@pytest.mark.asyncio
async def test_ml_anomaly_detection(mock_settings):
    """Test ML-based anomaly detection."""
    engine = DetectionEngine(mock_settings)
    
    # Test anomalous authentication event
    auth_event = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'source': 'test_source',
        'event_type': 'authentication',
        'data': {
            'timestamp_hour': 3,  # Unusual hour
            'user_id': 'admin',
            'source_ip': '192.168.1.1',
            'success': False
        }
    }
    
    alerts = await engine._check_ml_anomalies(auth_event)
    assert len(alerts) > 0
    alert = alerts[0]
    assert 'ML Anomaly' in alert.title
    assert 'authentication' in alert.tags

@pytest.mark.asyncio
async def test_alert_notifications(mock_settings):
    """Test alert notifications through different channels."""
    alert_manager = AlertManager(mock_settings)
    
    # Create test alert
    alert = Alert(
        id='test_alert_1',
        title='Test Alert',
        description='Test alert description',
        severity='high',
        timestamp=datetime.now(timezone.utc),
        rule_id='test_rule',
        rule_name='Test Rule',
        source_event={'source': 'test'},
        matched_fields={'field1': 'value1'},
        tags=['test']
    )
    
    # Test email notification
    with patch('smtplib.SMTP') as mock_smtp:
        await alert_manager.notification_channels['email'].send(asdict(alert))
        mock_smtp.return_value.__enter__.return_value.send_message.assert_called_once()
    
    # Test Slack notification
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 200
        await alert_manager.notification_channels['slack'].send(asdict(alert))
        mock_post.assert_called_once()
    
    # Test severity-based channel selection
    channels = alert_manager._get_channels_for_severity('critical')
    assert 'email' in channels
    assert 'slack' in channels
    
    channels = alert_manager._get_channels_for_severity('low')
    assert 'slack' in channels
    assert 'email' not in channels
