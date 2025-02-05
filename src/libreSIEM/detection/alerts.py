"""Alert management and notification system for LibreSIEM."""

import os
import json
import logging
import smtplib
import aiohttp
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import asdict
from jinja2 import Environment, FileSystemLoader
from libreSIEM.config import Settings, get_settings
from libreSIEM.detection.engine import Alert

logger = logging.getLogger(__name__)

class AlertManager:
    """Manages alerts and notifications."""
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        
        # Initialize template engine
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Initialize notification channels
        self.notification_channels = {
            'email': EmailNotifier(self.settings),
            'webhook': WebhookNotifier(self.settings),
            'slack': SlackNotifier(self.settings),
            'discord': DiscordNotifier(self.settings),
            'telegram': TelegramNotifier(self.settings)
        }
        
        logger.info("Alert manager initialized")
    
    async def process_alerts(self, alerts: List[Alert]) -> None:
        """Process and distribute alerts to configured channels."""
        for alert in alerts:
            try:
                # Convert alert to dictionary
                alert_dict = asdict(alert)
                
                # Add metadata
                alert_dict['processed_at'] = datetime.now(timezone.utc).isoformat()
                
                # Get notification channels based on severity
                channels = self._get_channels_for_severity(alert.severity)
                
                # Send notifications
                await asyncio.gather(*[
                    self._send_notification(channel, alert_dict)
                    for channel in channels
                ])
                
                logger.info(f"Alert {alert.id} processed and notifications sent")
                
            except Exception as e:
                logger.error(f"Error processing alert {alert.id}: {e}")
    
    def _get_channels_for_severity(self, severity: str) -> List[str]:
        """Get notification channels based on alert severity."""
        severity_channels = {
            'critical': ['email', 'slack', 'telegram'],
            'high': ['email', 'slack'],
            'medium': ['slack'],
            'low': ['slack']
        }
        return severity_channels.get(severity.lower(), ['slack'])
    
    async def _send_notification(self, channel: str, alert: Dict[str, Any]) -> None:
        """Send notification through specified channel."""
        try:
            notifier = self.notification_channels.get(channel)
            if notifier:
                await notifier.send(alert)
            else:
                logger.warning(f"Notification channel {channel} not configured")
        except Exception as e:
            logger.error(f"Error sending {channel} notification: {e}")

class BaseNotifier:
    """Base class for notification channels."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    async def send(self, alert: Dict[str, Any]) -> None:
        """Send notification."""
        raise NotImplementedError

class EmailNotifier(BaseNotifier):
    """Email notification channel."""
    
    async def send(self, alert: Dict[str, Any]) -> None:
        """Send email notification."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.settings.notifications.EMAIL_FROM
            msg['To'] = self.settings.notifications.EMAIL_TO
            msg['Subject'] = f"LibreSIEM Alert: {alert['title']} ({alert['severity'].upper()})"
            
            # Create HTML body
            template = self.settings.notifications.get_template('email_alert.html')
            html = template.render(alert=alert)
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            with smtplib.SMTP(self.settings.notifications.SMTP_HOST, 
                            self.settings.notifications.SMTP_PORT) as server:
                if self.settings.notifications.SMTP_TLS:
                    server.starttls()
                if self.settings.notifications.SMTP_USERNAME:
                    server.login(
                        self.settings.notifications.SMTP_USERNAME,
                        self.settings.notifications.SMTP_PASSWORD
                    )
                server.send_message(msg)
            
            logger.info(f"Email notification sent for alert {alert['id']}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")

class WebhookNotifier(BaseNotifier):
    """Generic webhook notification channel."""
    
    async def send(self, alert: Dict[str, Any]) -> None:
        """Send webhook notification."""
        try:
            webhook_url = self.settings.notifications.WEBHOOK_URL
            if not webhook_url:
                return
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=alert) as response:
                    if response.status != 200:
                        logger.error(f"Webhook notification failed with status {response.status}")
                    else:
                        logger.info(f"Webhook notification sent for alert {alert['id']}")
        
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")

class SlackNotifier(BaseNotifier):
    """Slack notification channel."""
    
    async def send(self, alert: Dict[str, Any]) -> None:
        """Send Slack notification."""
        try:
            webhook_url = self.settings.notifications.SLACK_WEBHOOK_URL
            if not webhook_url:
                return
            
            # Create Slack message
            message = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"🚨 {alert['title']}"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Severity:* {alert['severity'].upper()}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Rule:* {alert['rule_name']}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": alert['description']
                        }
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=message) as response:
                    if response.status != 200:
                        logger.error(f"Slack notification failed with status {response.status}")
                    else:
                        logger.info(f"Slack notification sent for alert {alert['id']}")
        
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")

class DiscordNotifier(BaseNotifier):
    """Discord notification channel."""
    
    async def send(self, alert: Dict[str, Any]) -> None:
        """Send Discord notification."""
        try:
            webhook_url = self.settings.notifications.DISCORD_WEBHOOK_URL
            if not webhook_url:
                return
            
            # Create Discord embed
            embed = {
                "title": alert['title'],
                "description": alert['description'],
                "color": self._get_color_for_severity(alert['severity']),
                "fields": [
                    {
                        "name": "Severity",
                        "value": alert['severity'].upper(),
                        "inline": True
                    },
                    {
                        "name": "Rule",
                        "value": alert['rule_name'],
                        "inline": True
                    }
                ],
                "timestamp": alert['timestamp']
            }
            
            message = {
                "embeds": [embed]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=message) as response:
                    if response.status != 204:
                        logger.error(f"Discord notification failed with status {response.status}")
                    else:
                        logger.info(f"Discord notification sent for alert {alert['id']}")
        
        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")
    
    def _get_color_for_severity(self, severity: str) -> int:
        """Get Discord color code for severity."""
        colors = {
            'critical': 0xFF0000,  # Red
            'high': 0xFFA500,     # Orange
            'medium': 0xFFFF00,   # Yellow
            'low': 0x00FF00       # Green
        }
        return colors.get(severity.lower(), 0x808080)  # Default gray

class TelegramNotifier(BaseNotifier):
    """Telegram notification channel."""
    
    async def send(self, alert: Dict[str, Any]) -> None:
        """Send Telegram notification."""
        try:
            bot_token = self.settings.notifications.TELEGRAM_BOT_TOKEN
            chat_id = self.settings.notifications.TELEGRAM_CHAT_ID
            if not bot_token or not chat_id:
                return
            
            # Create message text
            message = (
                f"🚨 *{alert['title']}*\n\n"
                f"*Severity:* {alert['severity'].upper()}\n"
                f"*Rule:* {alert['rule_name']}\n\n"
                f"{alert['description']}"
            )
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            params = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params) as response:
                    if response.status != 200:
                        logger.error(f"Telegram notification failed with status {response.status}")
                    else:
                        logger.info(f"Telegram notification sent for alert {alert['id']}")
        
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
