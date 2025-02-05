"""Endpoint security integration for LibreSIEM."""

import logging
import asyncio
import aiofiles
import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, UTC
from pydantic import BaseModel, HttpUrl, ConfigDict
import aiohttp
from ..models import LogEvent
from ..parsers import LogParser

logger = logging.getLogger(__name__)

from enum import Enum

class EndpointVendor(str, Enum):
    """Supported endpoint security vendors."""
    CROWDSTRIKE = "crowdstrike"
    CARBON_BLACK = "carbon_black"
    SENTINEL_ONE = "sentinel_one"
    SYMANTEC = "symantec"
    MCAFEE = "mcafee"

class EndpointConfig(BaseModel):
    """Configuration for an endpoint security solution."""
    name: str
    vendor: EndpointVendor
    enabled: bool = True
    api_url: HttpUrl
    api_key: str
    api_secret: Optional[str] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    verify_ssl: bool = True
    proxy: Optional[str] = None

class EndpointIntegration:
    """Integration for collecting logs from endpoint security solutions."""
    
    def __init__(self):
        self.parser = LogParser()
        self._session = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
        
    async def _make_request(
        self,
        config: EndpointConfig,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None
    ) -> Dict:
        """Make an authenticated request to the endpoint security API."""
        session = await self._get_session()
        headers = self._get_auth_headers(config)
        
        try:
            async with session.request(
                method,
                f"{config.api_url}{endpoint}",
                headers=headers,
                params=params,
                json=json,
                ssl=config.verify_ssl,
                proxy=config.proxy
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"API request error for {config.name}: {str(e)}")
            raise
            
    def _get_auth_headers(self, config: EndpointConfig) -> Dict[str, str]:
        """Get vendor-specific authentication headers."""
        headers = {"Content-Type": "application/json"}
        
        if config.vendor == EndpointVendor.CROWDSTRIKE:
            headers["Authorization"] = f"Bearer {config.api_key}"
        elif config.vendor == EndpointVendor.CARBON_BLACK:
            headers["X-Auth-Token"] = config.api_key
        elif config.vendor == EndpointVendor.SENTINEL_ONE:
            headers["Authorization"] = f"ApiToken {config.api_key}"
        elif config.vendor == EndpointVendor.SYMANTEC:
            headers["Authorization"] = f"Basic {config.api_key}"
        elif config.vendor == EndpointVendor.MCAFEE:
            headers["X-API-Key"] = config.api_key
            
        return headers
        
    async def collect_alerts(
        self,
        config: EndpointConfig,
        start_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect security alerts from the endpoint solution."""
        logs = []
        start_time = start_time or (datetime.now(UTC) - timedelta(minutes=5))
        
        try:
            if config.vendor == EndpointVendor.CROWDSTRIKE:
                # CrowdStrike Falcon API
                response = await self._make_request(
                    config,
                    "GET",
                    "/detects/queries/detects/v1",
                    params={
                        "filter": f"created_timestamp:>'{start_time.isoformat()}Z'"
                    }
                )
                
                if "resources" in response:
                    for alert_id in response["resources"]:
                        alert_details = await self._make_request(
                            config,
                            "GET",
                            f"/detects/entities/detects/v1",
                            params={"ids": alert_id}
                        )
                        
                        for alert in alert_details.get("resources", []):
                            logs.append(LogEvent(
                                source=f"endpoint.{config.name}",
                                event_type="endpoint.alert",
                                timestamp=datetime.fromtimestamp(
                                    alert["created_timestamp"],
                                    UTC
                                ),
                                data={
                                    "vendor": config.vendor,
                                    "alert": alert
                                }
                            ))
                            
            elif config.vendor == EndpointVendor.CARBON_BLACK:
                # Carbon Black API
                response = await self._make_request(
                    config,
                    "GET",
                    "/api/alerts/v7/orgs/{}/alerts/search",
                    params={
                        "criteria": {
                            "create_time": {
                                "start": start_time.isoformat()
                            }
                        }
                    }
                )
                
                for alert in response.get("results", []):
                    logs.append(LogEvent(
                        source=f"endpoint.{config.name}",
                        event_type="endpoint.alert",
                        timestamp=datetime.fromisoformat(alert["create_time"]),
                        data={
                            "vendor": config.vendor,
                            "alert": alert
                        }
                    ))
                    
            elif config.vendor == EndpointVendor.SENTINEL_ONE:
                # SentinelOne API
                response = await self._make_request(
                    config,
                    "GET",
                    "/web/api/v2.1/threats",
                    params={
                        "createdAt__gt": int(start_time.timestamp() * 1000)
                    }
                )
                
                for threat in response.get("data", []):
                    logs.append(LogEvent(
                        source=f"endpoint.{config.name}",
                        event_type="endpoint.threat",
                        timestamp=datetime.fromtimestamp(
                            threat["createdAt"] / 1000,
                            UTC
                        ),
                        data={
                            "vendor": config.vendor,
                            "threat": threat
                        }
                    ))
                    
        except Exception as e:
            logger.error(f"Error collecting alerts from {config.name}: {str(e)}")
            
        return logs
        
    async def collect_events(
        self,
        config: EndpointConfig,
        start_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect security events from the endpoint solution."""
        logs = []
        start_time = start_time or (datetime.now(UTC) - timedelta(minutes=5))
        
        try:
            if config.vendor == EndpointVendor.CROWDSTRIKE:
                # CrowdStrike Falcon API - Events
                response = await self._make_request(
                    config,
                    "GET",
                    "/fwapi/queries/events/v1",
                    params={
                        "filter": f"timestamp:>'{start_time.isoformat()}Z'"
                    }
                )
                
                if "resources" in response:
                    for event_id in response["resources"]:
                        event_details = await self._make_request(
                            config,
                            "GET",
                            f"/fwapi/entities/events/v1",
                            params={"ids": event_id}
                        )
                        
                        for event in event_details.get("resources", []):
                            logs.append(LogEvent(
                                source=f"endpoint.{config.name}",
                                event_type="endpoint.event",
                                timestamp=datetime.fromtimestamp(
                                    event["timestamp"],
                                    UTC
                                ),
                                data={
                                    "vendor": config.vendor,
                                    "event": event
                                }
                            ))
                            
            elif config.vendor == EndpointVendor.CARBON_BLACK:
                # Carbon Black API - Events
                response = await self._make_request(
                    config,
                    "GET",
                    "/api/investigate/v2/orgs/{}/events/search",
                    params={
                        "criteria": {
                            "create_time": {
                                "start": start_time.isoformat()
                            }
                        }
                    }
                )
                
                for event in response.get("results", []):
                    logs.append(LogEvent(
                        source=f"endpoint.{config.name}",
                        event_type="endpoint.event",
                        timestamp=datetime.fromisoformat(event["create_time"]),
                        data={
                            "vendor": config.vendor,
                            "event": event
                        }
                    ))
                    
        except Exception as e:
            logger.error(f"Error collecting events from {config.name}: {str(e)}")
            
        return logs
        
    async def collect_logs(
        self,
        config: EndpointConfig,
        start_time: Optional[datetime] = None
    ) -> List[LogEvent]:
        """Collect all available logs from an endpoint security solution."""
        all_logs = []
        
        # Collect alerts
        logs = await self.collect_alerts(config, start_time)
        all_logs.extend(logs)
        
        # Collect events
        logs = await self.collect_events(config, start_time)
        all_logs.extend(logs)
        
        return all_logs
        
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
