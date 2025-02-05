"""Test SOAR automation engine."""

import pytest
from unittest.mock import MagicMock, patch
import yaml
from datetime import datetime, timezone
from libreSIEM.soar.engine import SOAREngine, Playbook, PlaybookAction
from libreSIEM.detection.engine import Alert

@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = MagicMock()
    settings.PLAYBOOKS_DIR = '/tmp/playbooks'
    settings.soar.THEHIVE_URL = 'http://localhost:9000'
    settings.soar.THEHIVE_API_KEY = 'test_key'
    settings.soar.CORTEX_URL = 'http://localhost:9001'
    settings.soar.CORTEX_API_KEY = 'test_key'
    return settings

@pytest.fixture
def sample_playbook():
    """Sample playbook for testing."""
    return Playbook(
        id='test_playbook',
        name='Test Playbook',
        description='Playbook for testing',
        triggers=[
            {
                'field': 'severity',
                'op': 'equals',
                'value': 'high'
            }
        ],
        actions=[
            PlaybookAction(
                type='thehive',
                name='create_case',
                description='Create case in TheHive',
                parameters={
                    'title': 'Test Case',
                    'description': 'Test description',
                    'severity': 3
                },
                conditions=[]
            )
        ],
        enabled=True
    )

@pytest.fixture
def sample_alert():
    """Sample alert for testing."""
    return Alert(
        id='test_alert_1',
        title='Test Alert',
        description='Test alert description',
        severity='high',
        timestamp=datetime.now(timezone.utc),
        rule_id='test_rule',
        rule_name='Test Rule',
        source_event={'source': 'test'},
        matched_fields={'source_ip': '192.168.1.1'},
        tags=['security']
    )

@pytest.mark.asyncio
async def test_playbook_loading(mock_settings):
    """Test playbook loading."""
    with patch('os.path.exists') as mock_exists, \
         patch('builtins.open') as mock_open:
        # Setup mocks
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = yaml.dump({
            'id': 'test_playbook',
            'name': 'Test Playbook',
            'description': 'Test description',
            'triggers': [{'field': 'severity', 'op': 'equals', 'value': 'high'}],
            'actions': [{
                'type': 'thehive',
                'name': 'create_case',
                'description': 'Create case',
                'parameters': {},
                'conditions': []
            }]
        })
        
        engine = SOAREngine(mock_settings)
        assert len(engine.playbooks) == 1
        playbook = engine.playbooks[0]
        assert playbook.id == 'test_playbook'
        assert len(playbook.actions) == 1

@pytest.mark.asyncio
async def test_trigger_matching(mock_settings, sample_playbook, sample_alert):
    """Test playbook trigger matching."""
    engine = SOAREngine(mock_settings)
    engine.playbooks = [sample_playbook]
    
    # Test matching alert
    matching_playbooks = engine._get_matching_playbooks(sample_alert)
    assert len(matching_playbooks) == 1
    assert matching_playbooks[0].id == 'test_playbook'
    
    # Test non-matching alert
    non_matching_alert = sample_alert
    non_matching_alert.severity = 'low'
    matching_playbooks = engine._get_matching_playbooks(non_matching_alert)
    assert len(matching_playbooks) == 0

@pytest.mark.asyncio
async def test_thehive_integration(mock_settings, sample_playbook, sample_alert):
    """Test TheHive integration."""
    with patch('thehive4py.api.TheHiveApi') as mock_thehive:
        engine = SOAREngine(mock_settings)
        
        # Mock TheHive responses
        mock_case = MagicMock()
        mock_case.id = 'case_1'
        mock_thehive.return_value.case.create.return_value = mock_case
        
        mock_alert = MagicMock()
        mock_alert.id = 'alert_1'
        mock_thehive.return_value.alert.create.return_value = mock_alert
        
        # Execute TheHive action
        action = sample_playbook.actions[0]
        await engine._handle_thehive_action(action, sample_alert)
        
        # Verify case creation
        mock_thehive.return_value.case.create.assert_called_once()
        mock_thehive.return_value.alert.create.assert_called_once()

@pytest.mark.asyncio
async def test_cortex_integration(mock_settings, sample_alert):
    """Test Cortex integration."""
    with patch('cortex4py.api.Api') as mock_cortex:
        engine = SOAREngine(mock_settings)
        
        # Create Cortex action
        action = PlaybookAction(
            type='cortex',
            name='run_analyzer',
            description='Run Cortex analyzer',
            parameters={
                'analyzer_id': 'Virustotal_GetReport_3_0',
                'data': {'data': 'test_hash'},
                'wait_for_completion': True
            },
            conditions=[]
        )
        
        # Mock Cortex responses
        mock_job = MagicMock()
        mock_job.id = 'job_1'
        mock_cortex.return_value.analyzers.run_by_id.return_value = mock_job
        
        mock_job_details = MagicMock()
        mock_job_details.status = 'Success'
        mock_job_details.report = {'results': 'test_results'}
        mock_cortex.return_value.jobs.get_by_id.return_value = mock_job_details
        
        # Execute Cortex action
        await engine._handle_cortex_action(action, sample_alert)
        
        # Verify analyzer execution
        mock_cortex.return_value.analyzers.run_by_id.assert_called_once()
        mock_cortex.return_value.jobs.get_by_id.assert_called()

@pytest.mark.asyncio
async def test_ansible_integration(mock_settings, sample_alert):
    """Test Ansible integration."""
    with patch('ansible_runner.run_async') as mock_run:
        engine = SOAREngine(mock_settings)
        
        # Create Ansible action
        action = PlaybookAction(
            type='ansible',
            name='run_playbook',
            description='Run Ansible playbook',
            parameters={
                'playbook': 'test_playbook.yml',
                'inventory': {'hosts': ['localhost']},
                'variables': {'test_var': 'test_value'}
            },
            conditions=[]
        )
        
        # Mock Ansible response
        mock_result = MagicMock()
        mock_result.rc = 0
        mock_run.return_value = mock_result
        
        # Execute Ansible action
        await engine._handle_ansible_action(action, sample_alert)
        
        # Verify playbook execution
        mock_run.assert_called_once()

@pytest.mark.asyncio
async def test_python_automation(mock_settings, sample_alert):
    """Test custom Python automation."""
    with patch('importlib.import_module') as mock_import:
        engine = SOAREngine(mock_settings)
        
        # Create Python action
        action = PlaybookAction(
            type='python',
            name='custom_enrichment',
            description='Run custom enrichment',
            parameters={
                'module': 'test_module',
                'function': 'test_function',
                'kwargs': {'test_param': 'test_value'}
            },
            conditions=[]
        )
        
        # Mock Python module
        mock_module = MagicMock()
        mock_function = MagicMock()
        mock_function.return_value = {'result': 'success'}
        mock_module.test_function = mock_function
        mock_import.return_value = mock_module
        
        # Execute Python action
        await engine._handle_python_action(action, sample_alert)
        
        # Verify function execution
        mock_function.assert_called_once()
