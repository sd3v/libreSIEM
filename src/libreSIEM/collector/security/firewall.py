"""Firewall integration for LibreSIEM."""

import logging
import asyncio
import aiofiles
import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, UTC
from pydantic import BaseModel
import asyncssh
from ..models import LogEvent
from ..parsers import LogParser

logger = logging.getLogger(__name__)

from enum import Enum

class FirewallVendor(str, Enum):
    """Supported firewall vendors."""
    PALO_ALTO = "palo_alto"
    CISCO_ASA = "cisco_asa"
    FORTINET = "fortinet"
    CHECKPOINT = "checkpoint"
    PFSENSE = "pfsense"

class FirewallConfig(BaseModel):
    """Configuration for a firewall device."""
    name: str
    vendor: FirewallVendor
    enabled: bool = True
    host: str
    port: int = 22
    username: str
    
    class Config:
        arbitrary_types_allowed = True
    password: Optional[str] = None
    private_key: Optional[str] = None
    log_path: Optional[str] = None
    syslog_port: Optional[int] = None

class FirewallIntegration:
    """Integration for collecting logs from firewall devices."""
    
    def __init__(self):
        self.parser = LogParser()
        self._vendor_patterns = {
            FirewallVendor.PALO_ALTO: {
                "traffic": r"TRAFFIC,(?P<timestamp>[^,]+),(?P<serial>[^,]+),(?P<type>[^,]+),(?P<subtype>[^,]+),(?P<src_ip>[^,]+),(?P<dst_ip>[^,]+),(?P<src_port>[^,]+),(?P<dst_port>[^,]+),(?P<protocol>[^,]+)",
                "threat": r"THREAT,(?P<timestamp>[^,]+),(?P<serial>[^,]+),(?P<type>[^,]+),(?P<subtype>[^,]+),(?P<src_ip>[^,]+),(?P<dst_ip>[^,]+),(?P<threat_id>[^,]+),(?P<threat_name>[^,]+)"
            },
            FirewallVendor.CISCO_ASA: {
                "traffic": r"%ASA-(?P<level>\d+)-(?P<code>\d+):\s+(?P<message>.*)",
                "vpn": r"%ASA-(?P<level>\d+)-(?P<code>\d+):\s+Group\s+<(?P<group>[^>]+)>\s+User\s+<(?P<user>[^>]+)>"
            },
            FirewallVendor.FORTINET: {
                "traffic": r"type=(?P<type>[^\s]+)\s+.*?src=(?P<src_ip>[^\s]+)\s+dst=(?P<dst_ip>[^\s]+)\s+src_port=(?P<src_port>[^\s]+)\s+dst_port=(?P<dst_port>[^\s]+)",
                "event": r"type=(?P<type>[^\s]+)\s+.*?level=(?P<level>[^\s]+)\s+msg=\"(?P<message>[^\"]+)\""
            }
        }
        
    def _parse_log_line(self, line: str, vendor: FirewallVendor) -> Optional[Dict[str, Any]]:
        """Parse a log line based on vendor-specific patterns."""
        patterns = self._vendor_patterns.get(vendor, {})
        
        for log_type, pattern in patterns.items():
            match = re.match(pattern, line)
            if match:
                return {
                    "type": log_type.lower(),
                    **match.groupdict()
                }
                
        return None
        
    async def collect_ssh_logs(
        self,
        config: FirewallConfig,
        start_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect logs via SSH."""
        logs = []
        
        try:
            # Connect via SSH
            async with asyncssh.connect(
                config.host,
                port=config.port,
                username=config.username,
                password=config.password,
                client_keys=[config.private_key] if config.private_key else None,
                known_hosts=None  # In production, use known_hosts
            ) as conn:
                # Get logs based on vendor
                if config.vendor == FirewallVendor.PALO_ALTO:
                    cmd = "show log traffic"
                elif config.vendor == FirewallVendor.CISCO_ASA:
                    cmd = "show logging | include %ASA"
                elif config.vendor == FirewallVendor.FORTINET:
                    cmd = "execute log filter category 0"
                    await conn.run("execute log display")
                else:
                    cmd = f"tail -n 1000 {config.log_path}" if config.log_path else None
                    
                if cmd:
                    result = await conn.run(cmd)
                    
                    for line in result.stdout.splitlines():
                        parsed = self._parse_log_line(line, config.vendor)
                        if parsed:
                            logs.append(LogEvent(
                                source=f"firewall.{config.name}",
                                event_type=f"firewall.{parsed['type']}",
                                timestamp=datetime.now(UTC),  # Use parsed timestamp if available
                                data={
                                    "vendor": config.vendor,
                                    "raw_message": line,
                                    **parsed
                                }
                            ))
                            
        except Exception as e:
            logger.error(f"Error collecting logs from firewall {config.name}: {str(e)}")
            
        return logs
        
    async def collect_syslog_logs(
        self,
        config: FirewallConfig,
        buffer_size: int = 1024
    ) -> List[LogEvent]:
        """Collect logs via syslog."""
        logs = []
        
        if not config.syslog_port:
            return logs
            
        class SyslogProtocol(asyncio.Protocol):
            def __init__(self, callback):
                self.callback = callback
                self.buffer = ""
                
            def connection_made(self, transport):
                pass
                
            def data_received(self, data):
                self.buffer += data.decode()
                while "\n" in self.buffer:
                    line, self.buffer = self.buffer.split("\n", 1)
                    self.callback(line)
                    
        async def handle_syslog():
            def process_line(line):
                parsed = self._parse_log_line(line, config.vendor)
                if parsed:
                    logs.append(LogEvent(
                        source=f"firewall.{config.name}",
                        event_type=f"firewall.{parsed['type']}",
                        timestamp=datetime.now(UTC),
                        data={
                            "vendor": config.vendor,
                            "raw_message": line,
                            **parsed
                        }
                    ))
                    
            loop = asyncio.get_event_loop()
            await loop.create_server(
                lambda: SyslogProtocol(process_line),
                "0.0.0.0",
                config.syslog_port
            )
            
        try:
            await asyncio.wait_for(handle_syslog(), timeout=10.0)
        except asyncio.TimeoutError:
            logger.info(f"Syslog collection timeout for {config.name}")
        except Exception as e:
            logger.error(f"Error collecting syslog from firewall {config.name}: {str(e)}")
            
        return logs
        
    async def collect_logs(
        self,
        config: FirewallConfig,
        start_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect logs from a firewall using all available methods."""
        all_logs = []
        
        # Collect via SSH if credentials are provided
        if config.username and (config.password or config.private_key):
            logs = await self.collect_ssh_logs(config, start_time)
            all_logs.extend(logs)
            
        # Collect via syslog if port is configured
        if config.syslog_port:
            logs = await self.collect_syslog_logs(config)
            all_logs.extend(logs)
            
        return all_logs
