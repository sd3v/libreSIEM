"""Models for the collector service."""

from pydantic import BaseModel, Field, field_validator, AnyUrl, ConfigDict
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, UTC
import re

class LogSource(BaseModel):
    """Log source configuration."""
    name: str = Field(..., description="Name of the log source")
    type: str = Field(..., description="Type of log source (e.g., 'syslog', 'apache', 'aws')")
    format: str = Field(..., description="Format of the logs (e.g., 'json', 'syslog', 'cef')")
    enabled: bool = Field(default=True, description="Whether this source is enabled")
    description: Optional[str] = Field(default=None, description="Description of the log source")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the source")

class LogEvent(BaseModel):
    """Log event model with enhanced validation."""
    source: str = Field(..., min_length=1, max_length=255, description="Source of the log event")
    event_type: str = Field(..., min_length=1, max_length=100, description="Type of event")
    timestamp: Optional[datetime] = Field(default=None, description="Event timestamp")
    vendor: Optional[str] = Field(default=None, description="Vendor of the security device")
    severity: str = Field(
        default="info",
        description="Event severity level",
        pattern="^(debug|info|warning|error|critical)$"
    )
    data: Dict[str, Any] = Field(..., description="Event data")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the event"
    )
    
    @field_validator('timestamp', mode='before')
    def set_timestamp(cls, v):
        """Set timestamp to current UTC time if not provided."""
        if v is None:
            return datetime.now(UTC)
        return v
    
    @field_validator('data')
    def validate_data_size(cls, v):
        """Validate data size is within limits."""
        data_str = str(v)
        if len(data_str) > 1048576:  # 1MB limit
            raise ValueError("Event data exceeds maximum size of 1MB")
        return v
    
    @field_validator('source')
    def validate_source(cls, v):
        """Validate source format."""
        if not re.match(r'^[a-zA-Z0-9_.-]+$', v):
            raise ValueError("Source must contain only alphanumeric characters, dots, hyphens, and underscores")
        return v

    @field_validator('event_type')
    def validate_event_type(cls, v):
        """Validate event type format."""
        if not re.match(r'^[a-zA-Z0-9_.-]+$', v):
            raise ValueError("Event type must contain only alphanumeric characters, dots, hyphens, and underscores")
        return v

class BatchLogEvents(BaseModel):
    """Model for batch log event ingestion."""
    events: List[LogEvent] = Field(..., min_length=1, max_length=1000)
    
    @field_validator('events')
    def validate_batch_size(cls, v):
        """Validate total batch size."""
        total_size = sum(len(str(event.model_dump())) for event in v)
        if total_size > 5242880:  # 5MB limit
            raise ValueError("Total batch size exceeds maximum of 5MB")
        return v

class LogFormat(BaseModel):
    """Log format configuration."""
    name: str = Field(..., description="Name of the log format")
    pattern: str = Field(..., description="Regex pattern for parsing")
    fields: Dict[str, str] = Field(..., description="Field mapping configuration")
    sample: Optional[str] = Field(None, description="Sample log entry")
    description: Optional[str] = Field(None, description="Format description")
    
    @field_validator('pattern')
    def validate_pattern(cls, v):
        """Validate regex pattern is valid."""
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        return v
        
    model_config = ConfigDict(arbitrary_types_allowed=True)
