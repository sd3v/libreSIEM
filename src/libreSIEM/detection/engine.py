"""Detection engine for LibreSIEM."""

import os
import re
import json
import yaml
import yara
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone, timedelta
import numpy as np
from sklearn.ensemble import IsolationForest
from dataclasses import dataclass
from libreSIEM.config import Settings, get_settings
from libreSIEM.processor.elasticsearch import ElasticsearchManager

logger = logging.getLogger(__name__)

@dataclass
class Alert:
    """Alert generated by detection rules."""
    id: str
    title: str
    description: str
    severity: str
    timestamp: datetime
    rule_id: str
    rule_name: str
    source_event: Dict[str, Any]
    matched_fields: Dict[str, Any]
    tags: List[str]

class DetectionEngine:
    """Core detection engine supporting multiple rule types."""
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        self.es_manager = ElasticsearchManager(self.settings)
        
        # Load rules
        self.sigma_rules = self._load_sigma_rules()
        self.yara_rules = self._load_yara_rules()
        self.custom_rules = self._load_custom_rules()
        
        # Initialize ML models
        self.ml_models = self._initialize_ml_models()
        
        # Initialize alert manager
        self.alert_manager = AlertManager(self.settings)
        
        logger.info("Detection engine initialized")
    
    def _load_sigma_rules(self) -> Dict[str, Any]:
        """Load Sigma rules from the rules directory."""
        rules = {}
        rules_dir = os.path.join(self.settings.RULES_DIR, 'sigma')
        
        if not os.path.exists(rules_dir):
            logger.warning(f"Sigma rules directory not found: {rules_dir}")
            return rules
        
        for root, _, files in os.walk(rules_dir):
            for file in files:
                if file.endswith('.yml'):
                    try:
                        with open(os.path.join(root, file)) as f:
                            rule = yaml.safe_load(f)
                            rules[rule['id']] = rule
                    except Exception as e:
                        logger.error(f"Error loading Sigma rule {file}: {e}")
        
        logger.info(f"Loaded {len(rules)} Sigma rules")
        return rules
    
    def _load_yara_rules(self) -> Optional[yara.Rules]:
        """Load YARA rules from the rules directory."""
        rules_dir = os.path.join(self.settings.RULES_DIR, 'yara')
        
        if not os.path.exists(rules_dir):
            logger.warning(f"YARA rules directory not found: {rules_dir}")
            return None
        
        try:
            # Compile all .yar files in the directory
            rules_dict = {}
            for root, _, files in os.walk(rules_dir):
                for file in files:
                    if file.endswith('.yar'):
                        with open(os.path.join(root, file)) as f:
                            rules_dict[file] = f.read()
            
            compiled_rules = yara.compile(sources=rules_dict)
            logger.info(f"Loaded YARA rules from {len(rules_dict)} files")
            return compiled_rules
            
        except Exception as e:
            logger.error(f"Error loading YARA rules: {e}")
            return None
    
    def _load_custom_rules(self) -> List[Dict[str, Any]]:
        """Load custom detection rules."""
        rules = []
        rules_dir = os.path.join(self.settings.RULES_DIR, 'custom')
        
        if not os.path.exists(rules_dir):
            logger.warning(f"Custom rules directory not found: {rules_dir}")
            return rules
        
        for root, _, files in os.walk(rules_dir):
            for file in files:
                if file.endswith('.json'):
                    try:
                        with open(os.path.join(root, file)) as f:
                            rule = json.load(f)
                            rules.append(rule)
                    except Exception as e:
                        logger.error(f"Error loading custom rule {file}: {e}")
        
        logger.info(f"Loaded {len(rules)} custom rules")
        return rules
    
    def _initialize_ml_models(self) -> Dict[str, Any]:
        """Initialize ML models for anomaly detection."""
        models = {}
        
        # Initialize models for different event types
        event_types = ['authentication', 'network', 'process', 'file']
        for event_type in event_types:
            models[event_type] = {
                'model': IsolationForest(contamination=0.1, random_state=42),
                'features': self._get_features_for_event_type(event_type),
                'scaler': None,  # Will be fit during training
                'last_training': None
            }
        
        return models
    
    def _get_features_for_event_type(self, event_type: str) -> List[str]:
        """Get relevant features for ML models based on event type."""
        feature_map = {
            'authentication': ['timestamp_hour', 'user_id', 'source_ip', 'success'],
            'network': ['bytes_in', 'bytes_out', 'dest_port', 'protocol'],
            'process': ['cpu_percent', 'memory_percent', 'open_files'],
            'file': ['file_size', 'entropy', 'magic_number']
        }
        return feature_map.get(event_type, [])
    
    async def process_event(self, event: Dict[str, Any]) -> List[Alert]:
        """Process a single event through all detection methods."""
        alerts = []
        
        # Check Sigma rules
        sigma_alerts = await self._check_sigma_rules(event)
        alerts.extend(sigma_alerts)
        
        # Check YARA rules if applicable
        if 'file' in event.get('data', {}):
            yara_alerts = await self._check_yara_rules(event)
            alerts.extend(yara_alerts)
        
        # Check custom rules
        custom_alerts = await self._check_custom_rules(event)
        alerts.extend(custom_alerts)
        
        # Check ML-based anomalies
        ml_alerts = await self._check_ml_anomalies(event)
        alerts.extend(ml_alerts)
        
        # Send alerts through alert manager
        if alerts:
            await self.alert_manager.process_alerts(alerts)
        
        return alerts
    
    async def _check_sigma_rules(self, event: Dict[str, Any]) -> List[Alert]:
        """Check event against Sigma rules."""
        alerts = []
        
        for rule_id, rule in self.sigma_rules.items():
            try:
                if self._match_sigma_rule(rule, event):
                    alert = Alert(
                        id=f"sigma_{rule_id}_{datetime.now(timezone.utc).timestamp()}",
                        title=rule['title'],
                        description=rule.get('description', ''),
                        severity=rule.get('level', 'medium'),
                        timestamp=datetime.now(timezone.utc),
                        rule_id=rule_id,
                        rule_name=rule['title'],
                        source_event=event,
                        matched_fields=self._get_matched_fields(rule, event),
                        tags=rule.get('tags', [])
                    )
                    alerts.append(alert)
            except Exception as e:
                logger.error(f"Error checking Sigma rule {rule_id}: {e}")
        
        return alerts
    
    def _match_sigma_rule(self, rule: Dict[str, Any], event: Dict[str, Any]) -> bool:
        """Match an event against a Sigma rule."""
        try:
            detection = rule.get('detection', {})
            condition = detection.get('condition', 'all of them')
            
            # Handle different condition types
            if condition == 'all of them':
                return all(self._match_sigma_selection(sel, event) 
                         for sel in detection.values() if isinstance(sel, dict))
            elif condition == 'any of them':
                return any(self._match_sigma_selection(sel, event) 
                         for sel in detection.values() if isinstance(sel, dict))
            elif ' and ' in condition:
                parts = condition.split(' and ')
                return all(self._match_sigma_selection(detection[p], event) for p in parts)
            elif ' or ' in condition:
                parts = condition.split(' or ')
                return any(self._match_sigma_selection(detection[p], event) for p in parts)
            
        except Exception as e:
            logger.error(f"Error in Sigma rule matching: {e}")
            return False
        
        return False
    
    def _match_sigma_selection(self, selection: Dict[str, Any], event: Dict[str, Any]) -> bool:
        """Match a Sigma selection against an event."""
        for field, expected in selection.items():
            # Handle nested fields
            value = event
            for part in field.split('.'):
                value = value.get(part, {})
            
            # Handle different match types
            if isinstance(expected, str):
                if not self._match_sigma_value(value, expected):
                    return False
            elif isinstance(expected, list):
                if not any(self._match_sigma_value(value, e) for e in expected):
                    return False
        
        return True
    
    def _match_sigma_value(self, value: Any, expected: str) -> bool:
        """Match a single value against a Sigma pattern."""
        if expected.startswith('*') and expected.endswith('*'):
            pattern = expected.strip('*')
            return pattern in str(value)
        elif expected.startswith('*'):
            pattern = expected.lstrip('*')
            return str(value).endswith(pattern)
        elif expected.endswith('*'):
            pattern = expected.rstrip('*')
            return str(value).startswith(pattern)
        else:
            return str(value) == expected
    
    async def _check_yara_rules(self, event: Dict[str, Any]) -> List[Alert]:
        """Check file content against YARA rules."""
        alerts = []
        
        if not self.yara_rules:
            return alerts
        
        try:
            file_data = event.get('data', {}).get('file', {})
            if not file_data or 'content' not in file_data:
                return alerts
            
            matches = self.yara_rules.match(data=file_data['content'])
            for match in matches:
                alert = Alert(
                    id=f"yara_{match.rule}_{datetime.now(timezone.utc).timestamp()}",
                    title=f"YARA Detection: {match.rule}",
                    description=f"File matched YARA rule: {match.rule}",
                    severity="high",
                    timestamp=datetime.now(timezone.utc),
                    rule_id=match.rule,
                    rule_name=match.rule,
                    source_event=event,
                    matched_fields={'file': file_data.get('path', 'unknown')},
                    tags=['yara', 'malware']
                )
                alerts.append(alert)
        
        except Exception as e:
            logger.error(f"Error in YARA scanning: {e}")
        
        return alerts
    
    async def _check_custom_rules(self, event: Dict[str, Any]) -> List[Alert]:
        """Check event against custom rules."""
        alerts = []
        
        for rule in self.custom_rules:
            try:
                if self._match_custom_rule(rule, event):
                    alert = Alert(
                        id=f"custom_{rule['id']}_{datetime.now(timezone.utc).timestamp()}",
                        title=rule['title'],
                        description=rule.get('description', ''),
                        severity=rule.get('severity', 'medium'),
                        timestamp=datetime.now(timezone.utc),
                        rule_id=rule['id'],
                        rule_name=rule['title'],
                        source_event=event,
                        matched_fields=self._get_matched_fields(rule, event),
                        tags=rule.get('tags', [])
                    )
                    alerts.append(alert)
            except Exception as e:
                logger.error(f"Error checking custom rule {rule.get('id')}: {e}")
        
        return alerts
    
    def _match_custom_rule(self, rule: Dict[str, Any], event: Dict[str, Any]) -> bool:
        """Match an event against a custom rule."""
        try:
            conditions = rule.get('conditions', [])
            operator = rule.get('operator', 'and')
            
            results = []
            for condition in conditions:
                field = condition['field']
                op = condition['op']
                value = condition['value']
                
                # Get actual value from event
                actual = event
                for part in field.split('.'):
                    actual = actual.get(part, {})
                
                # Compare based on operator
                if op == 'equals':
                    results.append(actual == value)
                elif op == 'contains':
                    results.append(value in str(actual))
                elif op == 'regex':
                    results.append(bool(re.match(value, str(actual))))
                elif op == 'greater_than':
                    results.append(float(actual) > float(value))
                elif op == 'less_than':
                    results.append(float(actual) < float(value))
            
            return all(results) if operator == 'and' else any(results)
            
        except Exception as e:
            logger.error(f"Error in custom rule matching: {e}")
            return False
    
    async def _check_ml_anomalies(self, event: Dict[str, Any]) -> List[Alert]:
        """Check for anomalies using ML models."""
        alerts = []
        event_type = event.get('event_type', '').split('.')[0]
        
        if event_type not in self.ml_models:
            return alerts
        
        model_info = self.ml_models[event_type]
        features = model_info['features']
        
        # Extract feature values
        feature_values = []
        for feature in features:
            value = event.get('data', {}).get(feature, 0)
            feature_values.append(float(value))
        
        # Reshape for prediction
        X = np.array(feature_values).reshape(1, -1)
        
        # Make prediction
        try:
            score = model_info['model'].score_samples(X)[0]
            threshold = -0.5  # Adjust based on your needs
            
            if score < threshold:
                alert = Alert(
                    id=f"ml_{event_type}_{datetime.now(timezone.utc).timestamp()}",
                    title=f"ML Anomaly: {event_type}",
                    description=f"Anomalous {event_type} event detected",
                    severity="medium",
                    timestamp=datetime.now(timezone.utc),
                    rule_id=f"ml_{event_type}",
                    rule_name=f"ML Anomaly Detection - {event_type}",
                    source_event=event,
                    matched_fields={'anomaly_score': score},
                    tags=['ml', 'anomaly', event_type]
                )
                alerts.append(alert)
        
        except Exception as e:
            logger.error(f"Error in ML anomaly detection: {e}")
        
        return alerts
    
    def _get_matched_fields(self, rule: Dict[str, Any], event: Dict[str, Any]) -> Dict[str, Any]:
        """Get the fields that matched in a rule."""
        matched = {}
        
        if 'detection' in rule:
            for selection_name, selection in rule['detection'].items():
                if isinstance(selection, dict):
                    for field, expected in selection.items():
                        value = event
                        for part in field.split('.'):
                            value = value.get(part, {})
                        if self._match_sigma_value(value, expected):
                            matched[field] = value
        
        return matched
