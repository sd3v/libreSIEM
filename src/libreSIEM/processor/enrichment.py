"""Enrichment processors for LibreSIEM."""

from typing import Dict, Any, Optional, List, Set
import asyncio
import logging
import geoip2.database
import geoip2.errors
import aiodns
import aiohttp
import json
import hashlib
from datetime import datetime, timezone
import boto3
from botocore.exceptions import ClientError
from minio import Minio
from libreSIEM.config import Settings, get_settings

logger = logging.getLogger(__name__)

class EnrichmentProcessor:
    """Enriches log events with additional context."""
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        
        # Initialize GeoIP reader
        try:
            self.geoip_reader = geoip2.database.Reader('GeoLite2-City.mmdb')
            logger.info("GeoIP database loaded successfully")
        except FileNotFoundError:
            logger.warning("GeoIP database not found. GeoIP enrichment will be disabled.")
            self.geoip_reader = None
        
        # Initialize DNS resolver
        self.dns_resolver = aiodns.DNSResolver()
        
        # Initialize threat intel session
        self.threat_session = aiohttp.ClientSession()
        
        # Initialize deduplication cache
        self.dedup_cache: Set[str] = set()
        self.last_cache_cleanup = datetime.now(timezone.utc)
        
        # Initialize storage clients
        self._init_storage_clients()
    
    def _init_storage_clients(self):
        """Initialize cold storage clients (S3 or MinIO)."""
        if self.settings.storage.STORAGE_TYPE == 'aws':
            self.storage_client = boto3.client(
                's3',
                aws_access_key_id=self.settings.storage.AWS_ACCESS_KEY,
                aws_secret_access_key=self.settings.storage.AWS_SECRET_KEY,
                region_name=self.settings.storage.AWS_REGION
            )
        elif self.settings.storage.STORAGE_TYPE == 'minio':
            self.storage_client = Minio(
                self.settings.storage.MINIO_ENDPOINT,
                access_key=self.settings.storage.MINIO_ACCESS_KEY,
                secret_key=self.settings.storage.MINIO_SECRET_KEY,
                secure=self.settings.storage.MINIO_SECURE
            )
        else:
            logger.warning("No cold storage configured")
            self.storage_client = None
    
    async def enrich_log(self, log_event: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a log event with additional context."""
        enriched = log_event.copy()
        
        # Skip if this is a duplicate event
        if self._is_duplicate(enriched):
            return None
        
        # Add enrichment data
        enriched['enriched'] = {
            'processing_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Run enrichment tasks concurrently
        tasks = [
            self._enrich_geoip(enriched),
            self._enrich_dns(enriched),
            self._enrich_threat_intel(enriched)
        ]
        await asyncio.gather(*tasks)
        
        # Archive to cold storage if needed
        await self._archive_to_cold_storage(enriched)
        
        return enriched
    
    def _is_duplicate(self, log_event: Dict[str, Any]) -> bool:
        """Check if this is a duplicate event using fuzzy matching."""
        # Clean up cache if needed
        if (datetime.now(timezone.utc) - self.last_cache_cleanup).total_seconds() > 3600:
            self.dedup_cache.clear()
            self.last_cache_cleanup = datetime.now(timezone.utc)
        
        # Create a fingerprint of the event
        relevant_fields = {
            'source': log_event.get('source'),
            'event_type': log_event.get('event_type'),
            'data': {k: v for k, v in log_event.get('data', {}).items() 
                    if k not in ['timestamp', 'id', 'sequence_num']}
        }
        fingerprint = hashlib.sha256(
            json.dumps(relevant_fields, sort_keys=True).encode()
        ).hexdigest()
        
        # Check if we've seen this fingerprint recently
        if fingerprint in self.dedup_cache:
            return True
        
        self.dedup_cache.add(fingerprint)
        return False
    
    async def _enrich_geoip(self, log_event: Dict[str, Any]) -> None:
        """Enrich with GeoIP data."""
        if not self.geoip_reader:
            return
        
        # Extract IP addresses from the event
        ip_addresses = self._extract_ip_addresses(log_event)
        ip_info = {}
        
        for ip in ip_addresses:
            try:
                response = self.geoip_reader.city(ip)
                ip_info[ip] = {
                    'country': response.country.iso_code,
                    'city': response.city.name,
                    'location': {
                        'lat': response.location.latitude,
                        'lon': response.location.longitude
                    },
                    'asn': response.traits.autonomous_system_number
                }
            except (geoip2.errors.AddressNotFoundError, ValueError):
                continue
        
        if ip_info:
            log_event['enriched']['ip_info'] = ip_info
    
    async def _enrich_dns(self, log_event: Dict[str, Any]) -> None:
        """Enrich with DNS resolution data."""
        # Extract hostnames from the event
        hostnames = self._extract_hostnames(log_event)
        dns_info = {}
        
        for hostname in hostnames:
            try:
                response = await self.dns_resolver.query(hostname, 'A')
                dns_info[hostname] = {
                    'ip_addresses': [str(rdata.host) for rdata in response],
                    'resolution_time': datetime.now(timezone.utc).isoformat()
                }
            except Exception as e:
                logger.debug(f"DNS resolution failed for {hostname}: {e}")
                continue
        
        if dns_info:
            log_event['enriched']['dns_info'] = dns_info
    
    async def _enrich_threat_intel(self, log_event: Dict[str, Any]) -> None:
        """Enrich with threat intelligence data."""
        # Extract indicators from the event
        indicators = {
            'ips': self._extract_ip_addresses(log_event),
            'domains': self._extract_hostnames(log_event),
            'hashes': self._extract_hashes(log_event)
        }
        
        threat_info = {}
        
        for indicator_type, values in indicators.items():
            for value in values:
                try:
                    # Query multiple threat intel sources
                    sources = [
                        f"https://api.abuseipdb.com/api/v2/check?ipAddress={value}",
                        f"https://api.virustotal.com/api/v3/ip_addresses/{value}"
                    ]
                    
                    for source in sources:
                        headers = {'API-Key': self.settings.threat_intel.API_KEY}
                        async with self.threat_session.get(source, headers=headers) as response:
                            if response.status == 200:
                                data = await response.json()
                                threat_info[value] = self._parse_threat_intel_response(data)
                except Exception as e:
                    logger.debug(f"Threat intel lookup failed for {value}: {e}")
                    continue
        
        if threat_info:
            log_event['enriched']['threat_intel'] = threat_info
    
    async def _archive_to_cold_storage(self, log_event: Dict[str, Any]) -> None:
        """Archive log to cold storage if it meets archival criteria."""
        if not self.storage_client:
            return
        
        # Check if this event should be archived
        if not self._should_archive(log_event):
            return
        
        # Prepare the archive path
        timestamp = datetime.fromisoformat(log_event['timestamp'])
        archive_path = f"{timestamp.strftime('%Y/%m/%d')}/{log_event['source']}/{timestamp.strftime('%H%M%S')}-{log_event.get('id', 'unknown')}.json"
        
        try:
            if isinstance(self.storage_client, boto3.client):
                self.storage_client.put_object(
                    Bucket=self.settings.storage.ARCHIVE_BUCKET,
                    Key=archive_path,
                    Body=json.dumps(log_event)
                )
            else:  # MinIO client
                self.storage_client.put_object(
                    bucket_name=self.settings.storage.ARCHIVE_BUCKET,
                    object_name=archive_path,
                    data=json.dumps(log_event).encode(),
                    length=-1,
                    content_type='application/json'
                )
            logger.debug(f"Archived log to {archive_path}")
        except Exception as e:
            logger.error(f"Failed to archive log: {e}")
    
    def _should_archive(self, log_event: Dict[str, Any]) -> bool:
        """Determine if a log event should be archived to cold storage."""
        # Archive based on severity or event type
        severity = log_event.get('data', {}).get('severity', '').lower()
        event_type = log_event.get('event_type', '').lower()
        
        return any([
            severity in ['critical', 'high'],
            'attack' in event_type,
            'threat' in event_type,
            'security' in event_type
        ])
    
    @staticmethod
    def _extract_ip_addresses(log_event: Dict[str, Any]) -> Set[str]:
        """Extract IP addresses from a log event."""
        # Implementation would use regex to find IP addresses in the event
        # For now, return a simple example
        return {'192.168.1.1', '10.0.0.1'}
    
    @staticmethod
    def _extract_hostnames(log_event: Dict[str, Any]) -> Set[str]:
        """Extract hostnames from a log event."""
        # Implementation would use regex to find hostnames in the event
        # For now, return a simple example
        return {'example.com', 'test.local'}
    
    @staticmethod
    def _extract_hashes(log_event: Dict[str, Any]) -> Set[str]:
        """Extract file hashes from a log event."""
        # Implementation would look for common hash patterns (MD5, SHA1, SHA256)
        # For now, return a simple example
        return {'a1b2c3d4e5f6', '123456789abcdef'}
    
    def _parse_threat_intel_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse threat intelligence API response."""
        return {
            'score': data.get('data', {}).get('abuseConfidenceScore', 0),
            'categories': data.get('data', {}).get('categories', []),
            'last_seen': data.get('data', {}).get('lastReportedAt')
        }
    
    async def close(self):
        """Close all connections."""
        if self.geoip_reader:
            self.geoip_reader.close()
        await self.threat_session.close()
