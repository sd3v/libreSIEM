"""IDS/IPS integration for LibreSIEM."""

import logging
import asyncio
import aiofiles
import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, UTC
from pydantic import BaseModel, ConfigDict, field_validator
import asyncssh
from ..models import LogEvent
from ..parsers import LogParser

logger = logging.getLogger(__name__)

from enum import Enum

class IDSVendor(str, Enum):
    """Supported IDS/IPS vendors."""
    SNORT = "snort"
    SURICATA = "suricata"
    ZEEK = "zeek"
    OSSEC = "ossec"

class IDSConfig(BaseModel):
    """Configuration for an IDS/IPS device."""
    name: str
    vendor: IDSVendor
    enabled: bool = True
    host: Optional[str] = None
    port: int = 22
    username: Optional[str] = None
    password: Optional[str] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    private_key: Optional[str] = None
    log_path: Optional[str] = None
    eve_json_path: Optional[str] = None

    @field_validator('vendor')
    def validate_vendor(cls, v):
        """Ensure vendor is supported."""
        if v not in IDSVendor:
            raise ValueError(f"Unsupported vendor: {v}")
        return v
    alert_log_path: Optional[str] = None

class IDSIntegration:
    """Integration for collecting logs from IDS/IPS devices."""
    
    def __init__(self):
        self.parser = LogParser()
        self._vendor_patterns = {
            IDSVendor.SNORT: {
                "alert": r"\[\*\*\]\s+\[(?P<sid>\d+):(?P<rev>\d+)\]\s+(?P<message>[^\[]+)\s+\[Classification:\s+(?P<classification>[^\]]+)\]\s+\[Priority:\s+(?P<priority>\d+)\]\s+{(?P<protocol>[^}]+)}\s+(?P<src_ip>[^:]+):(?P<src_port>\d+)\s+->\s+(?P<dst_ip>[^:]+):(?P<dst_port>\d+)"
            },
            IDSVendor.SURICATA: {
                "alert": r"(?P<timestamp>[^\s]+)\s+\[(?P<sid>\d+):(?P<rev>\d+)\]\s+(?P<message>[^\[]+)\s+\[Classification:\s+(?P<classification>[^\]]+)\]\s+\[Priority:\s+(?P<priority>\d+)\]\s+{(?P<protocol>[^}]+)}"
            },
            IDSVendor.OSSEC: {
                "alert": r"(?P<timestamp>[^\s]+)\s+(?P<hostname>[^\s]+)\s+(?P<location>[^\s]+)\s+(?P<rule_id>\d+)\s+-\s+(?P<message>.*)"
            }
        }
        
    def _parse_log_line(self, line: str, vendor: IDSVendor) -> Optional[Dict[str, Any]]:
        """Parse a log line based on vendor-specific patterns."""
        patterns = self._vendor_patterns.get(vendor, {})
        
        for log_type, pattern in patterns.items():
            match = re.match(pattern, line)
            if match:
                data = match.groupdict()
                data['type'] = log_type.lower()
                return data
                
        return None
        
    async def collect_file_logs(
        self,
        config: IDSConfig,
        start_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect logs from local log files."""
        logs = []
        
        if not config.log_path and not config.eve_json_path and not config.alert_log_path:
            return logs
            
        try:
            # Handle Suricata eve.json
            if config.eve_json_path and config.vendor == IDSVendor.SURICATA:
                async with aiofiles.open(config.eve_json_path, mode='r') as f:
                    async for line in f:
                        try:
                            event = json.loads(line)
                            if event.get('event_type') == 'alert':
                                logs.append(LogEvent(
                                    source=f"ids.{config.name}",
                                    event_type="ids.alert",
                                    timestamp=datetime.fromisoformat(event['timestamp']),
                                    data={
                                        "vendor": config.vendor,
                                        "alert": event
                                    }
                                ))
                        except json.JSONDecodeError:
                            continue
                            
            # Handle Snort/OSSEC alert logs
            if config.alert_log_path:
                async with aiofiles.open(config.alert_log_path, mode='r') as f:
                    async for line in f:
                        parsed = self._parse_log_line(line, config.vendor)
                        if parsed:
                            logs.append(LogEvent(
                                source=f"ids.{config.name}",
                                event_type=f"ids.{parsed['type']}",
                                timestamp=datetime.now(UTC),  # Use parsed timestamp if available
                                data={
                                    "vendor": config.vendor,
                                    "raw_message": line,
                                    **parsed
                                }
                            ))
                            
            # Handle Zeek logs
            if config.log_path and config.vendor == IDSVendor.ZEEK:
                log_files = ['conn.log', 'http.log', 'dns.log', 'ssl.log', 'x509.log']
                for log_file in log_files:
                    try:
                        path = f"{config.log_path}/{log_file}"
                        async with aiofiles.open(path, mode='r') as f:
                            async for line in f:
                                if line.startswith('#'):
                                    continue
                                fields = line.strip().split('\t')
                                if len(fields) > 1:
                                    logs.append(LogEvent(
                                        source=f"ids.{config.name}",
                                        event_type=f"ids.zeek.{log_file.replace('.log', '')}",
                                        timestamp=datetime.now(UTC),
                                        data={
                                            "vendor": config.vendor,
                                            "raw_message": line,
                                            "fields": fields
                                        }
                                    ))
                    except FileNotFoundError:
                        continue
                        
        except Exception as e:
            logger.error(f"Error collecting file logs from IDS {config.name}: {str(e)}")
            
        return logs
        
    async def collect_remote_logs(
        self,
        config: IDSConfig,
        start_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect logs via SSH from remote IDS/IPS."""
        logs = []
        
        if not config.host or not config.username:
            return logs
            
        try:
            async with asyncssh.connect(
                config.host,
                port=config.port,
                username=config.username,
                password=config.password,
                client_keys=[config.private_key] if config.private_key else None,
                known_hosts=None  # In production, use known_hosts
            ) as conn:
                # Get logs based on vendor
                if config.vendor == IDSVendor.SNORT:
                    cmd = f"tail -n 1000 {config.alert_log_path}"
                elif config.vendor == IDSVendor.SURICATA:
                    cmd = f"tail -n 1000 {config.eve_json_path}"
                elif config.vendor == IDSVendor.OSSEC:
                    cmd = "tail -n 1000 /var/ossec/logs/alerts/alerts.log"
                else:
                    return logs
                    
                result = await conn.run(cmd)
                
                for line in result.stdout.splitlines():
                    if config.vendor == IDSVendor.SURICATA:
                        try:
                            event = json.loads(line)
                            if event.get('event_type') == 'alert':
                                logs.append(LogEvent(
                                    source=f"ids.{config.name}",
                                    event_type="ids.alert",
                                    timestamp=datetime.fromisoformat(event['timestamp']),
                                    data={
                                        "vendor": config.vendor,
                                        "alert": event
                                    }
                                ))
                        except json.JSONDecodeError:
                            continue
                    else:
                        parsed = self._parse_log_line(line, config.vendor)
                        if parsed:
                            logs.append(LogEvent(
                                source=f"ids.{config.name}",
                                event_type=f"ids.{parsed['type']}",
                                timestamp=datetime.now(UTC),
                                data={
                                    "vendor": config.vendor,
                                    "raw_message": line,
                                    **parsed
                                }
                            ))
                            
        except Exception as e:
            logger.error(f"Error collecting remote logs from IDS {config.name}: {str(e)}")
            
        return logs
        
    async def collect_logs(
        self,
        config: IDSConfig,
        start_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect logs from an IDS/IPS using all available methods."""
        all_logs = []
        
        # Collect from local files
        logs = await self.collect_file_logs(config, start_time)
        all_logs.extend(logs)
        
        # Collect from remote system if configured
        if config.host and config.username:
            logs = await self.collect_remote_logs(config, start_time)
            all_logs.extend(logs)
            
        return all_logs
