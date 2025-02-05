"""Webhook management and processing for LibreSIEM."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, HttpUrl
from datetime import datetime, UTC
import httpx
import hashlib
import hmac
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class WebhookEventType(str, Enum):
    """Types of events that can trigger webhooks."""
    LOG_RECEIVED = "log.received"
    ALERT_CREATED = "alert.created"
    THREAT_DETECTED = "threat.detected"
    SYSTEM_STATUS = "system.status"

class WebhookConfig(BaseModel):
    """Configuration for a webhook endpoint."""
    url: HttpUrl
    secret: str
    description: Optional[str] = None
    enabled: bool = True
    event_types: List[WebhookEventType]
    headers: Optional[Dict[str, str]] = None
    retry_count: int = 3
    timeout_seconds: int = 5

class WebhookDeliveryStatus(str, Enum):
    """Status of webhook delivery attempts."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"

class WebhookEvent(BaseModel):
    """Event to be sent via webhook."""
    id: str
    type: WebhookEventType
    timestamp: datetime
    data: Dict[str, Any]

class WebhookManager:
    """Manages webhook configurations and deliveries."""
    
    def __init__(self):
        self.webhooks: Dict[str, WebhookConfig] = {}
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def register_webhook(self, webhook: WebhookConfig) -> str:
        """Register a new webhook configuration."""
        webhook_id = hashlib.sha256(webhook.url.encode()).hexdigest()[:16]
        self.webhooks[webhook_id] = webhook
        logger.info(f"Registered webhook {webhook_id} for URL {webhook.url}")
        return webhook_id
        
    def generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload."""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
    async def deliver_webhook(self, webhook: WebhookConfig, event: WebhookEvent) -> bool:
        """Deliver a webhook event to its configured endpoint."""
        payload = event.model_dump_json()
        signature = self.generate_signature(payload, webhook.secret)
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "LibreSIEM-Webhook/1.0",
            "X-LibreSIEM-Event": event.type,
            "X-LibreSIEM-Signature": signature,
            "X-LibreSIEM-Delivery": event.id,
            **(webhook.headers or {})
        }
        
        for attempt in range(webhook.retry_count):
            try:
                async with httpx.AsyncClient(timeout=webhook.timeout_seconds) as client:
                    response = await client.post(
                        str(webhook.url),
                        headers=headers,
                        json=json.loads(payload)
                    )
                    
                    if response.status_code in (200, 201, 202):
                        logger.info(f"Successfully delivered webhook {event.id} to {webhook.url}")
                        return True
                        
                    logger.warning(
                        f"Webhook delivery failed (attempt {attempt + 1}/{webhook.retry_count}): "
                        f"Status {response.status_code}"
                    )
                    
            except Exception as e:
                logger.error(
                    f"Webhook delivery error (attempt {attempt + 1}/{webhook.retry_count}): {str(e)}"
                )
                
            if attempt < webhook.retry_count - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
        return False
        
    async def broadcast_event(self, event: WebhookEvent) -> Dict[str, bool]:
        """Broadcast an event to all registered webhooks that are subscribed to its type."""
        results = {}
        
        for webhook_id, webhook in self.webhooks.items():
            if not webhook.enabled or event.type not in webhook.event_types:
                continue
                
            success = await self.deliver_webhook(webhook, event)
            results[webhook_id] = success
            
        return results
        
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Global webhook manager instance
webhook_manager = WebhookManager()
