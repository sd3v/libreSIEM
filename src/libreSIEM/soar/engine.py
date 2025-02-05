"""SOAR automation engine for LibreSIEM."""

import os
import yaml
import json
import logging
import asyncio
import importlib
from typing import Dict, Any, List, Optional, Type
from datetime import datetime, timezone
from dataclasses import dataclass
from thehive4py.api import TheHiveApi
from cortex4py.api import Api as CortexApi
from ansible_runner import run_async
from libreSIEM.config import Settings, get_settings
from libreSIEM.detection.engine import Alert

logger = logging.getLogger(__name__)

@dataclass
class PlaybookAction:
    """Represents a single action in a playbook."""
    type: str
    name: str
    description: str
    parameters: Dict[str, Any]
    conditions: List[Dict[str, Any]]
    timeout: int = 300  # Default timeout in seconds

@dataclass
class Playbook:
    """Represents an automation playbook."""
    id: str
    name: str
    description: str
    triggers: List[Dict[str, Any]]
    actions: List[PlaybookAction]
    enabled: bool = True

class SOAREngine:
    """SOAR automation engine."""
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        
        # Initialize integrations
        self.thehive = TheHiveApi(
            self.settings.soar.THEHIVE_URL,
            self.settings.soar.THEHIVE_API_KEY
        )
        
        self.cortex = CortexApi(
            self.settings.soar.CORTEX_URL,
            self.settings.soar.CORTEX_API_KEY
        )
        
        # Load playbooks
        self.playbooks = self._load_playbooks()
        
        # Initialize action handlers
        self.action_handlers = {
            'thehive': self._handle_thehive_action,
            'cortex': self._handle_cortex_action,
            'ansible': self._handle_ansible_action,
            'python': self._handle_python_action
        }
        
        logger.info("SOAR engine initialized")
    
    def _load_playbooks(self) -> List[Playbook]:
        """Load playbooks from the playbooks directory."""
        playbooks = []
        playbooks_dir = os.path.join(self.settings.PLAYBOOKS_DIR)
        
        if not os.path.exists(playbooks_dir):
            logger.warning(f"Playbooks directory not found: {playbooks_dir}")
            return playbooks
        
        for root, _, files in os.walk(playbooks_dir):
            for file in files:
                if file.endswith('.yml') or file.endswith('.yaml'):
                    try:
                        with open(os.path.join(root, file)) as f:
                            data = yaml.safe_load(f)
                            playbook = Playbook(
                                id=data['id'],
                                name=data['name'],
                                description=data.get('description', ''),
                                triggers=data['triggers'],
                                actions=[
                                    PlaybookAction(**action)
                                    for action in data['actions']
                                ],
                                enabled=data.get('enabled', True)
                            )
                            playbooks.append(playbook)
                    except Exception as e:
                        logger.error(f"Error loading playbook {file}: {e}")
        
        logger.info(f"Loaded {len(playbooks)} playbooks")
        return playbooks
    
    async def process_alert(self, alert: Alert) -> None:
        """Process an alert through relevant playbooks."""
        matching_playbooks = self._get_matching_playbooks(alert)
        
        if not matching_playbooks:
            logger.debug(f"No matching playbooks for alert {alert.id}")
            return
        
        for playbook in matching_playbooks:
            try:
                logger.info(f"Executing playbook {playbook.id} for alert {alert.id}")
                await self._execute_playbook(playbook, alert)
            except Exception as e:
                logger.error(f"Error executing playbook {playbook.id}: {e}")
    
    def _get_matching_playbooks(self, alert: Alert) -> List[Playbook]:
        """Get playbooks that match the alert's triggers."""
        matching = []
        
        for playbook in self.playbooks:
            if not playbook.enabled:
                continue
            
            for trigger in playbook.triggers:
                if self._matches_trigger(trigger, alert):
                    matching.append(playbook)
                    break
        
        return matching
    
    def _matches_trigger(self, trigger: Dict[str, Any], alert: Alert) -> bool:
        """Check if an alert matches a trigger condition."""
        try:
            field = trigger['field']
            op = trigger['op']
            value = trigger['value']
            
            # Get actual value from alert
            actual = getattr(alert, field, None)
            if actual is None:
                return False
            
            # Compare based on operator
            if op == 'equals':
                return actual == value
            elif op == 'contains':
                return value in str(actual)
            elif op == 'matches':
                return bool(re.match(value, str(actual)))
            elif op == 'in':
                return actual in value
            
        except Exception as e:
            logger.error(f"Error matching trigger: {e}")
            return False
        
        return False
    
    async def _execute_playbook(self, playbook: Playbook, alert: Alert) -> None:
        """Execute a playbook's actions."""
        for action in playbook.actions:
            try:
                # Check conditions
                if not all(self._check_condition(c, alert) for c in action.conditions):
                    logger.debug(f"Skipping action {action.name} due to conditions")
                    continue
                
                # Get handler for action type
                handler = self.action_handlers.get(action.type)
                if not handler:
                    logger.error(f"No handler for action type: {action.type}")
                    continue
                
                # Execute action with timeout
                try:
                    async with asyncio.timeout(action.timeout):
                        await handler(action, alert)
                except asyncio.TimeoutError:
                    logger.error(f"Action {action.name} timed out after {action.timeout}s")
                
            except Exception as e:
                logger.error(f"Error executing action {action.name}: {e}")
    
    def _check_condition(self, condition: Dict[str, Any], alert: Alert) -> bool:
        """Check if a condition is met."""
        return self._matches_trigger(condition, alert)
    
    async def _handle_thehive_action(self, action: PlaybookAction, alert: Alert) -> None:
        """Handle TheHive integration actions."""
        if action.name == 'create_case':
            # Create case in TheHive
            case = self.thehive.case.create(
                title=action.parameters.get('title', alert.title),
                description=action.parameters.get('description', alert.description),
                severity=action.parameters.get('severity', alert.severity),
                tags=action.parameters.get('tags', alert.tags)
            )
            logger.info(f"Created TheHive case: {case.id}")
            
            # Create alert in case
            alert_data = self.thehive.alert.create(
                title=alert.title,
                description=alert.description,
                severity=alert.severity,
                date=int(alert.timestamp.timestamp() * 1000),
                tags=alert.tags,
                type='internal',
                source='LibreSIEM',
                sourceRef=alert.id,
                case=case.id
            )
            logger.info(f"Created TheHive alert: {alert_data.id}")
    
    async def _handle_cortex_action(self, action: PlaybookAction, alert: Alert) -> None:
        """Handle Cortex integration actions."""
        if action.name == 'run_analyzer':
            # Get analyzer
            analyzer_id = action.parameters['analyzer_id']
            data = action.parameters.get('data', {})
            
            # Run analyzer
            job = self.cortex.analyzers.run_by_id(
                analyzer_id,
                data
            )
            logger.info(f"Started Cortex analysis job: {job.id}")
            
            # Wait for results if specified
            if action.parameters.get('wait_for_completion', False):
                while True:
                    job_details = self.cortex.jobs.get_by_id(job.id)
                    if job_details.status in ['Success', 'Failure']:
                        break
                    await asyncio.sleep(5)
                
                if job_details.status == 'Success':
                    logger.info(f"Cortex analysis completed: {job_details.report}")
                else:
                    logger.error(f"Cortex analysis failed: {job_details.report}")
    
    async def _handle_ansible_action(self, action: PlaybookAction, alert: Alert) -> None:
        """Handle Ansible automation actions."""
        if action.name == 'run_playbook':
            # Prepare inventory
            inventory = action.parameters.get('inventory', {})
            
            # Run Ansible playbook
            result = await run_async(
                playbook=action.parameters['playbook'],
                inventory=inventory,
                extravars=action.parameters.get('variables', {}),
                quiet=True
            )
            
            if result.rc != 0:
                logger.error(f"Ansible playbook failed: {result.stderr}")
            else:
                logger.info(f"Ansible playbook completed successfully")
    
    async def _handle_python_action(self, action: PlaybookAction, alert: Alert) -> None:
        """Handle custom Python automation actions."""
        try:
            # Import custom module
            module_path = action.parameters['module']
            function_name = action.parameters['function']
            
            module = importlib.import_module(module_path)
            function = getattr(module, function_name)
            
            # Execute function
            kwargs = action.parameters.get('kwargs', {})
            result = await function(alert=alert, **kwargs)
            
            logger.info(f"Python automation completed: {result}")
            
        except Exception as e:
            logger.error(f"Error in Python automation: {e}")
            raise
