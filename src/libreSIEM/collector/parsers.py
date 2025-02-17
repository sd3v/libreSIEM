"""Log parsing utilities for the collector service."""

import re
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from .models import LogFormat, LogEvent

logger = logging.getLogger(__name__)

class LogParser:
    """Parser for various log formats."""
    
    def __init__(self):
        self.formats: Dict[str, LogFormat] = {}
        self._load_default_formats()
    
    def _load_default_formats(self):
        """Load default log format patterns."""
        # Common log formats
        self.add_format(LogFormat(
            name="syslog",
            pattern=r"^(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(?P<host>[\w\-]+)\s+(?P<program>[\w\-\[\]]+):\s+(?P<message>.*)$",
            fields={
                "timestamp": "datetime",
                "host": "string",
                "program": "string",
                "message": "string"
            },
            sample="Feb  5 12:23:09 myhost program[123]: Sample log message"
        ))
        
        self.add_format(LogFormat(
            name="apache_combined",
            pattern=r'^(?P<remote_host>[\w\-\.:\[\]]+)\s+(?P<ident>\S+)\s+(?P<user>\S+)\s+\[(?P<timestamp>[^\]]+)\]\s+"(?P<request>[^"]*?)"\s+(?P<status>\d+)\s+(?P<bytes>\d+)\s+"(?P<referrer>[^"]*?)"\s+"(?P<user_agent>[^"]*?)"$',
            fields={
                "remote_host": "string",
                "ident": "string",
                "user": "string",
                "timestamp": "datetime",
                "request": "string",
                "status": "integer",
                "bytes": "integer",
                "referrer": "string",
                "user_agent": "string"
            },
            sample='127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326 "http://www.example.com/start.html" "Mozilla/4.08 [en] (Win98; I ;Nav)"'
        ))
        
        # Palo Alto firewall format
        self.add_format(LogFormat(
            name="paloalto",
            pattern=r"^(?P<event_type>\w+),(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}),(?P<serial>[\w\-]+),(?P<type>\w+),(?P<subtype>\w+),(?P<source_ip>[\d\.]+),(?P<destination_ip>[\d\.]+),(?P<source_port>\d+),(?P<destination_port>\d+),(?P<protocol>\w+)$",
            fields={
                "event_type": "string",
                "timestamp": "datetime",
                "serial": "string",
                "type": "string",
                "subtype": "string",
                "source_ip": "string",
                "destination_ip": "string",
                "source_port": "integer",
                "destination_port": "integer",
                "protocol": "string"
            },
            sample="traffic,2024-02-05 14:11:05,001234567890,traffic,end,10.0.0.1,192.168.1.1,1234,80,TCP"
        ))
        
        # Suricata IDS format
        self.add_format(LogFormat(
            name="suricata",
            pattern=r"^(?P<json>{.*})$",
            fields={"json": "json"},
            sample='{"event_type": "alert", "src_ip": "10.0.0.1", "dest_ip": "192.168.1.1", "alert": {"signature_id": 2001, "category": "Attempted Information Leak", "severity": 2}}'
        ))
        
        # CrowdStrike endpoint format
        self.add_format(LogFormat(
            name="crowdstrike",
            pattern=r"^(?P<json>{.*})$",
            fields={"json": "json"},
            sample='{"device_id": "test-device", "event_type": "DetectionSummaryEvent", "timestamp": "2024-02-05T14:11:05Z", "severity": "high", "detection_name": "Test Detection", "src_ip": "10.0.0.1", "dst_ip": "192.168.1.1"}'
        ))
    
    def add_format(self, format: LogFormat):
        """Add a new log format."""
        self.formats[format.name] = format
    
    def detect_format(self, log_line: str) -> Optional[str]:
        """Detect the format of a log line."""
        for name, format in self.formats.items():
            if re.match(format.pattern, log_line):
                return name
        return None
    
    async def parse_line(self, log_line: str, format_name: Optional[str] = None, source: str = None, event_type: str = "log", vendor: Optional[str] = None) -> Optional[LogEvent]:
        """Parse a log line using the specified or auto-detected format."""
        try:
            # Try JSON first if no format specified
            if not format_name:
                try:
                    data = json.loads(log_line)
                    if isinstance(data, dict):
                        return self.create_event(data, source, event_type, vendor)
                except json.JSONDecodeError:
                    pass
                
                # Auto-detect format
                format_name = self.detect_format(log_line)
                if not format_name:
                    logger.error("Unable to detect log format")
                    return None
            
            if format_name not in self.formats:
                logger.error(f"Unknown format: {format_name}")
                return None
            
            format = self.formats[format_name]
            match = re.match(format.pattern, log_line)
            if not match:
                logger.error(f"Log line does not match format {format_name}")
                return None
            
            # Extract and convert fields
            data = {}
            for field_name, field_type in format.fields.items():
                value = match.group(field_name)
                if field_type == "integer":
                    data[field_name] = int(value)
                elif field_type == "datetime":
                    try:
                        if format_name == "syslog":
                            # Add current year since syslog format doesn't include it
                            current_year = datetime.now().year
                            dt = datetime.strptime(f"{current_year} {value}", "%Y %b %d %H:%M:%S")
                        elif format_name == "apache_combined":
                            # Parse Apache Combined format timestamp
                            dt = datetime.strptime(value, "%d/%b/%Y:%H:%M:%S %z")
                        else:
                            # Default format
                            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        
                        data[field_name] = dt.astimezone().isoformat()
                    except ValueError as e:
                        logger.error(f"Failed to parse timestamp '{value}': {str(e)}")
                        return None
                elif field_type == "json":
                    data.update(json.loads(value))
                else:
                    data[field_name] = value
            
            return self.create_event(data, source, event_type, vendor)
            
        except Exception as e:
            logger.error(f"Error parsing log line: {e}")
            return None
    
    def create_event(self, data: Dict[str, Any], source: str, event_type: str = "log", vendor: Optional[str] = None) -> LogEvent:
        """Create a LogEvent from parsed data."""
        # Extract timestamp if present in common fields
        timestamp = None
        for ts_field in ["timestamp", "@timestamp", "time", "datetime"]:
            if ts_field in data:
                timestamp = data[ts_field]
                del data[ts_field]
                break
        
        return LogEvent(
            source=source,
            event_type=event_type,
            timestamp=timestamp,
            vendor=vendor,
            data=data
        )
